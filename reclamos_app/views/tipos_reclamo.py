"""Vistas de consulta y mantenimiento de tipos de reclamo."""

from django.urls import reverse_lazy

from ..forms import TipoReclamoForm
from ..models import TipoReclamo
from .base import CrearView, EditarView, EliminarView, ListaView


class TipoReclamoLista(ListaView):
    """Listado paginado de tipos de reclamo."""

    model = TipoReclamo
    template_name = "reclamos_app/tipos_reclamo/lista.html"
    context_object_name = "tipos"
    queryset = TipoReclamo.objects.select_related("clase_reclamo")


class TipoReclamoCrear(CrearView):
    """Alta de un tipo de reclamo."""

    model = TipoReclamo
    form_class = TipoReclamoForm
    titulo = "Nuevo tipo de reclamo"
    icono = "bi-list-check"
    success_url = reverse_lazy("reclamos_app:tipo_reclamo_lista")


class TipoReclamoEditar(EditarView):
    """Edición de un tipo de reclamo."""

    model = TipoReclamo
    form_class = TipoReclamoForm
    titulo = "Editar tipo de reclamo"
    icono = "bi-list-check"
    success_url = reverse_lazy("reclamos_app:tipo_reclamo_lista")


class TipoReclamoEliminar(EliminarView):
    """Baja de un tipo de reclamo."""

    model = TipoReclamo
    success_url = reverse_lazy("reclamos_app:tipo_reclamo_lista")
