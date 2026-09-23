from rest_framework.viewsets import ModelViewSet
from core.models import Reserva
from core.serializers.reserva import ReservaSerializer
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema

class ReservaViewSet(ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        usuario = self.request.user

        if usuario.is_superuser:
            return Reserva.objects.all()

        if usuario.groups.filter(name='administradores').exists():
            return Reserva.objects.all()

        return Reserva.objects.filter(usuario=usuario)

    @action(detail=False, methods=['get'])
    def relatorio_reservas_mes(self, request):
        agora = timezone.now()

        inicio_mes = agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        reservas = Reserva.objects.filter(
            data_criacao__gte=inicio_mes
        )

        quantidade_reservas = reservas.count()

        return Response(
            {
                'status': 'Relatório de reservas deste mês',
                'quantidade_reservas': quantidade_reservas,
            },
            status=status.HTTP_200_OK,
        )
    @extend_schema(
        request=None,
        responses={200: None, 400: None},
        description="Finaliza a reserva e marca os livros como reservados.",
        summary="Finalizar reserva",
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def finalizar(self, request, pk=None):
        reserva = self.get_object()

        if reserva.status == Reserva.StatusReserva.RESERVADO:
            return Response(
                {
                    'status': 'Reserva já finalizada'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in reserva.itens.all():
            livro = item.livro

            if livro.status != livro.Status.DISPONIVEL:
                return Response(
                    {
                        'status': 'Livro não disponível',
                        'livro': livro.titulo,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            livro.status = livro.Status.RESERVADO
            livro.save(update_fields=['status'])

        reserva.status = Reserva.StatusReserva.RESERVADO
        reserva.save()

        return Response(
            {
                'status': 'Reserva finalizada'
            },
            status=status.HTTP_200_OK
        )