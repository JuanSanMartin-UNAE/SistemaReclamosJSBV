"""Formularios de reclamos y reconsideraciones."""

import logging
from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.models.functions import Upper

from .constantes_reclamo import (
    CATEGORIAS_FORMULARIO,
    ESTADOS_CERRADOS,
    EXTENSIONES_FOTO,
    TAMANO_MAXIMO_FOTO,
)
from .forms import EstiloBootstrapMixin
from .models import (
    ClasificacionReclamo,
    Funcionario,
    Prioridad,
    Reclamo,
    Reconsideracion,
    TipoReclamo,
)
from .reglas import coordenadas_en_bella_vista, cupo_disponible, tope_funcionario

logger = logging.getLogger(__name__)

LARGO_MINIMO_DESCRIPCION = 15
LARGO_MINIMO_DESCARGO = 20


class TipoReclamoSelect(forms.Select):
    """Desplegable de tipos_reclamos con la clasificación de cada opción."""

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        """Marca cada tipo con el id de su clasificación.

        Args:
            name: Nombre del campo.
            value: Valor de la opción.
            label: Texto visible.
            selected: Si la opción queda elegida.
            index: Índice de la opción.
            subindex: Índice interno del grupo.
            attrs: Atributos extra de la opción.

        Returns:
            dict: Opción lista para renderizar.
        """
        opcion = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        instancia = getattr(value, "instance", None)
        if instancia is not None:
            opcion["attrs"]["data-clase"] = instancia.clase_reclamo_id
        return opcion


class ReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un reclamo domiciliario o de la vía pública."""

    categoria = forms.ModelChoiceField(
        label="Categoría",
        queryset=ClasificacionReclamo.objects.none(),
        help_text="Elegí la categoría y después el tipo de anomalía.",
    )
    numero_medidor = forms.CharField(
        label="Número de medidor o cuenta",
        max_length=4,
        required=False,
        help_text=("Obligatorio si el reclamo es de tu conexión. Máximo 4 caracteres."),
    )
    foto = forms.FileField(
        label="Foto de evidencia",
        required=False,
        help_text="Opcional. Una imagen JPG, PNG o WEBP de hasta 5 MB.",
    )

    class Meta:
        """Campos del reclamo que completa el usuario."""

        model = Reclamo
        fields = [
            "tipo",
            "barrio",
            "posee_conexion",
            "descripcion",
            "latitud",
            "longitud",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "tipo": TipoReclamoSelect(),
        }
        labels = {
            "tipo": "Tipo de anomalía",
            "barrio": "Barrio habilitado",
            "posee_conexion": "El reclamo es de mi conexión domiciliaria",
            "latitud": "Latitud",
            "longitud": "Longitud",
        }
        help_texts = {
            "posee_conexion": (
                "Si el problema está en la vía pública, dejá esta opción "
                "sin marcar e indicá el punto en el mapa."
            ),
            "descripcion": "Describí el problema con al menos 15 caracteres.",
            "latitud": "Obligatoria en la vía pública, dentro de Bella Vista.",
            "longitud": "Obligatoria en la vía pública, dentro de Bella Vista.",
        }

    def __init__(self, *args, **kwargs):
        """Prepara la categoría y el medidor según el reclamo guardado.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        categorias = ClasificacionReclamo.objects.filter(
            nombre__in=CATEGORIAS_FORMULARIO
        )
        tipos = TipoReclamo.objects.annotate(reclamo_mayuscula=Upper("reclamo")).filter(
            reclamo=F("reclamo_mayuscula"),
            clase_reclamo__nombre__in=CATEGORIAS_FORMULARIO,
        )
        if self.instance.pk and self.instance.tipo_id:
            categorias = categorias | ClasificacionReclamo.objects.filter(
                pk=self.instance.tipo.clase_reclamo_id
            )
            tipos = TipoReclamo.objects.filter(
                pk__in=list(tipos.values_list("pk", flat=True))
                + [self.instance.tipo_id]
            )
        self.fields["categoria"].queryset = categorias.order_by("nombre")
        self.fields["tipo"].queryset = tipos.order_by("reclamo")
        self.fields["latitud"].required = False
        self.fields["longitud"].required = False
        self.fields["posee_conexion"].required = False
        if self.instance.pk and self.instance.tipo_id:
            self.fields["categoria"].initial = self.instance.tipo.clase_reclamo_id
        if (
            self.instance.pk
            and self.instance.posee_conexion
            and self.instance.conexion_id
        ):
            self.fields["numero_medidor"].initial = (
                self.instance.conexion.numero_medidor
            )
        self.order_fields(
            [
                "categoria",
                "tipo",
                "barrio",
                "posee_conexion",
                "numero_medidor",
                "descripcion",
                "latitud",
                "longitud",
                "foto",
            ]
        )

    def clean_descripcion(self):
        """Exige un relato suficiente del problema.

        Returns:
            str: Descripción sin espacios sobrantes.

        Raises:
            ValidationError: Si el texto es demasiado corto.
        """
        descripcion = (self.cleaned_data.get("descripcion") or "").strip()
        if len(descripcion) < LARGO_MINIMO_DESCRIPCION:
            raise ValidationError(
                "Describí el problema con al menos "
                f"{LARGO_MINIMO_DESCRIPCION} caracteres."
            )
        return descripcion

    def clean_numero_medidor(self):
        """Normaliza el número de medidor.

        Returns:
            str: Medidor sin espacios sobrantes.
        """
        return (self.cleaned_data.get("numero_medidor") or "").strip()

    def clean_foto(self):
        """Acepta solo imágenes livianas.

        Returns:
            UploadedFile | None: Archivo válido, o None.

        Raises:
            ValidationError: Si el formato o el tamaño no sirven.
        """
        foto = self.cleaned_data.get("foto")
        if not foto:
            return foto
        extension = Path(foto.name).suffix.lower()
        if extension not in EXTENSIONES_FOTO:
            logger.info("Se rechazó una evidencia con extensión %s.", extension)
            raise ValidationError("La foto tiene que ser JPG, PNG o WEBP.")
        if foto.size > TAMANO_MAXIMO_FOTO:
            logger.info("Se rechazó una evidencia de %s bytes.", foto.size)
            raise ValidationError("La foto no puede superar los 5 MB.")
        return foto

    def clean(self):
        """Exige el medidor o el punto del mapa según la modalidad.

        Returns:
            dict: Datos limpios del formulario.
        """
        datos = super().clean()
        categoria = datos.get("categoria")
        tipo = datos.get("tipo")
        if categoria and tipo and tipo.clase_reclamo_id != categoria.pk:
            self.add_error(
                "tipo",
                "Elegí un tipo que pertenezca a la categoría.",
            )
        if datos.get("posee_conexion"):
            datos["latitud"] = None
            datos["longitud"] = None
            if not datos.get("numero_medidor"):
                self.add_error(
                    "numero_medidor",
                    "Indicá el número de medidor o cuenta.",
                )
            return datos
        latitud = datos.get("latitud")
        longitud = datos.get("longitud")
        if latitud is None or longitud is None:
            self.add_error(
                "latitud",
                "Indicá el punto del reclamo en el mapa.",
            )
            if longitud is None:
                self.add_error("longitud", "Indicá la longitud.")
            return datos
        if not coordenadas_en_bella_vista(latitud, longitud):
            self.add_error(
                "latitud",
                "El punto tiene que estar dentro del distrito de Bella Vista.",
            )
        return datos


class ReconsideracionForm(EstiloBootstrapMixin, forms.ModelForm):
    """Pedido del titular para revisar un reclamo cerrado."""

    class Meta:
        """Campo que completa el usuario."""

        model = Reconsideracion
        fields = ["descargo"]
        widgets = {"descargo": forms.Textarea(attrs={"rows": 4})}
        labels = {"descargo": "Descargo"}
        help_texts = {
            "descargo": "Explicá por qué la respuesta de la Junta no resuelve el caso.",
        }

    def __init__(self, *args, reclamo=None, **kwargs):
        """Guarda el reclamo que se quiere reconsiderar.

        Args:
            *args: Argumentos del formulario.
            reclamo: Reclamo cerrado.
            **kwargs: Argumentos con nombre del formulario.
        """
        self.reclamo = reclamo
        super().__init__(*args, **kwargs)

    def clean_descargo(self):
        """Exige un fundamento mínimo para abrir la reconsideración.

        Returns:
            str: Descargo sin espacios sobrantes.

        Raises:
            ValidationError: Si el texto es demasiado corto.
        """
        descargo = (self.cleaned_data.get("descargo") or "").strip()
        if len(descargo) < LARGO_MINIMO_DESCARGO:
            raise ValidationError(
                "Contá con más detalle por qué pedís la reconsideración "
                f"(mínimo {LARGO_MINIMO_DESCARGO} caracteres)."
            )
        return descargo

    def clean(self):
        """Impide un segundo pedido o uno sobre un reclamo todavía abierto.

        Returns:
            dict: Datos limpios del formulario.
        """
        datos = super().clean()
        if self.reclamo is not None and not self.reclamo.admite_reconsideracion():
            logger.info(
                "Se rechazó la reconsideración del reclamo %s.",
                self.reclamo.pk,
            )
            raise ValidationError(
                "Este reclamo no admite una reconsideración en este momento."
            )
        return datos


class GestionReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Actualización de estado, prioridad y funcionario a cargo."""

    class Meta:
        """Campos de gestión interna."""

        model = Reclamo
        fields = ["estado", "prioridad", "funcionario"]

    def __init__(self, *args, **kwargs):
        """Hace opcional al funcionario y obliga a elegir una prioridad.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["prioridad"].required = True
        self.fields["prioridad"].queryset = Prioridad.objects.all()
        self.fields["funcionario"].required = False
        self.fields["funcionario"].queryset = Funcionario.objects.select_related(
            "cargo"
        )

    def clean(self):
        """Respeta el máximo de reclamos activos por funcionario.

        Returns:
            dict: Datos limpios del formulario.
        """
        datos = super().clean()
        funcionario = datos.get("funcionario")
        estado = datos.get("estado")
        if funcionario is None or estado is None:
            return datos
        cerrados = {nombre.casefold() for nombre in ESTADOS_CERRADOS}
        if estado.nombre_estado.casefold() in cerrados:
            return datos
        if cupo_disponible(funcionario, excluir_pk=self.instance.pk):
            return datos
        tope = tope_funcionario(funcionario)
        logger.info(
            "No se asignó el reclamo %s al funcionario %s: cupo de %s agotado.",
            self.instance.pk,
            funcionario.pk,
            tope,
        )
        self.add_error(
            "funcionario",
            f"Ese funcionario ya alcanzó el máximo de {tope} reclamos activos.",
        )
        return datos


class ResolverReconsideracionForm(EstiloBootstrapMixin, forms.Form):
    """Respuesta de la Junta: reabrir el caso o mantener el cierre."""

    reabrir = forms.BooleanField(
        label="Reabrir el reclamo",
        required=False,
        help_text="Si la marcás, el reclamo vuelve a estar en proceso.",
    )
    respuesta = forms.CharField(
        label="Respuesta",
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Queda en el seguimiento del reclamo.",
    )

    def clean_respuesta(self):
        """Normaliza el fundamento de la Junta.

        Returns:
            str: Respuesta sin espacios sobrantes.

        Raises:
            ValidationError: Si la respuesta está vacía.
        """
        respuesta = (self.cleaned_data.get("respuesta") or "").strip()
        if not respuesta:
            raise ValidationError("Escribí el fundamento de la resolución.")
        return respuesta
