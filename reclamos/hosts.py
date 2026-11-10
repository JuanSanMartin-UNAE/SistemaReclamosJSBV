"""Hosts y orígenes públicos usados por el túnel de ngrok."""

import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SUFIJOS_NGROK = (
    "ngrok-free.app",
    "ngrok-free.dev",
    "ngrok.app",
    "ngrok.dev",
    "ngrok.io",
)


def dividir_lista(valor):
    """Parte una variable de entorno en piezas separadas por coma.

    Args:
        valor: Texto de la variable. Puede ser None.

    Returns:
        list[str]: Piezas sin espacios vacíos.
    """
    if not valor:
        return []
    texto = valor.replace(";", ",")
    if "://" not in texto:
        texto = texto.replace(" ", ",")
    return [pieza.strip() for pieza in texto.split(",") if pieza.strip()]


def unir_unicos(piezas):
    """Conserva el orden y descarta repetidos.

    Args:
        piezas: Valores ya normalizados.

    Returns:
        list[str]: Lista sin duplicados.
    """
    vistos = set()
    resultado = []
    for pieza in piezas:
        if pieza and pieza not in vistos:
            vistos.add(pieza)
            resultado.append(pieza)
    return resultado


def normalizar_hostname(valor):
    """Devuelve el hostname en minúsculas, sin esquema, puerto ni punto final.

    Args:
        valor: Host, origen o URL.

    Returns:
        str: Hostname, o cadena vacía si no se puede interpretar.
    """
    texto = (valor or "").strip().lower()
    if not texto:
        return ""
    if "://" in texto:
        try:
            analizado = urlparse(texto)
        except ValueError:
            logger.warning("No se pudo interpretar el host %r.", valor)
            return ""
        texto = analizado.hostname or analizado.netloc or ""
    else:
        texto = texto.split("/")[0]
    if texto.startswith("["):
        fin = texto.find("]")
        return texto[1:fin] if fin != -1 else ""
    return texto.split(":")[0].rstrip(".").lstrip(".")


def normalizar_origen(valor):
    """Devuelve un origen `scheme://host[:puerto]`.

    Args:
        valor: Origen con esquema, o un host suelto.

    Returns:
        str: Origen normalizado, o cadena vacía si no es válido.
    """
    texto = (valor or "").strip()
    if not texto:
        return ""
    if "://" not in texto:
        texto = "https://" + texto
    try:
        analizado = urlparse(texto)
    except ValueError:
        logger.warning("No se pudo interpretar el origen %r.", valor)
        return ""
    if analizado.scheme not in ("http", "https") or not analizado.netloc:
        return ""
    return f"{analizado.scheme}://{analizado.netloc}"


def host_es_ngrok(valor):
    """Indica si el valor pertenece a un dominio público de ngrok.

    Args:
        valor: Host, comodín u origen.

    Returns:
        bool: True si el sufijo es uno de los dominios de ngrok.
    """
    nombre = normalizar_hostname(valor)
    if nombre.startswith("*."):
        nombre = nombre[2:]
    return any(
        nombre == sufijo or nombre.endswith("." + sufijo) for sufijo in SUFIJOS_NGROK
    )


def ultimo_valor(encabezado):
    """Devuelve el último elemento de un encabezado separado por comas.

    ngrok agrega su valor al final de X-Forwarded-Proto. El valor de
    confianza es ese, no el que haya enviado el cliente al principio.

    Args:
        encabezado: Valor crudo del encabezado.

    Returns:
        str: Último elemento, en minúsculas y sin espacios.
    """
    if not encabezado:
        return ""
    return encabezado.split(",")[-1].strip().lower()


def construir_hosts_permitidos(hosts_entorno, permitir_ngrok, hostname_fijado):
    """Arma la lista de hosts que Django puede atender.

    Args:
        hosts_entorno: Hosts declarados en la configuración.
        permitir_ngrok: Si es True, agrega los comodines de ngrok.
        hostname_fijado: Hostname exacto del túnel, o cadena vacía.

    Returns:
        list[str]: Hosts sin duplicados. Los comodines solo entran si el
        túnel está habilitado.
    """
    hosts = list(hosts_entorno)
    if permitir_ngrok:
        hosts.extend(f".{sufijo}" for sufijo in SUFIJOS_NGROK)
    else:
        hosts = [
            host
            for host in hosts
            if (not host_es_ngrok(host) or normalizar_hostname(host) == hostname_fijado)
        ]
    if hostname_fijado:
        hosts.append(hostname_fijado)
    return unir_unicos(hosts)


def construir_origenes_csrf(origenes_extra, permitir_ngrok, hostname_fijado):
    """Arma los orígenes de confianza para el control CSRF.

    Args:
        origenes_extra: Orígenes declarados en la configuración.
        permitir_ngrok: Si es True, agrega los orígenes HTTPS de ngrok.
        hostname_fijado: Hostname exacto del túnel, o cadena vacía.

    Returns:
        list[str]: Orígenes sin duplicados.
    """
    origenes = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    if permitir_ngrok:
        origenes.extend(f"https://*.{sufijo}" for sufijo in SUFIJOS_NGROK)
    for origen in origenes_extra:
        if (
            not permitir_ngrok
            and host_es_ngrok(origen)
            and normalizar_hostname(origen) != hostname_fijado
        ):
            continue
        origenes.append(origen)
    if hostname_fijado:
        origenes.append(f"https://{hostname_fijado}")
    return unir_unicos(origenes)
