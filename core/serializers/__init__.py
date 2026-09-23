from rest_framework.serializers import ModelSerializer
from .user import UserRegistrationSerializer, UserSerializer
from .categoria import CategoriaSerializer
from .editora import EditoraSerializer
from .autor import AutorSerializer
from .livro import LivroListSerializer, LivroRetrieveSerializer, LivroSerializer
from .reserva import ReservaSerializer