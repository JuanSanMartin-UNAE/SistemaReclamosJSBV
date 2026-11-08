from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .clasificacion_reclamo import ClasificacionReclamo


class TipoReclamo(models.Model):
    id_tipo_reclamo = models.AutoField(
        primary_key=True,
        db_column='id_tipo_reclamo',
        db_comment='Identificador único del tipo de reclamo específico',
    )
    clase_reclamo = models.ForeignKey(
        ClasificacionReclamo,
        on_delete=models.PROTECT,
        db_column='id_clase_reclamo',
        related_name='tipos',
        verbose_name='clasificación',
        db_comment='Clasificación general a la que pertenece el tipo de reclamo',
    )
    reclamo = models.CharField(
        'motivo del reclamo',
        max_length=100,
        db_comment='Descripción del motivo de reclamo preestablecido',
    )
    plazo_dias = models.PositiveIntegerField(
        'plazo en días',
        validators=[MinValueValidator(1)],
        db_comment='Plazo máximo establecido en días para dar solución o respuesta al reclamo',
    )
    fecha_alta = models.DateField(
        'fecha de alta',
        default=timezone.localdate,
        db_comment='Fecha de registro del tipo de reclamo',
    )

    class Meta:
        db_table = 'tipos_reclamos'
        db_table_comment = (
            'Catálogo de reclamos específicos según su índole técnico o comercial '
            'y sus plazos de respuesta'
        )
        ordering = ['reclamo']
        verbose_name = 'tipo de reclamo'
        verbose_name_plural = 'tipos de reclamo'

    def __str__(self):
        return self.reclamo
