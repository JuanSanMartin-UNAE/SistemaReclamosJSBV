"""Reclamo presentado por un usuario de la Junta."""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from ..constantes_reclamo import ESTADOS_CERRADOS, ESTADOS_RECONSIDERABLES
from .barrio import Barrio
from .conexion import Conexion
from .estado_reclamo import EstadoReclamo
from .funcionario import Funcionario
from .prioridad import Prioridad
from .tipo_reclamo import TipoReclamo


class Reclamo(models.Model):
    """Incidencia reportada, en particular una intermitencia del servicio."""

    id_reclamo = models.AutoField(
        primary_key=True,
        db_column="id_reclamo",
        db_comment="Identificador único del reclamo o incidencia reportada",
    )
    fecha_hora = models.DateTimeField(
        "fecha y hora",
        db_comment="Fecha y hora exacta en que se genera el reclamo",
    )
    descripcion = models.TextField(
        "descripción",
        db_comment="Detalle descriptivo de la incidencia reportada",
    )
    foto_evidencia = models.TextField(
        "foto de evidencia",
        null=True,
        blank=True,
        db_comment="Ruta o archivo de imagen de evidencia adjunto al reclamo",
    )
    latitud = models.DecimalField(
        "latitud",
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        db_comment="Coordenada de latitud geolocalizada para la API de Google Maps",
    )
    longitud = models.DecimalField(
        "longitud",
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        db_comment="Coordenada de longitud geolocalizada para la API de Google Maps",
    )
    barrio = models.ForeignKey(
        Barrio,
        on_delete=models.PROTECT,
        db_column="id_barrio",
        related_name="reclamos",
        verbose_name="barrio",
        db_comment="Barrio donde se localiza geográficamente el reclamo",
    )
    tipo = models.ForeignKey(
        TipoReclamo,
        on_delete=models.PROTECT,
        db_column="id_tipo_reclamo",
        related_name="reclamos",
        verbose_name="tipo",
        db_comment="Tipo específico de reclamo reportado",
    )
    estado = models.ForeignKey(
        EstadoReclamo,
        on_delete=models.PROTECT,
        db_column="id_estado",
        related_name="reclamos",
        verbose_name="estado",
        db_comment="Estado actual en el ciclo de vida del reclamo",
    )
    conexion = models.ForeignKey(
        Conexion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_conexion",
        related_name="reclamos",
        verbose_name="conexión",
        db_comment=(
            "Conexión de suministro de agua asociada al reclamo "
            "(opcional para no usuarios)"
        ),
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_funcionario",
        related_name="reclamos",
        verbose_name="funcionario",
        db_comment="Funcionario responsable asignado a la atención del reclamo",
    )
    prioridad = models.ForeignKey(
        Prioridad,
        on_delete=models.PROTECT,
        db_column="id_prioridad",
        related_name="reclamos",
        verbose_name="prioridad",
        db_comment="Nivel de prioridad asignado al reclamo",
    )
    posee_conexion = models.BooleanField(
        "posee conexión",
        db_comment="Indicador de si el reclamante posee o no conexión de agua activa",
    )

    class Meta:
        """Tabla, orden y nombres visibles del reclamo."""

        db_table = "reclamos"
        ordering = ["-fecha_hora"]
        verbose_name = "reclamo"
        verbose_name_plural = "reclamos"

    def __str__(self):
        """Devuelve el número de reclamo y su motivo.

        Returns:
            str: Texto visible.
        """
        return f"Reclamo {self.id_reclamo} — {self.tipo}"

    def nombre_estado(self):
        """Devuelve el estado en minúsculas para compararlo.

        Returns:
            str: Nombre del estado sin distinguir mayúsculas.
        """
        return self.estado.nombre_estado.casefold()

    def esta_cerrado(self):
        """Indica si el reclamo ya no admite gestión cotidiana.

        Returns:
            bool: True cuando el estado es de cierre.
        """
        cerrados = {nombre.casefold() for nombre in ESTADOS_CERRADOS}
        return self.nombre_estado() in cerrados

    @property
    def num_reclamo(self):
        """Código correlativo visible. Es el id serial de la tabla.

        Returns:
            str: Identificador de seis dígitos, o vacío si todavía no se guardó.
        """
        if not self.pk:
            return ""
        return f"{self.pk:06d}"

    @property
    def titular(self):
        """Usuario al que pertenece el reclamo.

        En un reclamo domiciliario sale de la conexión. En uno de la vía
        pública, que no tiene conexión, sale del aviso registrado al crearlo.

        Returns:
            Usuario | None: Titular, si se puede determinar.
        """
        if self.conexion_id and self.conexion.usuario_id:
            return self.conexion.usuario
        for aviso in self.notificaciones.all():
            if aviso.usuario_id:
                return aviso.usuario
        return None

    def es_titular(self, usuario):
        """Indica si el reclamo pertenece al usuario.

        Args:
            usuario: Usuario autenticado.

        Returns:
            bool: True si la conexión o el aviso del alta son de ese usuario.
        """
        if usuario is None or not getattr(usuario, "is_authenticated", False):
            return False
        if self.conexion_id and self.conexion.usuario_id == usuario.pk:
            return True
        return self.notificaciones.filter(usuario_id=usuario.pk).exists()

    def puede_editar(self, usuario):
        """Indica si el reclamo enviado todavía puede corregirse.

        El texto ya guardado no se modifica. El usuario solo consulta el detalle.

        Args:
            usuario: Usuario autenticado. No habilita la edición.

        Returns:
            bool: Siempre False.
        """
        del usuario
        return False

    def admite_reconsideracion(self):
        """Indica si el titular puede pedir una reconsideración.

        Returns:
            bool: True si el reclamo está resuelto o rechazado y no tiene
            una reconsideración previa.
        """
        reconsiderables = {nombre.casefold() for nombre in ESTADOS_RECONSIDERABLES}
        if self.nombre_estado() not in reconsiderables:
            return False
        try:
            self.reconsideracion
        except ObjectDoesNotExist:
            return True
        return False

    def clase_estado(self):
        """Devuelve la clase visual de Bootstrap para el estado.

        Returns:
            str: Clases de una insignia.
        """
        clases = {
            "pendiente": "text-bg-warning",
            "en proceso": "text-bg-primary",
            "resuelto": "text-bg-success",
            "rechazado": "text-bg-danger",
        }
        return clases.get(self.nombre_estado(), "text-bg-secondary")
