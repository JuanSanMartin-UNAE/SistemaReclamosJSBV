from django.urls import reverse_lazy
from django.views.generic import ListView

from ..forms import UsuarioForm
from ..models import Usuario
from .base import CrearView, EditarView, EliminarView


class UsuarioLista(ListView):
    model = Usuario
    template_name = 'reclamos_app/usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('barrio', 'rol')


class UsuarioCrear(CrearView):
    model = Usuario
    form_class = UsuarioForm
    titulo = 'Nuevo usuario'
    success_url = reverse_lazy('reclamos_app:usuario_lista')


class UsuarioEditar(EditarView):
    model = Usuario
    form_class = UsuarioForm
    titulo = 'Editar usuario'
    success_url = reverse_lazy('reclamos_app:usuario_lista')


class UsuarioEliminar(EliminarView):
    model = Usuario
    success_url = reverse_lazy('reclamos_app:usuario_lista')
