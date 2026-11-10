"""Nota de seguimiento de un reclamo."""

from django.db import models

from .funcionario import Funcionario
from .reclamo import Reclamo


class Bitacora(models.Model):
    """Comentario de seguimiento asociado a un reclamo."""

    id_nota = models.AutoField(
        primary_key=True,
        db_column="id_nota",
        db_comment="Identificador único de la nota de bitácora",
    )
    reclamo = models.ForeignKey(
        Reclamo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="id_reclamo",
        related_name="notas",
        verbose_name="reclamo",
        db_comment="Reclamo al que pertenece la nota",
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_funcionario",
        related_name="notas",
        verbose_name="funcionario",
        db_comment="Funcionario que escribió la nota, si corresponde",
    )
    comentario = models.TextField(
        "comentario",
        db_comment="Texto del seguimiento o de la respuesta",
    )
    fecha_comentario = models.DateField(
        "fecha",
        null=True,
        blank=True,
        db_comment="Fecha del comentario",
    )

    class Meta:
        """Tabla de notas de seguimiento."""

        db_table = "bitacora"
        ordering = ["-fecha_comentario", "-id_nota"]
        verbose_name = "nota de bitácora"
        verbose_name_plural = "bitácora"

    def __str__(self):
        """Devuelve un recorte del comentario.

        Returns:
            str: Texto visible.
        """
        return self.comentario[:60]
