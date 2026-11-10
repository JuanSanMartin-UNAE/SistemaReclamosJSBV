import logging

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

from .barrio import Barrio
from .rol import Rol

logger = logging.getLogger(__name__)


class UsuarioManager(BaseUserManager):
    """Crea usuarios del sistema con la contraseña hasheada."""

    use_in_migrations = True

    def _crear(self, num_documento, password, **campos):
        """Persiste un usuario a partir del documento y la contraseña.

        Args:
            num_documento: Número de documento, usado como identificador de acceso.
            password: Contraseña en texto plano. Se guarda hasheada.
            **campos: Resto de atributos del usuario.

        Returns:
            Usuario: Instancia guardada.

        Raises:
            ValueError: Si el número de documento está vacío.
        """
        if not num_documento:
            logger.error("Se intentó crear un usuario sin número de documento.")
            raise ValueError("El número de documento es obligatorio.")
        if campos.get("correo_electronico"):
            campos["correo_electronico"] = self.normalize_email(
                campos["correo_electronico"]
            )
        usuario = self.model(num_documento=num_documento, **campos)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, num_documento, password=None, **campos):
        """Crea un usuario sin permisos de administración.

        Args:
            num_documento: Número de documento.
            password: Contraseña en texto plano.
            **campos: Resto de atributos del usuario.

        Returns:
            Usuario: Instancia guardada.
        """
        campos.setdefault("is_staff", False)
        campos.setdefault("is_superuser", False)
        return self._crear(num_documento, password, **campos)

    def create_superuser(self, num_documento, password=None, **campos):
        """Crea un usuario con acceso total al sistema.

        Args:
            num_documento: Número de documento.
            password: Contraseña en texto plano.
            **campos: Resto de atributos del usuario.

        Returns:
            Usuario: Superusuario guardado.
        """
        campos["is_staff"] = True
        campos["is_superuser"] = True
        return self._crear(num_documento, password, **campos)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Persona que accede al sistema con su número de documento."""

    id_usuario = models.AutoField(
        primary_key=True,
        db_column="id_usuario",
        db_comment="Identificador único del usuario proporcionado por el sistema",
    )
    num_documento = models.CharField(
        "número de documento",
        max_length=20,
        unique=True,
        error_messages={"unique": "Ya existe un usuario con este número de documento."},
        db_comment="Número de documento de identidad del usuario",
    )
    nombre = models.CharField(
        max_length=100,
        db_comment="Nombre/s particular del usuario",
    )
    apellido = models.CharField(
        max_length=100,
        db_comment="Apellido/s particular del usuario",
    )
    telefono = models.CharField(
        "teléfono",
        max_length=12,
        db_comment="Número de teléfono del usuario",
    )
    correo_electronico = models.EmailField(
        "correo electrónico",
        max_length=150,
        default="",
        db_comment="Correo del usuario",
    )
    direccion = models.TextField(
        "dirección",
        null=True,
        blank=True,
        db_comment="Nombre de la calle/avenida donde reside el usuario",
    )
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="id_barrio",
        related_name="usuarios",
        db_comment="Número de barrio asignado/escogido proporcionado por el sistema",
    )
    password = models.CharField(
        "contraseña",
        max_length=255,
        db_column="contrasenha",
        db_comment="Contraseña encriptada (Hash)",
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="rol_usuario",
        related_name="usuarios",
        db_comment="Número rol asignado/escogido proporcionado por el sistema",
    )
    fecha_inicio = models.DateField(
        "fecha de registro",
        default=timezone.localdate,
        db_comment="Fecha en que se registra el usuario",
    )
    is_active = models.BooleanField(
        "activo",
        default=True,
        db_column="activo",
        db_comment="Estado de la cuenta activa/inactivo",
    )
    is_staff = models.BooleanField(
        "acceso al panel de administración",
        default=False,
        db_column="es_staff",
        db_comment="Indica si el usuario puede ingresar al panel de administración",
    )
    is_superuser = models.BooleanField(
        "superusuario",
        default=False,
        db_column="es_superusuario",
        help_text=(
            "Tiene todos los permisos sin necesidad de asignarlos explícitamente."
        ),
        db_comment="Indica si el usuario tiene todos los permisos del sistema",
    )
    last_login = models.DateTimeField(
        "último acceso",
        null=True,
        blank=True,
        db_column="ultimo_acceso",
        db_comment="Fecha y hora del último inicio de sesión",
    )

    objects = UsuarioManager()

    USERNAME_FIELD = "num_documento"
    EMAIL_FIELD = "correo_electronico"
    REQUIRED_FIELDS = ["nombre", "apellido", "telefono"]

    class Meta:
        db_table = "usuarios"
        ordering = ["apellido", "nombre"]
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        """Devuelve apellido y nombre.

        Returns:
            str: Texto visible del usuario.
        """
        return f"{self.apellido}, {self.nombre}"

    def get_full_name(self):
        """Devuelve el nombre completo.

        Returns:
            str: Nombre seguido del apellido.
        """
        return f"{self.nombre} {self.apellido}".strip()

    def get_short_name(self):
        """Devuelve el nombre de pila.

        Returns:
            str: Nombre usado en el saludo de ingreso.
        """
        return self.nombre

    @property
    def iniciales(self):
        """Devuelve las iniciales del nombre y del apellido.

        Returns:
            str: Dos letras en mayúscula.
        """
        return f"{self.nombre[:1]}{self.apellido[:1]}".upper()

    def _nombre_rol(self):
        """Devuelve el nombre del rol, en minúsculas.

        Returns:
            str: Nombre del rol, o una cadena vacía si no tiene.
        """
        if not self.rol_id:
            return ""
        return (self.rol.nombre_rol or "").casefold()

    @property
    def es_administrador(self):
        """Indica si el usuario administra el sistema.

        Returns:
            bool: True para superusuario, personal o rol Administrador.
        """
        if self.is_superuser or self.is_staff:
            return True
        return self._nombre_rol() == "administrador"

    @property
    def es_administrativo(self):
        """Indica si el usuario es el interno que gestiona reclamos.

        Returns:
            bool: True cuando el rol es USUARIO INTERNO ADMINISTRATIVO.
        """
        return self._nombre_rol() == "usuario interno administrativo"

    @property
    def es_gestor(self):
        """Indica si al ingresar corresponde el escritorio de gestión.

        Returns:
            bool: True para el administrador del sistema o el interno administrativo.
        """
        return self.es_administrador or self.es_administrativo
