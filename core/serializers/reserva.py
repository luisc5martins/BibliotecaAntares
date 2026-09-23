from rest_framework.serializers import CharField, ModelSerializer
from core.models import Reserva, ItensReserva
from django.db import transaction

class ItensReservaSerializer(ModelSerializer):
    class Meta:
        model = ItensReserva
        fields = ('livro',)
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
        fields = ('livro',)

class ReservaCreateUpdateSerializer(ModelSerializer):
    itens = ItensReservaCreateUpdateSerializer(many=True)

    class Meta:
        model = Reserva
        fields = ('id', 'usuario', 'itens')

class ItensReservaListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensReserva
        fields = ('livro',)
        depth = 1

class ReservaListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensReservaListSerializer(many=True, read_only=True)

    class Meta:
        model = Reserva
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def update(self, reserva, validated_data):
        itens = validated_data.pop('itens', None)
        if itens is not None:
            reserva.itens.all().delete()
            for item in itens:
                ItensReserva.objects.create(reserva=reserva, **item)
        return super().update(reserva, validated_data)