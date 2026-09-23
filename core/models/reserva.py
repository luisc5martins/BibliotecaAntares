from django.db import models
from .livro import Livro
from .user import User

class Reserva(models.Model):
    class StatusReserva(models.IntegerChoices):
        RESERVADO = 1, 'Reservado'
        RETIRADO = 2, 'Retirado'
        DEVOLVIDO = 3, 'Devolvido'

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reservas'
    )
    status = models.IntegerField(
        choices=StatusReserva.choices,
        default=StatusReserva.RESERVADO
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for item in self.itens.all():
            if self.status in [
                self.StatusReserva.RESERVADO,
                self.StatusReserva.RETIRADO
            ]:
                item.livro.status = Livro.Status.RESERVADO

            elif self.status == self.StatusReserva.DEVOLVIDO:
                item.livro.status = Livro.Status.DISPONIVEL

            item.livro.save(update_fields=['status'])

class ItensReserva(models.Model):
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    livro = models.ForeignKey(
        Livro,
        on_delete=models.PROTECT,
        related_name='itens_reserva'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.reserva.status in [
            Reserva.StatusReserva.RESERVADO,
            Reserva.StatusReserva.RETIRADO
        ]:
            self.livro.status = Livro.Status.RESERVADO

        elif self.reserva.status == Reserva.StatusReserva.DEVOLVIDO:
            self.livro.status = Livro.Status.DISPONIVEL

        self.livro.save(update_fields=['status'])