from django.db import models, transaction

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

        status_anterior = None

        if self.pk:
            status_anterior = (
                Reserva.objects
                .filter(pk=self.pk)
                .values_list('status', flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        # Só devolve o livro quando a reserva
        # MUDA para DEVOLVIDO.
        if (
            self.status == self.StatusReserva.DEVOLVIDO
            and status_anterior != self.StatusReserva.DEVOLVIDO
        ):
            for item in self.itens.all():

                livro = item.livro

                livro.quantidade += 1
                livro.status = Livro.Status.DISPONIVEL

                livro.save(
                    update_fields=[
                        'quantidade',
                        'status'
                    ]
                )

        # RESERVADO ou RETIRADO não altera quantidade.
        elif self.status in [
            self.StatusReserva.RESERVADO,
            self.StatusReserva.RETIRADO
        ]:
            for item in self.itens.all():

                livro = item.livro

                if livro.quantidade == 0:
                    livro.status = Livro.Status.RESERVADO
                else:
                    livro.status = Livro.Status.DISPONIVEL

                livro.save(
                    update_fields=['status']
                )


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

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.reserva.status == Reserva.StatusReserva.DEVOLVIDO:
                raise ValueError(
                    'Não é possível adicionar itens a uma reserva devolvida.'
                )

            livro = Livro.objects.select_for_update().get(pk=self.livro_id)

            if livro.quantidade <= 0:
                raise ValueError(
                    f'O livro "{livro.titulo}" não possui '
                    'quantidade disponível.'
                )

            livro.quantidade -= 1
            livro.save(update_fields=['quantidade'])

        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.reserva.status != Reserva.StatusReserva.DEVOLVIDO:
            livro = Livro.objects.select_for_update().get(pk=self.livro_id)
            livro.quantidade += 1
            livro.save(update_fields=['quantidade'])

        return super().delete(*args, **kwargs)