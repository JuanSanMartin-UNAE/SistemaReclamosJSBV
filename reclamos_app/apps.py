"""Configuración de la aplicación de reclamos."""

from django.apps import AppConfig


class ReclamosAppConfig(AppConfig):
    """Aplicación principal del sistema de gestión de reclamos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "reclamos_app"
