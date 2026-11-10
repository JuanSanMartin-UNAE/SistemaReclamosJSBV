"""Vistas de consulta y mantenimiento de prioridades."""

from django.urls import reverse_lazy

from ..forms import PrioridadForm
from ..models import Prioridad
from .base import CrearView, EditarView, EliminarView, ListaView


class PrioridadLista(ListaView):
    """Listado paginado de prioridades."""

    model = Prioridad
    template_name = "reclamos_app/prioridades/lista.html"
    context_object_name = "prioridades"


class PrioridadCrear(CrearView):
    """Alta de una prioridad."""

    model = Prioridad
    form_class = PrioridadForm
    titulo = "Nueva prioridad"
    icono = "bi-exclamation-triangle"
    success_url = reverse_lazy("reclamos_app:prioridad_lista")


class PrioridadEditar(EditarView):
    """Edición de una prioridad."""

    model = Prioridad
    form_class = PrioridadForm
    titulo = "Editar prioridad"
    icono = "bi-exclamation-triangle"
    success_url = reverse_lazy("reclamos_app:prioridad_lista")


class PrioridadEliminar(EliminarView):
    """Baja de una prioridad."""

    model = Prioridad
    success_url = reverse_lazy("reclamos_app:prioridad_lista")
