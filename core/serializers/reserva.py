from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    CurrentUserDefault,
    HiddenField,
)
from core.models import Reserva, ItensReserva
from django.db import transaction

from core.views import reserva


class ItensReservaSerializer(ModelSerializer):
    class Meta:
        model = ItensReserva
        fields = ('livro',)


class ReservaSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    itens = ItensReservaSerializer(many=True, read_only=True)

    class Meta:
        model = Reserva
        fields = (
            'id',
            'usuario',
            'status',
            'data_criacao',
            'data_atualizacao',
            'itens',
        )


class ItensReservaCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensReserva
        fields = ('livro',)

class ReservaCreateUpdateSerializer(ModelSerializer):
    usuario = HiddenField(default=CurrentUserDefault())
    itens = ItensReservaCreateUpdateSerializer(many=True)

    class Meta:
        model = Reserva
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens = validated_data.pop('itens', [])

        reserva = Reserva.objects.create(**validated_data)

        for item in itens:
            ItensReserva.objects.create(
                reserva=reserva,
                **item
            )

        return reserva

    @transaction.atomic
    def update(self, reserva, validated_data):
        itens = validated_data.pop('itens', [])

        if itens:
            reserva.itens.all().delete()

            for item in itens:
                ItensReserva.objects.create(
                    reserva=reserva,
                    **item
                )

        return super().update(reserva, validated_data)


class ItensReservaListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensReserva
        fields = ('livro',)


class ReservaListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensReservaListSerializer(many=True, read_only=True)

    class Meta:
        model = Reserva
        fields = ('id', 'usuario', 'itens')