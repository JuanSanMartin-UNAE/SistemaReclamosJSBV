from django.urls import reverse_lazy

from ..forms import TipoReclamoForm
from ..models import TipoReclamo
from .base import CrearView, EditarView, EliminarView, ListaView


class TipoReclamoLista(ListaView):
    model = TipoReclamo
    template_name = 'reclamos_app/tipos_reclamo/lista.html'
    context_object_name = 'tipos'
    queryset = TipoReclamo.objects.select_related('clase_reclamo')


class TipoReclamoCrear(CrearView):
    model = TipoReclamo
    form_class = TipoReclamoForm
    titulo = 'Nuevo tipo de reclamo'
    icono = 'bi-list-check'
    success_url = reverse_lazy('reclamos_app:tipo_reclamo_lista')


class TipoReclamoEditar(EditarView):
    model = TipoReclamo
    form_class = TipoReclamoForm
    titulo = 'Editar tipo de reclamo'
    icono = 'bi-list-check'
    success_url = reverse_lazy('reclamos_app:tipo_reclamo_lista')


class TipoReclamoEliminar(EliminarView):
    model = TipoReclamo
    success_url = reverse_lazy('reclamos_app:tipo_reclamo_lista')
