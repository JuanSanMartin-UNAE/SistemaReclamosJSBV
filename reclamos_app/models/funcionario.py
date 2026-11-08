from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .cargo_funcionario import CargoFuncionario


class Funcionario(models.Model):
    id_funcionario = models.AutoField(
        primary_key=True,
        db_column='id_funcionario',
        db_comment='Identificador único del funcionario de la Junta',
    )
    nombre_apellido = models.CharField(
        'nombre y apellido',
        max_length=50,
        db_comment='Nombre y apellido del funcionario',
    )
    cargo = models.ForeignKey(
        CargoFuncionario,
        on_delete=models.PROTECT,
        db_column='id_cargo_funcionario',
        related_name='funcionarios',
        verbose_name='cargo',
        db_comment='Cargo institucional asignado al funcionario',
    )
    cant_maxima_despachada = models.PositiveIntegerField(
        'carga máxima',
        validators=[MinValueValidator(1)],
        db_comment=(
            'Límite máximo de incidentes activos que el funcionario puede tener '
            'asignados simultáneamente'
        ),
    )
    fecha_alta = models.DateField(
        'fecha de alta',
        default=timezone.localdate,
        db_comment='Fecha de alta del funcionario en el sistema',
    )

    class Meta:
        db_table = 'funcionarios'
        db_table_comment = (
            'Almacena los datos del personal operativo y administrativo que gestiona los incidentes'
        )
        ordering = ['nombre_apellido']
        verbose_name = 'funcionario'
        verbose_name_plural = 'funcionarios'

    def __str__(self):
        return self.nombre_apellido
