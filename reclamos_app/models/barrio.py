from django.db import models
from django.utils import timezone


class Barrio(models.Model):
    id_barrio = models.AutoField(
        primary_key=True,
        db_column='id_barrio',
        db_comment='Identificador único de barrio proporcionado por el sistema',
    )
    nombre_barrio = models.CharField(
        'nombre del barrio',
        max_length=50,
        db_comment='Nombre del barrio',
    )
    fecha_alta = models.DateField(
        'fecha de alta',
        default=timezone.localdate,
        db_comment='Fecha de registro del barrio',
    )

    class Meta:
        db_table = 'barrios'
        ordering = ['nombre_barrio']
        verbose_name = 'barrio'
        verbose_name_plural = 'barrios'

    def __str__(self):
        return self.nombre_barrio
