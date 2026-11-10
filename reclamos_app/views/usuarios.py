"""Vistas de consulta y mantenimiento de usuarios."""

from django.urls import reverse_lazy

from ..forms import UsuarioForm
from ..models import Usuario
from .base import CrearView, EditarView, EliminarView, ListaView


class UsuarioLista(ListaView):
    """Listado paginado de usuarios."""

    model = Usuario
    template_name = "reclamos_app/usuarios/lista.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        """Incluye barrio y rol para evitar consultas por fila.

        Returns:
            QuerySet: Usuarios con las relaciones necesarias para el listado.
        """
        return super().get_queryset().select_related("barrio", "rol")


class UsuarioCrear(CrearView):
    """Alta de un usuario desde la administración."""

    model = Usuario
    form_class = UsuarioForm
    titulo = "Nuevo usuario"
    icono = "bi-person-plus"
    success_url = reverse_lazy("reclamos_app:usuario_lista")


class UsuarioEditar(EditarView):
    """Edición de un usuario."""

    model = Usuario
    form_class = UsuarioForm
    titulo = "Editar usuario"
    icono = "bi-person-gear"
    success_url = reverse_lazy("reclamos_app:usuario_lista")


class UsuarioEliminar(EliminarView):
    """Baja de un usuario."""

    model = Usuario
    success_url = reverse_lazy("reclamos_app:usuario_lista")
