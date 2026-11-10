from django.db import models
from django.utils import timezone


class Rol(models.Model):
    """Rol de acceso asignable a un usuario."""

    class Activo(models.TextChoices):
        """Valores permitidos para el estado del rol."""

        SI = "SI", "Sí"
        NO = "NO", "No"

    id_rol = models.AutoField(
        primary_key=True,
        db_column="id_rol",
        db_comment="Identificador único del rol proporcionado por el sistema",
    )
    nombre_rol = models.CharField(
        "nombre del rol",
        max_length=30,
        db_comment="Denominación o descripción del rol",
    )
    fecha_alta = models.DateField(
        "fecha de alta",
        default=timezone.localdate,
        db_comment="Fecha de registro de rol",
    )
    activo = models.CharField(
        max_length=2,
        choices=Activo.choices,
        default=Activo.SI,
        db_comment="Estado de la cuenta activa/inactivo",
    )

    class Meta:
        db_table = "roles"
        ordering = ["nombre_rol"]
        verbose_name = "rol"
        verbose_name_plural = "roles"

    def __str__(self):
        """Devuelve el nombre del rol.

        Returns:
            str: Nombre visible.
        """
        return self.nombre_rol
