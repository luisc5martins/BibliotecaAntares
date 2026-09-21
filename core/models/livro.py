from django.db import models

class Livro(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = 'disponivel', 'Disponível'
        RESERVADO = 'reservado', 'Reservado'

    titulo = models.CharField(max_length=255)
    isbn = models.CharField(max_length=32, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISPONIVEL)

    def __str__(self):
        return f'({self.id}) {self.titulo} ({self.status})'