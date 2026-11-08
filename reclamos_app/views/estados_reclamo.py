from django.urls import reverse_lazy

from ..forms import EstadoReclamoForm
from ..models import EstadoReclamo
from .base import CrearView, EditarView, EliminarView, ListaView


class EstadoReclamoLista(ListaView):
    model = EstadoReclamo
    template_name = 'reclamos_app/estados_reclamo/lista.html'
    context_object_name = 'estados'


class EstadoReclamoCrear(CrearView):
    model = EstadoReclamo
    form_class = EstadoReclamoForm
    titulo = 'Nuevo estado'
    icono = 'bi-flag'
    success_url = reverse_lazy('reclamos_app:estado_reclamo_lista')


class EstadoReclamoEditar(EditarView):
    model = EstadoReclamo
    form_class = EstadoReclamoForm
    titulo = 'Editar estado'
    icono = 'bi-flag'
    success_url = reverse_lazy('reclamos_app:estado_reclamo_lista')


class EstadoReclamoEliminar(EliminarView):
    model = EstadoReclamo
    success_url = reverse_lazy('reclamos_app:estado_reclamo_lista')
