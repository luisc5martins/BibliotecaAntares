from rest_framework.serializers import CharField, ModelSerializer, SerializerMethodField
from core.models import Reserva, ItensReserva
from django.db import transaction

from core.views import reserva

class ItensReservaSerializer(ModelSerializer):
    class Meta:
        model = ItensReserva
        fields = ('livro')
        depth = 1

class ReservaSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    itens = ItensReservaSerializer(many=True, read_only=True)
    class Meta:
        model = Reserva
        fields = '__all__'

class ItensReservaCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensReserva
        fields = ('livro')

class ReservaCreateUpdateSerializer(ModelSerializer):
    itens = ItensReservaCreateUpdateSerializer(many=True)

    class Meta:
        model = Reserva
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens = validated_data.pop('itens')
        reserva = Reserva.objects.create(**validated_data)
        for item in itens:
            ItensReserva.objects.create(reserva=reserva, **item)
        reserva.save()
        return reserva