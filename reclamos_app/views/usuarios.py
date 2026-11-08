from django.urls import reverse_lazy

from ..forms import UsuarioForm
from ..models import Usuario
from .base import CrearView, EditarView, EliminarView, ListaView


class UsuarioLista(ListaView):
    model = Usuario
    template_name = 'reclamos_app/usuarios/lista.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return super().get_queryset().select_related('barrio', 'rol')


class UsuarioCrear(CrearView):
    model = Usuario
    form_class = UsuarioForm
    titulo = 'Nuevo usuario'
    icono = 'bi-person-plus'
    success_url = reverse_lazy('reclamos_app:usuario_lista')


class UsuarioEditar(EditarView):
    model = Usuario
    form_class = UsuarioForm
    titulo = 'Editar usuario'
    icono = 'bi-person-gear'
    success_url = reverse_lazy('reclamos_app:usuario_lista')


class UsuarioEliminar(EliminarView):
    model = Usuario
    success_url = reverse_lazy('reclamos_app:usuario_lista')
