from rest_framework.viewsets import ModelViewSet
from core.models import Reserva
from core.serializers.reserva import (
    ReservaSerializer,
    ReservaCreateUpdateSerializer,
    ReservaListSerializer,
)
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated


class ReservaViewSet(ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    filterset_fields = [
        "usuario__email",
        "status",
        "data_criacao",
    ]

    search_fields = [
        "usuario__email",
    ]

    ordering_fields = [
        "usuario__email",
        "status",
        "data_criacao",
    ]

    ordering = ["-data_criacao"]

    http_method_names = [
        "get",
        "post",
        "put",
        "delete",
    ]

    def get_queryset(self):
        usuario = self.request.user

        # Superusuário pode visualizar todas as reservas
        if usuario.is_superuser:
            return Reserva.objects.all()

        # Administradores podem visualizar todas as reservas
        if usuario.groups.filter(name="Administradores").exists():
            return Reserva.objects.all()

        # Usuário comum só visualiza suas próprias reservas
        return Reserva.objects.filter(usuario=usuario)

    def is_admin(self):
        usuario = self.request.user

        return (
            usuario.is_superuser
            or usuario.groups.filter(name="Administradores").exists()
        )

    def update(self, request, *args, **kwargs):
        if not self.is_admin():
            return Response(
                {
                    "detail": "Você não tem permissão para alterar reservas."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.is_admin():
            return Response(
                {
                    "detail": "Você não tem permissão para excluir reservas."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        request=None,
        responses={
            200: None,
            403: None,
        },
        description="Retorna a quantidade de reservas criadas no mês atual.",
        summary="Relatório de reservas do mês",
    )
    @action(detail=False, methods=["get"])
    def relatorio_reservas_mes(self, request):
        if not self.is_admin():
            return Response(
                {
                    "detail": "Você não tem permissão para acessar este relatório."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        agora = timezone.now()

        inicio_mes = agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        reservas = Reserva.objects.filter(
            data_criacao__gte=inicio_mes
        )

        quantidade_reservas = reservas.count()

        return Response(
            {
                "status": "Relatório de reservas deste mês",
                "quantidade_reservas": quantidade_reservas,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={
            200: None,
            400: None,
            403: None,
        },
        description="Finaliza a reserva e marca os livros como reservados.",
        summary="Finalizar reserva",
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def finalizar(self, request, pk=None):
        if not self.is_admin():
            return Response(
                {
                    "detail": "Você não tem permissão para finalizar reservas."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        reserva = self.get_object()

        if reserva.status == Reserva.StatusReserva.RESERVADO:
            return Response(
                {
                    "status": "Reserva já finalizada"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        for item in reserva.itens.all():
            livro = item.livro

            if livro.status != livro.Status.DISPONIVEL:
                return Response(
                    {
                        "status": "Livro não disponível",
                        "livro": livro.titulo,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            livro.status = livro.Status.RESERVADO

            livro.save(
                update_fields=["status"]
            )

        reserva.status = Reserva.StatusReserva.RESERVADO
        reserva.save()

        return Response(
            {
                "status": "Reserva finalizada"
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={
            200: None,
            400: None,
            403: None,
        },
        description="Devolve os livros da reserva e aumenta a quantidade disponível.",
        summary="Devolver reserva",
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def devolver(self, request, pk=None):
        if not self.is_admin():
            return Response(
                {
                    "detail": "Você não tem permissão para devolver reservas."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        reserva = self.get_object()

        if reserva.status == Reserva.StatusReserva.DEVOLVIDO:
            return Response(
                {
                    "status": "A reserva já foi devolvida."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reserva.status not in [
            Reserva.StatusReserva.RESERVADO,
            Reserva.StatusReserva.RETIRADO,
        ]:
            return Response(
                {
                    "status": "A reserva não pode ser devolvida."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        for item in reserva.itens.all():
            livro = item.livro

            livro.quantidade += 1
            livro.status = livro.Status.DISPONIVEL

            livro.save(
                update_fields=[
                    "quantidade",
                    "status",
                ]
            )

        reserva.status = Reserva.StatusReserva.DEVOLVIDO
        reserva.save()

        return Response(
            {
                "status": "Reserva devolvida com sucesso"
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={
            200: None,
            400: None,
            403: None,
            404: None,
        },
        description="Cancela uma reserva do próprio usuário.",
        summary="Cancelar reserva",
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def cancelar(self, request, pk=None):

        try:
            reserva = Reserva.objects.get(pk=pk)
        except Reserva.DoesNotExist:
            return Response(
                {
                    "detail": "Reserva não encontrada."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Administrador pode cancelar qualquer reserva
        if self.is_admin():
            pass

        # Usuário comum só pode cancelar a própria reserva
        elif reserva.usuario_id != request.user.id:
            return Response(
                {
                    "detail": "Você não tem permissão para cancelar esta reserva."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Só permite cancelar reservas reservadas
        if reserva.status != Reserva.StatusReserva.RESERVADO:
            return Response(
                {
                    "detail": "Apenas reservas reservadas podem ser canceladas."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reserva.status = Reserva.StatusReserva.CANCELADO
        reserva.save()

        return Response(
            {
                "status": "Reserva cancelada com sucesso."
            },
            status=status.HTTP_200_OK,
        )

    def get_serializer_class(self):
        if self.action in [
            "create",
            "update",
        ]:
            return ReservaCreateUpdateSerializer

        if self.action == "list":
            return ReservaListSerializer

        return ReservaSerializer