"""Reglas de catálogo, visibilidad y cupo de los reclamos."""

import logging
from pathlib import Path
from uuid import uuid4

from django.core.files.storage import default_storage
from django.db.models import Q
from django.utils import timezone

from .constantes_reclamo import (
    CLASE_COMERCIAL,
    CLASE_TECNICA,
    ESTADOS_CERRADOS,
    LATITUD_MAXIMA,
    LATITUD_MINIMA,
    LIMITE_RECLAMOS_ACTIVOS_FUNCIONARIO,
    LONGITUD_MAXIMA,
    LONGITUD_MINIMA,
    PLAZO_INTERMITENCIA_DIAS,
    PRIORIDAD_INICIAL,
    TIPO_PERDIDA_VIA_PUBLICA,
)
from .models import (
    ClasificacionReclamo,
    Conexion,
    EstadoReclamo,
    Notificacion,
    Prioridad,
    Reclamo,
    TipoReclamo,
)

logger = logging.getLogger(__name__)


def obtener_estado(nombre):
    """Devuelve un estado del catálogo y lo crea si todavía no existe.

    Args:
        nombre: Denominación exacta del estado.

    Returns:
        EstadoReclamo: Estado encontrado o recién creado.
    """
    estado = EstadoReclamo.objects.filter(nombre_estado__iexact=nombre).first()
    if estado is not None:
        return estado
    estado = EstadoReclamo.objects.create(nombre_estado=nombre)
    logger.info("Se creó el estado de reclamo %s.", nombre)
    return estado


def _clase_tecnica():
    """Devuelve la clasificación técnica ya cargada, sin duplicar acentos.

    Returns:
        ClasificacionReclamo: Clasificación TECNICO o Técnico existente, o una nueva.
    """
    clase = ClasificacionReclamo.objects.filter(nombre__iexact=CLASE_TECNICA).first()
    if clase is None:
        clase = ClasificacionReclamo.objects.filter(nombre__iexact="Técnico").first()
    if clase is None:
        clase = ClasificacionReclamo.objects.create(nombre=CLASE_TECNICA)
        logger.info("Se creó la clasificación %s.", CLASE_TECNICA)
    return clase


def asegurar_catalogo_reclamos():
    """Garantiza los estados y el tipo de vía pública ya escrito en mayúsculas.

    Returns:
        TipoReclamo: Tipo PERDIDA DE AGUA EN LA VIA PUBLICA.
    """
    for nombre in ("Pendiente", "En proceso", "Resuelto", "Rechazado"):
        obtener_estado(nombre)
    tecnica = _clase_tecnica()
    if not ClasificacionReclamo.objects.filter(nombre=CLASE_COMERCIAL).exists():
        ClasificacionReclamo.objects.create(nombre=CLASE_COMERCIAL)
        logger.info("Se creó la clasificación %s.", CLASE_COMERCIAL)
    tipo = TipoReclamo.objects.filter(reclamo=TIPO_PERDIDA_VIA_PUBLICA).first()
    if tipo is not None:
        return tipo
    tipo = TipoReclamo.objects.create(
        clase_reclamo=tecnica,
        reclamo=TIPO_PERDIDA_VIA_PUBLICA,
        plazo_dias=PLAZO_INTERMITENCIA_DIAS,
    )
    logger.info("Se creó el tipo de reclamo %s.", TIPO_PERDIDA_VIA_PUBLICA)
    return tipo


def coordenadas_en_bella_vista(latitud, longitud):
    """Indica si el punto cae dentro del distrito de Bella Vista.

    Args:
        latitud: Latitud informada.
        longitud: Longitud informada.

    Returns:
        bool: True cuando ambas coordenadas están dentro del recuadro.
    """
    if latitud is None or longitud is None:
        return False
    return (
        LATITUD_MINIMA <= latitud <= LATITUD_MAXIMA
        and LONGITUD_MINIMA <= longitud <= LONGITUD_MAXIMA
    )


def prioridad_inicial():
    """Devuelve la prioridad con la que nace un reclamo.

    Returns:
        Prioridad: La prioridad media, o la primera disponible.
    """
    prioridad = Prioridad.objects.filter(
        nombre_prioridad__iexact=PRIORIDAD_INICIAL
    ).first()
    if prioridad is not None:
        return prioridad
    prioridad = Prioridad.objects.order_by("id_prioridades").first()
    if prioridad is not None:
        return prioridad
    prioridad = Prioridad.objects.create(nombre_prioridad=PRIORIDAD_INICIAL)
    logger.info("Se creó la prioridad %s.", PRIORIDAD_INICIAL)
    return prioridad


def guardar_foto(archivo):
    """Guarda la evidencia en la carpeta de medios y devuelve su ruta.

    Args:
        archivo: Archivo subido por el usuario.

    Returns:
        str: Ruta relativa guardada en `foto_evidencia`.
    """
    extension = Path(archivo.name).suffix.lower()
    return default_storage.save(f"reclamos/{uuid4().hex}{extension}", archivo)


def conexion_del_usuario(usuario, barrio, numero_medidor):
    """Busca o crea la conexión domiciliaria del titular.

    Args:
        usuario: Titular autenticado.
        barrio: Barrio del reclamo.
        numero_medidor: Medidor o cuenta informado.

    Returns:
        Conexion: Conexión existente o recién creada.

    Raises:
        ValueError: Si no hay número de medidor.
    """
    medidor = (numero_medidor or "").strip()
    if not medidor:
        raise ValueError("El reclamo domiciliario necesita un número de medidor.")
    conexion = Conexion.objects.filter(usuario=usuario, numero_medidor=medidor).first()
    if conexion is not None:
        return conexion
    conexion = Conexion.objects.create(
        usuario=usuario,
        numero_medidor=medidor,
        barrio=barrio,
    )
    logger.info("Se registró la conexión %s del usuario %s.", medidor, usuario.pk)
    return conexion


def reclamos_visibles(usuario):
    """Devuelve los reclamos que el usuario puede consultar.

    Args:
        usuario: Usuario autenticado.

    Returns:
        QuerySet: Todos los reclamos si gestiona; si no, solo los propios.
    """
    consulta = Reclamo.objects.select_related(
        "tipo",
        "estado",
        "barrio",
        "prioridad",
        "funcionario",
        "conexion",
        "conexion__usuario",
    )
    consulta = consulta.prefetch_related("notificaciones__usuario")
    if not usuario.es_gestor:
        consulta = reclamos_del_titular(usuario, consulta)
    return consulta


def conexion_segun_modalidad(usuario, barrio, posee_conexion, numero_medidor):
    """Devuelve la conexión domiciliaria, o None si el reclamo es zonal.

    Un reclamo de la vía pública se guarda con id_conexion nulo.

    Args:
        usuario: Titular autenticado.
        barrio: Barrio del reclamo.
        posee_conexion: True cuando el problema es de su conexión.
        numero_medidor: Medidor informado en la modalidad domiciliaria.

    Returns:
        Conexion | None: Conexión del titular, o None en la vía pública.
    """
    if not posee_conexion:
        return None
    return conexion_del_usuario(usuario, barrio, numero_medidor)


def reclamos_del_titular(usuario, consulta=None):
    """Filtra los reclamos que el usuario puede ver como propios.

    Args:
        usuario: Titular autenticado.
        consulta: QuerySet de partida. Si no se indica, parte de todos.

    Returns:
        QuerySet: Reclamos de su conexión o de un aviso a su nombre.
    """
    if consulta is None:
        consulta = Reclamo.objects.all()
    return consulta.filter(
        Q(conexion__usuario=usuario) | Q(notificaciones__usuario=usuario)
    ).distinct()


def asegurar_aviso(reclamo, usuario):
    """Deja un aviso que vincula al titular con el reclamo que acaba de guardar.

    La tabla de reclamos no tiene id_usuario. El aviso usa la tabla
    notificaciones, que sí relaciona reclamo y usuario.

    Args:
        reclamo: Reclamo recién guardado.
        usuario: Titular autenticado.

    Returns:
        Notificacion: Aviso existente o recién creado.
    """
    aviso = Notificacion.objects.filter(reclamo=reclamo, usuario=usuario).first()
    if aviso is not None:
        return aviso
    aviso = Notificacion.objects.create(
        reclamo=reclamo,
        usuario=usuario,
        mensaje=f"Reclamo {reclamo.num_reclamo} registrado."[:100],
        fecha_envio=timezone.localdate(),
    )
    logger.info("Se avisó al usuario %s del reclamo %s.", usuario.pk, reclamo.pk)
    return aviso


def tope_funcionario(funcionario):
    """Calcula cuántos reclamos activos puede tener un funcionario.

    El tope del sistema es 5. Si el cargo admite menos, se usa ese límite.

    Args:
        funcionario: Funcionario candidato a recibir el reclamo.

    Returns:
        int: Cantidad máxima de reclamos activos.
    """
    return min(
        LIMITE_RECLAMOS_ACTIVOS_FUNCIONARIO,
        funcionario.cant_maxima_despachada,
    )


def reclamos_activos(funcionario, excluir_pk=None):
    """Cuenta los reclamos abiertos asignados a un funcionario.

    Args:
        funcionario: Funcionario evaluado.
        excluir_pk: Reclamo que no debe contarse, por ejemplo el que se edita.

    Returns:
        int: Cantidad de reclamos que siguen activos.
    """
    cerrados = Q()
    for nombre in ESTADOS_CERRADOS:
        cerrados |= Q(estado__nombre_estado__iexact=nombre)
    consulta = Reclamo.objects.filter(funcionario=funcionario).exclude(cerrados)
    if excluir_pk:
        consulta = consulta.exclude(pk=excluir_pk)
    return consulta.count()


def cupo_disponible(funcionario, excluir_pk=None):
    """Indica si el funcionario puede recibir un reclamo activo más.

    Args:
        funcionario: Funcionario candidato.
        excluir_pk: Reclamo excluido del conteo.

    Returns:
        bool: True cuando todavía no alcanzó su tope.
    """
    return reclamos_activos(funcionario, excluir_pk) < tope_funcionario(funcionario)
