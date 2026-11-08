from django.urls import reverse_lazy

from ..forms import PrioridadForm
from ..models import Prioridad
from .base import CrearView, EditarView, EliminarView, ListaView


class PrioridadLista(ListaView):
    model = Prioridad
    template_name = 'reclamos_app/prioridades/lista.html'
    context_object_name = 'prioridades'


class PrioridadCrear(CrearView):
    model = Prioridad
    form_class = PrioridadForm
    titulo = 'Nueva prioridad'
    icono = 'bi-exclamation-triangle'
    success_url = reverse_lazy('reclamos_app:prioridad_lista')


class PrioridadEditar(EditarView):
    model = Prioridad
    form_class = PrioridadForm
    titulo = 'Editar prioridad'
    icono = 'bi-exclamation-triangle'
    success_url = reverse_lazy('reclamos_app:prioridad_lista')


class PrioridadEliminar(EliminarView):
    model = Prioridad
    success_url = reverse_lazy('reclamos_app:prioridad_lista')
