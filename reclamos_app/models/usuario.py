from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

from .barrio import Barrio
from .rol import Rol


class Usuario(models.Model):
    id_usuario = models.AutoField(
        primary_key=True,
        db_column='Id_usuario',
        db_comment='Identificador único del usuario proporcionado por el sistema',
    )
    num_documento = models.CharField(
        'número de documento',
        max_length=20,
        db_comment='Número de documento de identidad del usuario',
    )
    nombre = models.CharField(
        max_length=100,
        db_comment='Nombre/s particular del usuario',
    )
    apellido = models.CharField(
        max_length=100,
        db_comment='Apellido/s particular del usuario',
    )
    telefono = models.CharField(
        'teléfono',
        max_length=12,
        db_comment='Número de teléfono del usuario',
    )
    correo_electronico = models.EmailField(
        'correo electrónico',
        max_length=150,
        null=True,
        blank=True,
        db_comment='Correo del usuario',
    )
    direccion = models.TextField(
        'dirección',
        null=True,
        blank=True,
        db_comment='Nombre de la calle/avenida donde reside el usuario',
    )
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='Id_barrio',
        related_name='usuarios',
        db_comment='Número de barrio asignado/escogido proporcionado por el sistema',
    )
    contrasenha = models.CharField(
        'contraseña',
        max_length=255,
        db_comment='Contraseña encriptada (Hash)',
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='rol_usuario',
        related_name='usuarios',
        db_comment='Número rol asignado/escogido proporcionado por el sistema',
    )
    fecha_inicio = models.DateTimeField(
        'fecha de registro',
        default=timezone.now,
        db_comment='Fecha en que se registra el usuario',
    )
    activo = models.BooleanField(
        default=True,
        db_comment='Estado de la cuenta activa/inactivo',
    )

    class Meta:
        db_table = 'Usuarios'
        ordering = ['apellido', 'nombre']
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'

    def set_contrasenha(self, contrasenha_plana):
        self.contrasenha = make_password(contrasenha_plana)

    def verificar_contrasenha(self, contrasenha_plana):
        return check_password(contrasenha_plana, self.contrasenha)
