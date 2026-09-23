from rest_framework.viewsets import ModelViewSet

from core.models import Reserva
from core.serializers import ReservaSerializer


class ReservaViewSet(ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer