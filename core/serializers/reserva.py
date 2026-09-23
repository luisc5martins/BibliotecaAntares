from rest_framework.serializers import ModelSerializer

from core.models import Reserva

class ReservaSerializer(ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'