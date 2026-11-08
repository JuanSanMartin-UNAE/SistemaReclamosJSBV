from django.db import models
from django.utils import timezone


class Rol(models.Model):
    class Activo(models.TextChoices):
        SI = 'SI', 'Sí'
        NO = 'NO', 'No'

    id_rol = models.AutoField(
        primary_key=True,
        db_column='id_rol',
        db_comment='Identificador único del rol proporcionado por el sistema',
    )
    nombre_rol = models.CharField(
        'nombre del rol',
        max_length=30,
        db_comment='Denominación o descripción del rol',
    )
    fecha_alta = models.DateField(
        'fecha de alta',
        default=timezone.localdate,
        db_comment='Fecha de registro de rol',
    )
    activo = models.CharField(
        max_length=2,
        choices=Activo.choices,
        default=Activo.SI,
        db_comment='Estado de la cuenta activa/inactivo',
    )

    class Meta:
        db_table = 'roles'
        ordering = ['nombre_rol']
        verbose_name = 'rol'
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.nombre_rol
