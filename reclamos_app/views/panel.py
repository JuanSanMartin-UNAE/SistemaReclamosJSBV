from django.contrib.auth.decorators import login_required
from django.shortcuts import render

<<<<<<< Updated upstream
from ..models import Barrio, Rol, Usuario
=======
from ..constantes_reclamo import (
    CENTRO_LATITUD,
    CENTRO_LONGITUD,
    ESTADO_EN_PROCESO,
    ESTADO_PENDIENTE,
    ESTADO_RESUELTO,
    LATITUD_MAXIMA,
    LATITUD_MINIMA,
    LONGITUD_MAXIMA,
    LONGITUD_MINIMA,
)
from ..models import Barrio, EstadoReclamo, Reclamo
from ..reglas import coordenadas_en_bella_vista, reclamos_del_titular

logger = logging.getLogger(__name__)
POR_PAGINA = 12


def _fecha(valor):
    """Interpreta una fecha de filtro en formato ISO.

    Args:
        valor: Texto recibido en la consulta, o vacío.

    Returns:
        date | None: Fecha válida, o None si no se puede leer.
    """
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        logger.info("Se ignoró una fecha de filtro inválida.")
        return None


def _conteo_estado(nombre):
    """Cuenta los reclamos de un estado, sin distinguir mayúsculas.

    Args:
        nombre: Nombre del estado.

    Returns:
        int: Cantidad de reclamos.
    """
    return Reclamo.objects.filter(estado__nombre_estado__iexact=nombre).count()


def _exigir_gestor(request):
    """Rechaza el acceso de un usuario que no gestiona reclamos.

    Args:
        request: Petición HTTP autenticada.

    Returns:
        HttpResponse | None: Redirección al panel, o None si puede entrar.
    """
    if request.user.es_gestor:
        return None
    messages.error(request, "No tiene permisos para acceder a esa sección.")
    return redirect("reclamos_app:panel")
>>>>>>> Stashed changes


@login_required
def panel(request):
<<<<<<< Updated upstream
    contexto = {}
    if request.user.es_administrador:
        contexto.update({
            'total_barrios': Barrio.objects.count(),
            'total_roles': Rol.objects.count(),
            'total_usuarios': Usuario.objects.count(),
            'usuarios_activos': Usuario.objects.filter(is_active=True).count(),
            'ultimos_usuarios': Usuario.objects.select_related('barrio', 'rol').order_by('-fecha_inicio')[:5],
        })
    return render(request, 'reclamos_app/panel.html', contexto)
=======
    """Muestra el escritorio de gestión o el panel del usuario externo.

    Args:
        request: Petición HTTP de un usuario autenticado.

    Returns:
        HttpResponse: Plantilla según el rol.
    """
    if request.user.es_gestor:
        return _escritorio(request)
    contexto = {
        "mis_reclamos": (
            reclamos_del_titular(request.user)
            .select_related("tipo", "estado")
            .order_by("-fecha_hora")[:5]
        )
    }
    return render(request, "reclamos_app/panel.html", contexto)


def _escritorio(request):
    """Arma el tablero de reclamos con filtros, tabla y mapa.

    El mapa omite los reclamos resueltos y los que no tienen un punto
    dentro de Bella Vista.

    Args:
        request: Petición de un gestor.

    Returns:
        HttpResponse: Escritorio de gestión.
    """
    desde = _fecha(request.GET.get("desde", ""))
    hasta = _fecha(request.GET.get("hasta", ""))
    barrio_id = request.GET.get("barrio") or ""
    estado_id = request.GET.get("estado") or ""
    consulta = (
        Reclamo.objects.select_related(
            "tipo",
            "estado",
            "barrio",
            "conexion",
            "conexion__usuario",
        )
        .prefetch_related("notificaciones__usuario")
        .order_by("-fecha_hora")
    )
    if desde:
        consulta = consulta.filter(fecha_hora__date__gte=desde)
    if hasta:
        consulta = consulta.filter(fecha_hora__date__lte=hasta)
    if str(barrio_id).isdigit():
        consulta = consulta.filter(barrio_id=int(barrio_id))
    else:
        barrio_id = ""
    if str(estado_id).isdigit():
        consulta = consulta.filter(estado_id=int(estado_id))
    else:
        estado_id = ""
    paginador = Paginator(consulta, POR_PAGINA)
    pagina = paginador.get_page(request.GET.get("page"))
    puntos = []
    marcados = (
        consulta.exclude(latitud=None)
        .exclude(longitud=None)
        .exclude(estado__nombre_estado__iexact=ESTADO_RESUELTO)
    )
    for reclamo in marcados[:300]:
        if not coordenadas_en_bella_vista(reclamo.latitud, reclamo.longitud):
            continue
        puntos.append(
            {
                "lat": float(reclamo.latitud),
                "lng": float(reclamo.longitud),
                "titulo": f"#{reclamo.pk} · {reclamo.tipo}",
                "url": reverse("reclamos_app:reclamo_detalle", args=[reclamo.pk]),
            }
        )
    parametros = request.GET.copy()
    parametros.pop("page", None)
    contexto = {
        "reclamos": pagina,
        "page_obj": pagina,
        "is_paginated": pagina.paginator.num_pages > 1,
        "consulta_filtros": parametros.urlencode(),
        "barrios": Barrio.objects.order_by("nombre_barrio"),
        "estados": EstadoReclamo.objects.order_by("nombre_estado"),
        "desde": desde.isoformat() if desde else "",
        "hasta": hasta.isoformat() if hasta else "",
        "barrio_id": str(barrio_id),
        "estado_id": str(estado_id),
        "total_reclamos": Reclamo.objects.count(),
        "total_pendientes": _conteo_estado(ESTADO_PENDIENTE),
        "total_en_proceso": _conteo_estado(ESTADO_EN_PROCESO),
        "total_resueltos": _conteo_estado(ESTADO_RESUELTO),
        "puntos": puntos,
        "centro_lat": str(CENTRO_LATITUD),
        "centro_lng": str(CENTRO_LONGITUD),
        "lat_min": str(LATITUD_MINIMA),
        "lat_max": str(LATITUD_MAXIMA),
        "lng_min": str(LONGITUD_MINIMA),
        "lng_max": str(LONGITUD_MAXIMA),
        "maps_key": settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, "reclamos_app/escritorio.html", contexto)


@login_required
def reportes(request):
    """Resume los reclamos por estado, barrio y tipo.

    Args:
        request: Petición HTTP de un usuario autenticado.

    Returns:
        HttpResponse: Reporte, o el panel si el usuario no gestiona.
    """
    bloqueo = _exigir_gestor(request)
    if bloqueo is not None:
        return bloqueo
    contexto = {
        "por_estado": (
            Reclamo.objects.values("estado__nombre_estado")
            .annotate(total=Count("id_reclamo"))
            .order_by("-total")
        ),
        "por_barrio": (
            Reclamo.objects.values("barrio__nombre_barrio")
            .annotate(total=Count("id_reclamo"))
            .order_by("-total")
        ),
        "por_tipo": (
            Reclamo.objects.values("tipo__reclamo")
            .annotate(total=Count("id_reclamo"))
            .order_by("-total")
        ),
    }
    return render(request, "reclamos_app/reportes.html", contexto)


@login_required
def configuracion(request):
    """Muestra los catálogos del sistema para el administrador.

    Args:
        request: Petición HTTP de un usuario autenticado.

    Returns:
        HttpResponse: Configuración, o el panel si el usuario no gestiona.
    """
    bloqueo = _exigir_gestor(request)
    if bloqueo is not None:
        return bloqueo
    return render(request, "reclamos_app/configuracion.html")
>>>>>>> Stashed changes
