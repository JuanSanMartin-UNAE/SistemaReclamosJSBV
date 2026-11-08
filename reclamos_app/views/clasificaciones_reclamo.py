from django.urls import reverse_lazy

from ..forms import ClasificacionReclamoForm
from ..models import ClasificacionReclamo
from .base import CrearView, EditarView, EliminarView, ListaView


class ClasificacionReclamoLista(ListaView):
    model = ClasificacionReclamo
    template_name = 'reclamos_app/clasificaciones_reclamo/lista.html'
    context_object_name = 'clasificaciones'


class ClasificacionReclamoCrear(CrearView):
    model = ClasificacionReclamo
    form_class = ClasificacionReclamoForm
    titulo = 'Nueva clasificación'
    icono = 'bi-tags'
    success_url = reverse_lazy('reclamos_app:clasificacion_reclamo_lista')


class ClasificacionReclamoEditar(EditarView):
    model = ClasificacionReclamo
    form_class = ClasificacionReclamoForm
    titulo = 'Editar clasificación'
    icono = 'bi-tags'
    success_url = reverse_lazy('reclamos_app:clasificacion_reclamo_lista')


class ClasificacionReclamoEliminar(EliminarView):
    model = ClasificacionReclamo
    success_url = reverse_lazy('reclamos_app:clasificacion_reclamo_lista')
