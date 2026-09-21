from django.db import models
from .categoria import Categoria
from .editora import Editora
from .autor import Autor

class Livro(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = 'disponivel', 'Disponível'
        RESERVADO = 'reservado', 'Reservado'

    titulo = models.CharField(max_length=255)
    isbn = models.CharField(max_length=32, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISPONIVEL)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='livros', null=True, blank=True)
    editora = models.ForeignKey(Editora, on_delete=models.PROTECT, related_name='livros', null=True, blank=True)
    autores = models.ManyToManyField(Autor, related_name='livros', blank=True)

    def __str__(self):
        return f'({self.id}) {self.titulo} ({self.status})'