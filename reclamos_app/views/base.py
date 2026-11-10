"""Vistas base del patrón MVT para los catálogos de administración."""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

logger = logging.getLogger(__name__)


class AdministradorRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe la vista a usuarios administradores."""

    def test_func(self):
        """Indica si el usuario de la petición puede administrar.

        Returns:
            bool: True cuando el usuario es administrador.
        """
        return self.request.user.es_administrador

    def handle_no_permission(self):
        """Responde cuando el usuario no puede entrar a la vista.

        Returns:
            HttpResponse: Redirección al panel, o al ingreso si no hay sesión.
        """
        if self.request.user.is_authenticated:
            messages.error(
                self.request, "No tiene permisos para acceder a esa sección."
            )
            return redirect("reclamos_app:panel")
        return super().handle_no_permission()


class GestorRequeridoMixin(AdministradorRequeridoMixin):
    """Permite el acceso al administrador y al usuario interno administrativo."""

    def test_func(self):
        """Indica si el usuario gestiona reclamos.

        Returns:
            bool: True para el administrador o el interno administrativo.
        """
        return getattr(self.request.user, "es_gestor", False)


class ListaView(AdministradorRequeridoMixin, ListView):
    """Listado paginado de un catálogo, solo para administradores."""

    paginate_by = 20


class FormularioMixin(AdministradorRequeridoMixin):
    """Formulario de alta o edición con título, icono y mensaje de éxito."""

    template_name = "reclamos_app/comun/formulario.html"
    titulo = ""
    icono = "bi-pencil-square"
    mensaje_exito = "Registro guardado correctamente."

    def get_context_data(self, **kwargs):
        """Agrega título, icono y URL de regreso al contexto.

        Args:
            **kwargs: Contexto adicional de la vista genérica.

        Returns:
            dict: Contexto de la plantilla del formulario.
        """
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["icono"] = self.icono
        contexto["bajada"] = getattr(self, "bajada", "")
        contexto["url_volver"] = self.success_url
        return contexto

    def form_valid(self, form):
        """Guarda el formulario y confirma la operación.

        Args:
            form: Formulario ya validado.

        Returns:
            HttpResponse: Redirección a la URL de éxito.
        """
        messages.success(self.request, self.mensaje_exito)
        return super().form_valid(form)


class CrearView(FormularioMixin, CreateView):
    """Alta de un registro de catálogo."""


class EditarView(FormularioMixin, UpdateView):
    """Edición de un registro de catálogo."""


class EliminarView(AdministradorRequeridoMixin, DeleteView):
    """Baja de un registro, con aviso si otros registros dependen de él."""

    template_name = "reclamos_app/comun/confirmar_eliminar.html"

    def get_context_data(self, **kwargs):
        """Agrega la URL de regreso a la confirmación de baja.

        Args:
            **kwargs: Contexto adicional de la vista genérica.

        Returns:
            dict: Contexto de la plantilla de confirmación.
        """
        contexto = super().get_context_data(**kwargs)
        contexto["url_volver"] = self.success_url
        return contexto

    def form_valid(self, form):
        """Elimina el registro o informa el conflicto de integridad.

        Args:
            form: Formulario de confirmación.

        Returns:
            HttpResponse: Redirección 302 al listado. Si hay dependencias,
            el registro se conserva y la respuesta lleva un mensaje de error.
        """
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            logger.warning(
                "No se eliminó %s pk=%s: hay registros que dependen de él.",
                self.model.__name__,
                getattr(self.object, "pk", None),
            )
            messages.error(
                self.request,
                "No se puede eliminar: hay registros que dependen de este.",
            )
            return redirect(self.success_url)
        messages.success(self.request, "Registro eliminado correctamente.")
        return respuesta
