from django.db import models
from .livro import Livro
from .user import User

class Reserva(models.Model):
    class StatusReserva(models.IntegerChoices):
        RESERVADO = 1, 'Reservado'
        RETIRADO = 2, 'Retirado'
        DEVOLVIDO = 3, 'Devolvido'

    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservas')
    status = models.IntegerField(choices=StatusReserva.choices,  default=StatusReserva.RESERVADO)

class ItensReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='itens')
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name='+')