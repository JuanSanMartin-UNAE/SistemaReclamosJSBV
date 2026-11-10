from django.db import models
from django.utils import timezone


class EstadoReclamo(models.Model):
    """Estado del ciclo de vida de un reclamo."""

    id_estado = models.AutoField(
        primary_key=True,
        db_column="id_estado",
        db_comment="Identificador único del estado del reclamo",
    )
    nombre_estado = models.CharField(
        "nombre del estado",
        max_length=50,
        db_comment="Denominación y descripción del estado del reclamo",
    )
    fecha_alta = models.DateField(
        "fecha de alta",
        default=timezone.localdate,
        db_comment="Fecha de registro del estado de reclamo",
    )

    class Meta:
        db_table = "estados_reclamos"
        db_table_comment = (
            "Administra el ciclo de vida y los estados por los que "
            "atraviesa un incidente reportado"
        )
        ordering = ["nombre_estado"]
        verbose_name = "estado de reclamo"
        verbose_name_plural = "estados de reclamo"

    def __str__(self):
        """Devuelve el nombre del estado.

        Returns:
            str: Nombre visible.
        """
        return self.nombre_estado
