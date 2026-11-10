"""Ajusta los encabezados que ngrok reenvía antes de que Django los interprete."""

import logging

from django.conf import settings

from reclamos.hosts import host_es_ngrok, normalizar_hostname, ultimo_valor

logger = logging.getLogger("django.security")


class EncabezadosProxyNgrok:
    """Normaliza el protocolo HTTPS del túnel y descarta encabezados falsificados.

    Django trata como seguro el primer valor de X-Forwarded-Proto. ngrok, en
    cambio, agrega el suyo al final y no borra el que traiga el cliente. Este
    middleware deja un único valor, el de ngrok, y solo si el host es del túnel.
    Una petición directa a localhost no puede hacerse pasar por HTTPS.
    """

    def __init__(self, get_response):
        """Guarda la siguiente capa de middleware.

        Args:
            get_response: Callable que continúa la cadena de middleware.
        """
        self.get_response = get_response

    def __call__(self, request):
        """Depura los encabezados del proxy y sigue con la petición.

        Args:
            request: Petición HTTP.

        Returns:
            HttpResponse: Respuesta de la vista o del middleware siguiente.
        """
        self._depurar_encabezados(request)
        return self.get_response(request)

    def _depurar_encabezados(self, request):
        """Deja un solo X-Forwarded-Proto cuando el host es del túnel.

        El cliente puede inventar X-Forwarded-Host. ngrok ya envía el hostname
        público en Host, así que ese encabezado se descarta.

        Args:
            request: Petición HTTP. Se modifica `request.META`.
        """
        host = normalizar_hostname(request.META.get("HTTP_HOST", ""))
        request.META.pop("HTTP_X_FORWARDED_HOST", None)

        proto = request.META.get("HTTP_X_FORWARDED_PROTO", "")
        if not getattr(settings, "BEHIND_PROXY", False) or not _host_de_confianza(host):
            if proto:
                logger.warning(
                    "Se descartó X-Forwarded-Proto para un host que no es el túnel: %s",
                    host or "(vacío)",
                )
            request.META.pop("HTTP_X_FORWARDED_PROTO", None)
            return

        if ultimo_valor(proto) == "https":
            request.META["HTTP_X_FORWARDED_PROTO"] = "https"
        else:
            request.META.pop("HTTP_X_FORWARDED_PROTO", None)


def _host_de_confianza(host):
    """Indica si el host puede recibir el protocolo informado por ngrok.

    Args:
        host: Hostname ya normalizado.

    Returns:
        bool: True para el dominio fijado o para un comodín de ngrok habilitado.
    """
    fijado = getattr(settings, "NGROK_HOSTNAME", "") or ""
    if fijado and host == fijado:
        return True
    return bool(getattr(settings, "ALLOW_NGROK", False) and host_es_ngrok(host))
