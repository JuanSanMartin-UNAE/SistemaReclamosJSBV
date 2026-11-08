from django.db import models
from django.utils import timezone


class Prioridad(models.Model):
    id_prioridades = models.AutoField(
        primary_key=True,
        db_column='id_prioridades',
        db_comment='Identificador único del nivel de prioridad',
    )
    nombre_prioridad = models.CharField(
        'nombre de la prioridad',
        max_length=20,
        db_comment='Descripción de la prioridad establecida (Ej. Alta, Media, Baja)',
    )
    fecha_alta = models.DateField(
        'fecha de alta',
        default=timezone.localdate,
        db_comment='Fecha de registro de la prioridad',
    )

    class Meta:
        db_table = 'prioridades'
        db_table_comment = (
            'Registra los niveles de urgencia o prioridad asignados a la naturaleza del reclamo'
        )
        ordering = ['nombre_prioridad']
        verbose_name = 'prioridad'
        verbose_name_plural = 'prioridades'

    def __str__(self):
        return self.nombre_prioridad
