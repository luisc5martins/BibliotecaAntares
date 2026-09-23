from rest_framework.serializers import CharField, ModelSerializer
from core.models import Reserva, ItensReserva

class ItensReservaSerializer(ModelSerializer):
    class Meta:
        model = ItensReserva
        fields = ('livro', 'quantidade')
        depth = 1

class ReservaSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    itens = ItensReservaSerializer(many=True, read_only=True)
    class Meta:
        model = Reserva
        fields = '__all__'