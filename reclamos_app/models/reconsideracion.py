"""Pedido de revisión de un reclamo ya resuelto o rechazado."""

from django.db import models
from django.utils import timezone

from .funcionario import Funcionario
from .prioridad import Prioridad
from .reclamo import Reclamo
from .usuario import Usuario


class Reconsideracion(models.Model):
    """Descargo del titular para que la Junta revise el cierre del reclamo."""

    id_reincidencia = models.AutoField(
        primary_key=True,
        db_column="id_reincidencia",
        db_comment="Identificador único de la reconsideración o apelación",
    )
    reclamo = models.OneToOneField(
        Reclamo,
        on_delete=models.CASCADE,
        db_column="id_reclamo",
        related_name="reconsideracion",
        verbose_name="reclamo",
        db_comment="Reclamo original sujeto a reconsideración",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        db_column="id_usuario",
        related_name="reconsideraciones",
        verbose_name="usuario",
        db_comment="Usuario que solicita la reconsideración",
    )
    prioridad = models.ForeignKey(
        Prioridad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_prioridad",
        related_name="reconsideraciones",
        verbose_name="prioridad",
        db_comment="Prioridad evaluada para la reconsideración",
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_funcionario",
        related_name="reconsideraciones",
        verbose_name="funcionario",
        db_comment="Funcionario encargado de evaluar la reconsideración",
    )
    descargo = models.TextField(
        "descargo",
        db_comment="Fundamentación o descargo presentado en la reconsideración",
    )
    fecha_reconsideracion = models.DateField(
        "fecha",
        default=timezone.localdate,
        db_comment="Fecha de presentación de la reconsideración",
    )

    class Meta:
        """Tabla de pedidos de reconsideración."""

        db_table = "reconsideracion"
        ordering = ["-fecha_reconsideracion"]
        verbose_name = "reconsideración"
        verbose_name_plural = "reconsideraciones"

    def __str__(self):
        """Devuelve el reclamo al que corresponde el pedido.

        Returns:
            str: Texto visible.
        """
        return f"Reconsideración del reclamo {self.reclamo_id}"
