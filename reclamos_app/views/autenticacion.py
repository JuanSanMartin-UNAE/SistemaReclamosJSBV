"""Vistas de bienvenida, ingreso, registro, perfil y recuperación de contraseña."""

import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from ..forms import (
    IngresoForm,
    NuevaContrasenhaForm,
    PerfilUsuarioForm,
    RecuperarForm,
    RegistroForm,
)
from ..models import Usuario

logger = logging.getLogger(__name__)

PLANTILLAS = "reclamos_app/autenticacion/"


def bienvenida(request):
    """Muestra la portada o abre el panel si ya hay sesión.

    Args:
        request: Petición HTTP.

    Returns:
        HttpResponse: Portada, o redirección al panel.
    """
    if request.user.is_authenticated:
        return redirect("reclamos_app:panel")
    return render(request, "reclamos_app/bienvenida.html")


class Ingresar(auth_views.LoginView):
    """Inicio de sesión con el número de documento."""

    template_name = PLANTILLAS + "ingresar.html"
    authentication_form = IngresoForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Abre la sesión y, si no eligió recordarme, la cierra con el navegador.

        Args:
            form: Formulario de ingreso válido.

        Returns:
            HttpResponse: Redirección posterior al ingreso.
        """
        respuesta = super().form_valid(form)
        if not form.cleaned_data.get("recordarme"):
            self.request.session.set_expiry(0)
        messages.success(
            self.request,
            f"¡Bienvenido/a, {self.request.user.get_short_name()}!",
        )
        return respuesta

    def form_invalid(self, form):
        """Registra un ingreso rechazado sin guardar la contraseña.

        Args:
            form: Formulario de ingreso con errores.

        Returns:
            HttpResponse: El mismo formulario, con el error de credenciales.
        """
        logger.info("Se rechazó un intento de ingreso.")
        return super().form_invalid(form)


class Salir(auth_views.LogoutView):
    """Cierre de sesión."""


class Registro(CreateView):
    """Alta pública de una cuenta de usuario."""

    template_name = PLANTILLAS + "registro.html"
    form_class = RegistroForm
    success_url = reverse_lazy("reclamos_app:panel")

    def dispatch(self, request, *args, **kwargs):
        """Evita que una sesión activa vuelva a registrar una cuenta.

        Args:
            request: Petición HTTP.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Panel, si ya hay sesión, o el formulario.
        """
        if request.user.is_authenticated:
            return redirect("reclamos_app:panel")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Guarda la cuenta e inicia la sesión del usuario nuevo.

        Args:
            form: Formulario de registro válido.

        Returns:
            HttpResponse: Redirección al panel, o el formulario si el documento
            ya fue registrado.
        """
        try:
            self.object = form.save()
        except IntegrityError:
            logger.warning("No se registró un número de documento duplicado.")
            form.add_error(
                "num_documento",
                "Ya existe un usuario con este número de documento.",
            )
            return self.form_invalid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            "¡Su cuenta fue creada correctamente! Ya puede utilizar el sistema.",
        )
        return redirect(self.get_success_url())


class Perfil(LoginRequiredMixin, UpdateView):
    """Edición del perfil del usuario que tiene la sesión abierta."""

    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = PLANTILLAS + "perfil.html"
    success_url = reverse_lazy("reclamos_app:perfil")

    def get_object(self, queryset=None):
        """Devuelve únicamente la cuenta de la sesión.

        Args:
            queryset: Ignorado. El perfil no se busca por un identificador de la URL.

        Returns:
            Usuario: Usuario autenticado.
        """
        return self.request.user

    def form_valid(self, form):
        """Guarda el perfil sin permitir otro documento.

        Args:
            form: Formulario de perfil válido.

        Returns:
            HttpResponse: El mismo perfil, con la confirmación o el error.
        """
        try:
            self.object = form.save()
        except IntegrityError:
            logger.warning(
                "No se guardó el perfil del usuario %s.",
                self.request.user.pk,
            )
            form.add_error(
                None,
                "No se pudo guardar el perfil. Verificá los datos.",
            )
            return self.form_invalid(form)
        messages.success(self.request, "Actualizamos tu perfil.")
        return redirect(self.get_success_url())


class Recuperar(auth_views.PasswordResetView):
    """Solicitud de restablecimiento de contraseña por correo."""

    template_name = PLANTILLAS + "recuperar.html"
    form_class = RecuperarForm
    email_template_name = PLANTILLAS + "correo_recuperacion.txt"
    html_email_template_name = PLANTILLAS + "correo_recuperacion.html"
    subject_template_name = PLANTILLAS + "correo_recuperacion_asunto.txt"
    success_url = reverse_lazy("reclamos_app:recuperar_enviado")


class RecuperarEnviado(auth_views.PasswordResetDoneView):
    """Aviso de que la solicitud de recuperación fue recibida."""

    template_name = PLANTILLAS + "recuperar_enviado.html"


class RecuperarConfirmar(auth_views.PasswordResetConfirmView):
    """Formulario para elegir la nueva contraseña desde el enlace del correo."""

    template_name = PLANTILLAS + "recuperar_confirmar.html"
    form_class = NuevaContrasenhaForm
    success_url = reverse_lazy("reclamos_app:recuperar_completo")


class RecuperarCompleto(auth_views.PasswordResetCompleteView):
    """Confirmación de que la contraseña fue actualizada."""

    template_name = PLANTILLAS + "recuperar_completo.html"
