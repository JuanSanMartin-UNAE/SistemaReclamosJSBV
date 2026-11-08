from django.db import models
from django.utils import timezone


class ClasificacionReclamo(models.Model):
    id_tipo_reclamo = models.AutoField(
        primary_key=True,
        db_column='id_tipo_reclamo',
        db_comment='Identificador único de la clasificación del reclamo',
    )
    nombre = models.CharField(
        max_length=50,
        db_comment='Denominación de la clasificación del reclamo',
    )
    fecha_alta = models.DateField(
        'fecha de alta',
        default=timezone.localdate,
        db_comment='Fecha de registro de la clasificación del reclamo',
    )

    class Meta:
        db_table = 'clasificacion_reclamos'
        db_table_comment = (
            'Categorización de reclamos en técnico o comercial conforme al Reglamento de la Ley 1614'
        )
        ordering = ['nombre']
        verbose_name = 'clasificación de reclamo'
        verbose_name_plural = 'clasificaciones de reclamo'

    def __str__(self):
        return self.nombre
