"""Vistas de consulta y mantenimiento de barrios."""

from django.urls import reverse_lazy

from ..forms import BarrioForm
from ..models import Barrio
from .base import CrearView, EditarView, EliminarView, ListaView


class BarrioLista(ListaView):
    """Listado paginado de barrios."""

    model = Barrio
    template_name = "reclamos_app/barrios/lista.html"
    context_object_name = "barrios"


class BarrioCrear(CrearView):
    """Alta de un barrio."""

    model = Barrio
    form_class = BarrioForm
    titulo = "Nuevo barrio"
    icono = "bi-geo-alt"
    success_url = reverse_lazy("reclamos_app:barrio_lista")


class BarrioEditar(EditarView):
    """Edición de un barrio."""

    model = Barrio
    form_class = BarrioForm
    titulo = "Editar barrio"
    icono = "bi-geo-alt"
    success_url = reverse_lazy("reclamos_app:barrio_lista")


class BarrioEliminar(EliminarView):
    """Baja de un barrio."""

    model = Barrio
    success_url = reverse_lazy("reclamos_app:barrio_lista")
