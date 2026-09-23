from rest_framework.viewsets import ModelViewSet
from core.models import Reserva
from core.serializers.reserva import (
    ReservaCreateUpdateSerializer,
    ReservaListSerializer,
    ReservaSerializer,
)

class ReservaViewSet(ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser:
            return Reserva.objects.all()
        if usuario.groups.filter(name='administradores'):
            return Reserva.objects.all()
        return Reserva.objects.filter(usuario=usuario)