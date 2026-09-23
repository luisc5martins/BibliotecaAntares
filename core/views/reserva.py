from rest_framework.viewsets import ModelViewSet
from core.models import Reserva
from core.serializers import ReservaSerializer, ReservaCreateUpdateSerializer

class ReservaViewSet(ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ReservaCreateUpdateSerializer
        return ReservaSerializer