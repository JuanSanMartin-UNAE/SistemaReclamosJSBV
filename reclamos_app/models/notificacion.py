"""Aviso asociado a un reclamo y a su destinatario."""

from django.db import models

from .reclamo import Reclamo
from .usuario import Usuario


class Notificacion(models.Model):
    """Notificación ya prevista en la tabla `notificaciones`."""

    id_notificacion = models.AutoField(
        primary_key=True,
        db_column="id_notificacion",
        db_comment="Identificador único de la notificación enviada",
    )
    reclamo = models.ForeignKey(
        Reclamo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="id_reclamo",
        related_name="notificaciones",
        verbose_name="reclamo",
        db_comment="Reclamo asociado al aviso o notificación",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="id_usuario",
        related_name="notificaciones",
        verbose_name="usuario",
        db_comment="Usuario destinatario de la notificación",
    )
    mensaje = models.CharField(
        "mensaje",
        max_length=100,
        db_comment="Texto del mensaje de notificación emitido",
    )
    fecha_envio = models.DateField(
        "fecha de envío",
        db_comment="Fecha en que se despachó la notificación",
    )

    class Meta:
        """Tabla de avisos del reclamo."""

        db_table = "notificaciones"
        ordering = ["-fecha_envio", "-id_notificacion"]
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"

    def __str__(self):
        """Devuelve el mensaje del aviso.

        Returns:
            str: Texto visible.
        """
        return self.mensaje
