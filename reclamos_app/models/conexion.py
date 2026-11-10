"""Conexión de agua asociada a un usuario."""

from django.db import models

from .barrio import Barrio
from .usuario import Usuario


class Conexion(models.Model):
    """Suministro de agua, con o sin medidor, de un usuario."""

    id_conexiones = models.AutoField(
        primary_key=True,
        db_column="id_conexiones",
        db_comment="Identificador único de la conexión o suministro de agua",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_usuario",
        related_name="conexiones",
        verbose_name="usuario",
        db_comment="Usuario titular responsable de la conexión",
    )
    numero_medidor = models.CharField(
        "número de medidor",
        max_length=4,
        db_comment="Número de medidor de la conexión",
    )
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_barrio",
        related_name="conexiones",
        verbose_name="barrio",
        db_comment="Barrio donde se encuentra instalada la conexión",
    )

    class Meta:
        """Tabla de conexiones de suministro."""

        db_table = "conexiones"
        ordering = ["numero_medidor"]
        verbose_name = "conexión"
        verbose_name_plural = "conexiones"

    def __str__(self):
        """Devuelve el medidor y, si existe, el titular.

        Returns:
            str: Texto visible.
        """
        if self.usuario_id:
            return f"{self.numero_medidor} · {self.usuario}"
        return self.numero_medidor
