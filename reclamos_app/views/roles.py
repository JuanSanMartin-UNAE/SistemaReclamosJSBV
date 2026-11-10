"""Vistas de consulta y mantenimiento de roles."""

from django.urls import reverse_lazy

from ..forms import RolForm
from ..models import Rol
from .base import CrearView, EditarView, EliminarView, ListaView


class RolLista(ListaView):
    """Listado paginado de roles."""

    model = Rol
    template_name = "reclamos_app/roles/lista.html"
    context_object_name = "roles"


class RolCrear(CrearView):
    """Alta de un rol."""

    model = Rol
    form_class = RolForm
    titulo = "Nuevo rol"
    icono = "bi-person-badge"
    success_url = reverse_lazy("reclamos_app:rol_lista")


class RolEditar(EditarView):
    """Edición de un rol."""

    model = Rol
    form_class = RolForm
    titulo = "Editar rol"
    icono = "bi-person-badge"
    success_url = reverse_lazy("reclamos_app:rol_lista")


class RolEliminar(EliminarView):
    """Baja de un rol."""

    model = Rol
    success_url = reverse_lazy("reclamos_app:rol_lista")
