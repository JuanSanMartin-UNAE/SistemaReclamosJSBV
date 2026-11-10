from django.db import models
from django.utils import timezone

from .clasificacion_reclamo import ClasificacionReclamo


class CargoFuncionario(models.Model):
    """Cargo institucional y la clasificación de reclamos que atiende."""

    id_cargo = models.AutoField(
        primary_key=True,
        db_column="id_cargo",
        db_comment="Identificador único del cargo del funcionario",
    )
    nombre_cargo = models.CharField(
        "nombre del cargo",
        max_length=50,
        db_comment="Descripción o denominación del cargo institucional",
    )
    clase_reclamo_atiende = models.ForeignKey(
        ClasificacionReclamo,
        on_delete=models.PROTECT,
        db_column="id_clase_reclamo_atiende",
        related_name="cargos",
        verbose_name="clasificación que atiende",
        db_comment=(
            "Clasificación de reclamos que el cargo está habilitado para atender"
        ),
    )
    fecha_alta = models.DateField(
        "fecha de alta",
        default=timezone.localdate,
        db_comment="Fecha de registro del cargo institucional",
    )

    class Meta:
        db_table = "cargos_funcionarios"
        db_table_comment = (
            "Almacena la denominación de los cargos de los operadores "
            "y funcionarios de la Junta"
        )
        ordering = ["nombre_cargo"]
        verbose_name = "cargo de funcionario"
        verbose_name_plural = "cargos de funcionarios"

    def __str__(self):
        """Devuelve el nombre del cargo.

        Returns:
            str: Nombre visible.
        """
        return self.nombre_cargo
