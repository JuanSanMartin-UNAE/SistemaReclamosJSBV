"""Vistas para registrar reclamos y pedir su reconsideración."""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from ..constantes_reclamo import (
    CENTRO_LATITUD,
    CENTRO_LONGITUD,
    ESTADO_EN_PROCESO,
    ESTADO_PENDIENTE,
    LATITUD_MAXIMA,
    LATITUD_MINIMA,
    LONGITUD_MAXIMA,
    LONGITUD_MINIMA,
)
from ..formularios_reclamo import (
    GestionReclamoForm,
    ReclamoForm,
    ReconsideracionForm,
    ResolverReconsideracionForm,
)
from ..models import Bitacora, Reclamo, Reconsideracion
from ..reglas import (
    asegurar_aviso,
    asegurar_catalogo_reclamos,
    conexion_segun_modalidad,
    guardar_foto,
    obtener_estado,
    prioridad_inicial,
    reclamos_visibles,
)
from .base import GestorRequeridoMixin

logger = logging.getLogger(__name__)


def _completar_mapa(contexto, reclamo=None):
    """Agrega la clave del mapa y el recuadro de Bella Vista.

    Args:
        contexto: Diccionario de la plantilla.
        reclamo: Reclamo en edición, para centrar el mapa en su punto.

    Returns:
        dict: El mismo contexto, con los datos del mapa.
    """
    if (
        reclamo is not None
        and reclamo.latitud is not None
        and reclamo.longitud is not None
    ):
        centro_lat = reclamo.latitud
        centro_lng = reclamo.longitud
    else:
        centro_lat = CENTRO_LATITUD
        centro_lng = CENTRO_LONGITUD
    contexto.update(
        {
            "maps_key": settings.GOOGLE_MAPS_API_KEY,
            "lat_min": str(LATITUD_MINIMA),
            "lat_max": str(LATITUD_MAXIMA),
            "lng_min": str(LONGITUD_MINIMA),
            "lng_max": str(LONGITUD_MAXIMA),
            "centro_lat": str(centro_lat),
            "centro_lng": str(centro_lng),
        }
    )
    return contexto


def _guardar_reclamo(form, usuario, reclamo):
    """Aplica la modalidad, guarda la foto y persiste el reclamo.

    Args:
        form: Formulario ya validado.
        usuario: Titular autenticado.
        reclamo: Instancia todavía sin guardar, o la que se edita.

    Returns:
        Reclamo | None: Reclamo guardado, o None si hubo que volver al formulario.
    """
    try:
        reclamo.conexion = conexion_segun_modalidad(
            usuario,
            form.cleaned_data["barrio"],
            form.cleaned_data["posee_conexion"],
            form.cleaned_data.get("numero_medidor"),
        )
    except ValueError:
        logger.info("Faltó el medidor en un reclamo domiciliario.")
        form.add_error("numero_medidor", "Indicá el número de medidor o cuenta.")
        return None
    foto = form.cleaned_data.get("foto")
    if foto:
        try:
            reclamo.foto_evidencia = guardar_foto(foto)
        except OSError:
            logger.exception("No se guardó la evidencia del reclamo.")
            form.add_error("foto", "No se pudo guardar la foto. Intentá de nuevo.")
            return None
    try:
        reclamo.save()
    except IntegrityError:
        logger.warning("No se guardó el reclamo por un conflicto de datos.")
        form.add_error(None, "No se pudo guardar el reclamo. Revisá los datos.")
        return None
    except ValidationError as error:
        logger.info("El reclamo no superó la validación del modelo.")
        form.add_error(None, error)
        return None
    asegurar_aviso(reclamo, usuario)
    return reclamo


class FormularioUsuarioMixin(LoginRequiredMixin):
    """Formulario autenticado, con el mismo diseño que los catálogos."""

    template_name = "reclamos_app/comun/formulario.html"
    titulo = ""
    icono = "bi-droplet"
    bajada = ""
    mensaje_exito = "Registro guardado correctamente."

    def get_context_data(self, **kwargs):
        """Agrega título, icono, bajada y URL de regreso.

        Args:
            **kwargs: Contexto adicional de la vista genérica.

        Returns:
            dict: Contexto de la plantilla del formulario.
        """
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = self.titulo
        contexto["icono"] = self.icono
        contexto["bajada"] = self.bajada
        contexto["url_volver"] = self.get_url_volver()
        return contexto

    def get_url_volver(self):
        """Devuelve la pantalla a la que vuelve el botón Cancelar.

        Returns:
            str: Ruta de la lista de reclamos.
        """
        return reverse("reclamos_app:reclamo_lista")

    def form_valid(self, form):
        """Confirma el guardado.

        Args:
            form: Formulario ya validado.

        Returns:
            HttpResponse: Redirección a la URL de éxito.
        """
        messages.success(self.request, self.mensaje_exito)
        return super().form_valid(form)

    def form_invalid(self, form):
        """Registra un envío que no superó la validación.

        Args:
            form: Formulario con errores.

        Returns:
            HttpResponse: El mismo formulario, con los errores visibles.
        """
        logger.info(
            "Formulario %s inválido para el usuario %s.",
            self.__class__.__name__,
            self.request.user.pk,
        )
        return super().form_invalid(form)


class ReclamoLista(LoginRequiredMixin, ListView):
    """Listado de reclamos propios, o de todos si el usuario administra."""

    model = Reclamo
    template_name = "reclamos_app/reclamos/lista.html"
    context_object_name = "reclamos"
    paginate_by = 20

    def get_queryset(self):
        """Filtra los reclamos visibles para quien consulta.

        Returns:
            QuerySet: Reclamos del más reciente al más antiguo.
        """
        return reclamos_visibles(self.request.user).order_by("-fecha_hora")


class ReclamoCrear(FormularioUsuarioMixin, CreateView):
    """Alta de un reclamo domiciliario o de la vía pública."""

    model = Reclamo
    form_class = ReclamoForm
    template_name = "reclamos_app/reclamos/crear_reclamo.html"
    titulo = "Registrar reclamo"
    icono = "bi-geo-alt"
    bajada = (
        "Elegí la categoría y contá el problema en tu conexión o en la vía pública."
    )
    mensaje_exito = "Registramos el reclamo. Quedó pendiente."

    def get(self, request, *args, **kwargs):
        """Prepara el catálogo antes de mostrar el formulario.

        Args:
            request: Petición HTTP autenticada.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Formulario de alta.
        """
        asegurar_catalogo_reclamos()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Prepara el catálogo antes de validar el alta.

        Args:
            request: Petición HTTP autenticada.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Redirección al detalle o el formulario con errores.
        """
        asegurar_catalogo_reclamos()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega el mapa y marca el formulario como alta.

        Args:
            **kwargs: Contexto adicional de la vista genérica.

        Returns:
            dict: Contexto de la plantilla.
        """
        contexto = super().get_context_data(**kwargs)
        contexto["es_alta"] = True
        return _completar_mapa(contexto)

    def form_valid(self, form):
        """Deja el reclamo pendiente, con ticket correlativo y aviso al titular.

        Args:
            form: Formulario ya validado.

        Returns:
            HttpResponse: Redirección al detalle, o el formulario si no se guardó.
        """
        reclamo = form.save(commit=False)
        reclamo.estado = obtener_estado(ESTADO_PENDIENTE)
        reclamo.prioridad = prioridad_inicial()
        reclamo.fecha_hora = timezone.now()
        guardado = _guardar_reclamo(form, self.request.user, reclamo)
        if guardado is None:
            return self.form_invalid(form)
        self.object = guardado
        messages.success(
            self.request,
            f"Registramos el reclamo {guardado.num_reclamo}. Quedó pendiente.",
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        """Vuelve al detalle del reclamo recién creado.

        Returns:
            str: Ruta del detalle.
        """
        return reverse("reclamos_app:reclamo_detalle", kwargs={"pk": self.object.pk})


class ReclamoDetalle(LoginRequiredMixin, DetailView):
    """Ficha del reclamo, su reconsideración y el seguimiento."""

    model = Reclamo
    template_name = "reclamos_app/reclamos/detalle.html"
    context_object_name = "reclamo"

    def get_queryset(self):
        """Limita el detalle a los reclamos visibles para quien consulta.

        Returns:
            QuerySet: Reclamos con sus notas precargadas.
        """
        return reclamos_visibles(self.request.user).prefetch_related("notas")

    def get_context_data(self, **kwargs):
        """Informa qué acciones puede hacer el usuario sobre este reclamo.

        Args:
            **kwargs: Contexto adicional de la vista genérica.

        Returns:
            dict: Contexto de la ficha.
        """
        contexto = super().get_context_data(**kwargs)
        reclamo = self.object
        try:
            reconsideracion = reclamo.reconsideracion
        except ObjectDoesNotExist:
            reconsideracion = None
        contexto["reconsideracion"] = reconsideracion
        contexto["puede_editar"] = reclamo.puede_editar(self.request.user)
        contexto["admite_reconsideracion"] = reclamo.admite_reconsideracion()
        contexto["puede_resolver"] = (
            self.request.user.es_gestor
            and reconsideracion is not None
            and not reclamo.notas.exists()
        )
        return contexto


class ReclamoEditar(FormularioUsuarioMixin, UpdateView):
    """Impide modificar un reclamo que ya fue enviado."""

    model = Reclamo
    form_class = ReclamoForm
    template_name = "reclamos_app/reclamos/crear_reclamo.html"
    titulo = "Editar reclamo"
    icono = "bi-droplet"
    bajada = "Un reclamo enviado no se puede modificar."
    mensaje_exito = "Actualizamos los datos del reclamo."

    def get_queryset(self):
        """Impide editar el reclamo de otra persona.

        Returns:
            QuerySet: Reclamos visibles para el usuario.
        """
        return reclamos_visibles(self.request.user)

    def _bloquear_si_no_edita(self):
        """Redirige porque un reclamo enviado no se modifica.

        Returns:
            HttpResponse | None: Redirección al detalle, o None si se pudiera editar.
        """
        reclamo = self.get_object()
        if reclamo.puede_editar(self.request.user):
            return None
        messages.error(
            self.request,
            "Un reclamo enviado no se puede modificar. Podés ver el detalle.",
        )
        return redirect("reclamos_app:reclamo_detalle", pk=reclamo.pk)

    def get(self, request, *args, **kwargs):
        """Muestra el formulario solo si el reclamo sigue pendiente.

        Args:
            request: Petición HTTP autenticada.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Formulario o redirección al detalle.
        """
        bloqueo = self._bloquear_si_no_edita()
        if bloqueo is not None:
            return bloqueo
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Guarda la corrección solo si el reclamo sigue pendiente.

        Args:
            request: Petición HTTP autenticada.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Redirección al detalle o el formulario con errores.
        """
        bloqueo = self._bloquear_si_no_edita()
        if bloqueo is not None:
            return bloqueo
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega el mapa centrado en el punto ya guardado.

        Args:
            **kwargs: Contexto adicional de la vista genérica.

        Returns:
            dict: Contexto de la plantilla.
        """
        contexto = super().get_context_data(**kwargs)
        contexto["es_alta"] = False
        return _completar_mapa(contexto, self.object)

    def form_valid(self, form):
        """Actualiza la modalidad y, si corresponde, la foto.

        Args:
            form: Formulario ya validado.

        Returns:
            HttpResponse: Redirección al detalle, o el formulario si no se guardó.
        """
        reclamo = form.save(commit=False)
        guardado = _guardar_reclamo(form, self.request.user, reclamo)
        if guardado is None:
            return self.form_invalid(form)
        self.object = guardado
        messages.success(self.request, self.mensaje_exito)
        return redirect(self.get_success_url())

    def get_url_volver(self):
        """Vuelve a la ficha del reclamo.

        Returns:
            str: Ruta del detalle.
        """
        return reverse("reclamos_app:reclamo_detalle", kwargs={"pk": self.object.pk})

    def get_success_url(self):
        """Vuelve a la ficha después de guardar.

        Returns:
            str: Ruta del detalle.
        """
        return self.get_url_volver()


class ReclamoGestionar(GestorRequeridoMixin, FormularioUsuarioMixin, UpdateView):
    """Cambio de estado, prioridad y funcionario responsable."""

    model = Reclamo
    form_class = GestionReclamoForm
    titulo = "Gestionar reclamo"
    icono = "bi-clipboard-check"
    bajada = (
        "Asigná un responsable y actualizá el estado. "
        "Un funcionario no puede tener más de 5 reclamos activos."
    )
    mensaje_exito = "Actualizamos la gestión del reclamo."

    def get_queryset(self):
        """Toma cualquier reclamo, porque la vista ya exige administrador.

        Returns:
            QuerySet: Reclamos visibles para el administrador.
        """
        return reclamos_visibles(self.request.user)

    def get_url_volver(self):
        """Vuelve a la ficha del reclamo.

        Returns:
            str: Ruta del detalle.
        """
        return reverse("reclamos_app:reclamo_detalle", kwargs={"pk": self.object.pk})

    def get_success_url(self):
        """Vuelve a la ficha después de guardar la gestión.

        Returns:
            str: Ruta del detalle.
        """
        return self.get_url_volver()


class _ReclamoRelacionadoMixin(FormularioUsuarioMixin):
    """Formulario colgado de un reclamo visible para el usuario."""

    def dispatch(self, request, *args, **kwargs):
        """Carga el reclamo o responde 404 si no corresponde verlo.

        Args:
            request: Petición HTTP.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre, incluido `pk` del reclamo.

        Returns:
            HttpResponse: La vista o la redirección de autenticación.
        """
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.reclamo = get_object_or_404(
            reclamos_visibles(request.user),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_url_volver(self):
        """Vuelve a la ficha del reclamo.

        Returns:
            str: Ruta del detalle.
        """
        return reverse("reclamos_app:reclamo_detalle", kwargs={"pk": self.reclamo.pk})


class ReconsideracionCrear(_ReclamoRelacionadoMixin, CreateView):
    """Pedido de revisión de un reclamo resuelto o rechazado."""

    model = Reconsideracion
    form_class = ReconsideracionForm
    titulo = "Pedir reconsideración"
    icono = "bi-arrow-repeat"
    bajada = (
        "Pedí que la Junta revise el cierre del reclamo. "
        "Cada reclamo admite una sola reconsideración."
    )
    mensaje_exito = "Recibimos tu pedido de reconsideración."

    def _bloquear_si_no_admite(self):
        """Impide el pedido cuando el reclamo no está en condiciones.

        Returns:
            HttpResponse | None: Redirección al detalle, o None si se puede pedir.
        """
        if self.reclamo.admite_reconsideracion():
            return None
        messages.error(
            self.request,
            "Este reclamo no admite una reconsideración en este momento.",
        )
        return redirect("reclamos_app:reclamo_detalle", pk=self.reclamo.pk)

    def get(self, request, *args, **kwargs):
        """Muestra el pedido solo si el reclamo admite reconsideración.

        Args:
            request: Petición HTTP autenticada.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Formulario o redirección al detalle.
        """
        bloqueo = self._bloquear_si_no_admite()
        if bloqueo is not None:
            return bloqueo
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Registra el pedido si el reclamo todavía lo admite.

        Args:
            request: Petición HTTP autenticada.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Redirección al detalle o el formulario con errores.
        """
        bloqueo = self._bloquear_si_no_admite()
        if bloqueo is not None:
            return bloqueo
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Pasa el reclamo para validar que admita el pedido.

        Returns:
            dict: Argumentos del formulario.
        """
        kwargs = super().get_form_kwargs()
        kwargs["reclamo"] = self.reclamo
        return kwargs

    def form_valid(self, form):
        """Vincula el descargo al titular y al reclamo.

        Args:
            form: Formulario ya validado.

        Returns:
            HttpResponse: Redirección al detalle, o el formulario si hubo conflicto.
        """
        form.instance.reclamo = self.reclamo
        form.instance.usuario = self.request.user
        form.instance.prioridad = self.reclamo.prioridad
        try:
            self.object = form.save()
        except IntegrityError:
            logger.warning(
                "No se guardó una segunda reconsideración del reclamo %s.",
                self.reclamo.pk,
            )
            messages.error(self.request, "Este reclamo ya tiene una reconsideración.")
            return redirect("reclamos_app:reclamo_detalle", pk=self.reclamo.pk)
        messages.success(self.request, self.mensaje_exito)
        return redirect(self.get_success_url())

    def get_success_url(self):
        """Vuelve a la ficha del reclamo.

        Returns:
            str: Ruta del detalle.
        """
        return self.get_url_volver()


class ReconsideracionResolver(GestorRequeridoMixin, FormularioUsuarioMixin, FormView):
    """Reabre el reclamo o mantiene el cierre, y deja la respuesta en seguimiento."""

    form_class = ResolverReconsideracionForm
    titulo = "Resolver reconsideración"
    icono = "bi-arrow-repeat"
    bajada = "Si la reabrís, el reclamo vuelve a estar en proceso."

    def dispatch(self, request, *args, **kwargs):
        """Carga el pedido antes de mostrar el formulario.

        Args:
            request: Petición HTTP.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre, incluido `pk` del pedido.

        Returns:
            HttpResponse: La vista, o la redirección si no corresponde.
        """
        if request.user.is_authenticated and request.user.es_gestor:
            self.reconsideracion = get_object_or_404(
                Reconsideracion.objects.select_related("reclamo", "reclamo__estado"),
                pk=kwargs["pk"],
            )
        return super().dispatch(request, *args, **kwargs)

    def _bloquear_si_respondida(self):
        """Impide responder dos veces el mismo pedido.

        Returns:
            HttpResponse | None: Redirección al detalle, o None si sigue abierto.
        """
        if not self.reconsideracion.reclamo.notas.exists():
            return None
        messages.error(self.request, "Esta reconsideración ya fue respondida.")
        return redirect(
            "reclamos_app:reclamo_detalle",
            pk=self.reconsideracion.reclamo_id,
        )

    def get(self, request, *args, **kwargs):
        """Muestra la respuesta solo si el pedido sigue sin seguimiento.

        Args:
            request: Petición HTTP de un administrador.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Formulario o redirección al detalle.
        """
        bloqueo = self._bloquear_si_respondida()
        if bloqueo is not None:
            return bloqueo
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Guarda la respuesta solo si el pedido sigue sin seguimiento.

        Args:
            request: Petición HTTP de un administrador.
            *args: Argumentos posicionales de la vista.
            **kwargs: Argumentos con nombre de la vista.

        Returns:
            HttpResponse: Redirección al detalle o el formulario con errores.
        """
        bloqueo = self._bloquear_si_respondida()
        if bloqueo is not None:
            return bloqueo
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Deja la respuesta en la bitácora y, si corresponde, reabre el caso.

        Args:
            form: Formulario ya validado.

        Returns:
            HttpResponse: Redirección al detalle del reclamo.
        """
        reclamo = self.reconsideracion.reclamo
        Bitacora.objects.create(
            reclamo=reclamo,
            comentario=form.cleaned_data["respuesta"],
            fecha_comentario=timezone.localdate(),
        )
        if form.cleaned_data["reabrir"]:
            reclamo.estado = obtener_estado(ESTADO_EN_PROCESO)
            reclamo.save(update_fields=["estado"])
            logger.info(
                "Se reabrió el reclamo %s por la reconsideración %s.",
                reclamo.pk,
                self.reconsideracion.pk,
            )
            messages.success(
                self.request,
                "Reconsideración aceptada. El reclamo volvió a estar en proceso.",
            )
        else:
            logger.info(
                "Se mantuvo el cierre del reclamo %s tras la reconsideración %s.",
                reclamo.pk,
                self.reconsideracion.pk,
            )
            messages.success(
                self.request,
                "Registramos la respuesta y el reclamo sigue cerrado.",
            )
        return redirect(self.get_success_url())

    def get_url_volver(self):
        """Vuelve a la ficha del reclamo.

        Returns:
            str: Ruta del detalle.
        """
        return reverse(
            "reclamos_app:reclamo_detalle",
            kwargs={"pk": self.reconsideracion.reclamo_id},
        )

    def get_success_url(self):
        """Vuelve a la ficha después de responder.

        Returns:
            str: Ruta del detalle.
        """
        return self.get_url_volver()
