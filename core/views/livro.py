from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema
from core.models import Livro, Reserva
from core.serializers import LivroSerializer
from core.serializers.livro import LivroMaisReservadoSerializer, LivroListSerializer, LivroRetrieveSerializer

class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria__descricao', 'editora__nome']

    def get_serializer_class(self):
        if self.action == 'list':
            return LivroListSerializer
        elif self.action == 'retrieve':
            return LivroRetrieveSerializer
        return LivroSerializer

    @extend_schema(
    summary="Lista os livros mais reservados",
    description="Retorna os livros que foram reservados mais de 10 vezes.",
    responses={
        200: LivroMaisReservadoSerializer(many=True)
    },
    )
    @action(detail=False, methods=['get'])
    def mais_reservados(self, request):
        livros = Livro.objects.annotate(
            total_reservas=Count(
                'itens_reserva__reserva',
                filter=Q(
                    itens_reserva__reserva__status__in=[
                        Reserva.StatusReserva.RESERVADO,
                        Reserva.StatusReserva.RETIRADO,
                        Reserva.StatusReserva.DEVOLVIDO,
                    ]
                ),
                distinct=True
            )
        ).filter(
            total_reservas__gt=10
        ).order_by('-total_reservas')

        serializer = LivroMaisReservadoSerializer(
            livros,
            many=True
        )

        if not serializer.data:
            return Response(
                {
                    "detail": "Nenhum livro possui mais de 10 reservas."
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )