from django.urls import reverse_lazy
from django.views.generic import ListView

from ..forms import RolForm
from ..models import Rol
from .base import CrearView, EditarView, EliminarView


class RolLista(ListView):
    model = Rol
    template_name = 'reclamos_app/roles/lista.html'
    context_object_name = 'roles'
    paginate_by = 20


class RolCrear(CrearView):
    model = Rol
    form_class = RolForm
    titulo = 'Nuevo rol'
    success_url = reverse_lazy('reclamos_app:rol_lista')


class RolEditar(EditarView):
    model = Rol
    form_class = RolForm
    titulo = 'Editar rol'
    success_url = reverse_lazy('reclamos_app:rol_lista')


class RolEliminar(EliminarView):
    model = Rol
    success_url = reverse_lazy('reclamos_app:rol_lista')
