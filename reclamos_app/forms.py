"""Formularios de autenticación y de los catálogos del sistema."""

import logging

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
    validate_password,
)
from django.core.exceptions import ValidationError

from .models import (
    Barrio,
    CargoFuncionario,
    ClasificacionReclamo,
    EstadoReclamo,
    Funcionario,
    Prioridad,
    Rol,
    TipoReclamo,
    Usuario,
)

logger = logging.getLogger(__name__)


class EstiloBootstrapMixin:
    """Aplica las clases de Bootstrap 5 a los campos del formulario."""

    def __init__(self, *args, **kwargs):
        """Marca cada campo con la clase de Bootstrap que le corresponde.

        form-floating necesita un placeholder para posicionar la etiqueta.

        Args:
            *args: Argumentos del formulario de Django.
            **kwargs: Argumentos con nombre del formulario de Django.
        """
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(campo.widget, forms.Select):
                campo.widget.attrs.setdefault("class", "form-select")
            else:
                campo.widget.attrs.setdefault("class", "form-control")
                campo.widget.attrs.setdefault("placeholder", campo.label or " ")

    def full_clean(self):
        """Valida el formulario y marca con `is-invalid` los campos con error.

        Returns:
            None: Django guarda el resultado en `cleaned_data` y `errors`.
        """
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                widget = self.fields[nombre].widget
                clases = f"{widget.attrs.get('class', '')} is-invalid".strip()
                widget.attrs["class"] = clases


class IngresoForm(EstiloBootstrapMixin, AuthenticationForm):
    """Ingreso con número de documento y opción de recordar la sesión."""

    recordarme = forms.BooleanField(label="Recordarme", required=False, initial=True)

    def __init__(self, *args, **kwargs):
        """Traduce las etiquetas del formulario de autenticación de Django.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Número de documento"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Número de documento",
                "autocomplete": "username",
                "inputmode": "text",
            }
        )
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs["placeholder"] = "Contraseña"


class RegistroForm(EstiloBootstrapMixin, forms.ModelForm):
    """Registro público de una cuenta de usuario."""

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        """Campos editables del registro público."""

        model = Usuario
        fields = [
            "num_documento",
            "nombre",
            "apellido",
            "telefono",
            "correo_electronico",
            "barrio",
            "direccion",
        ]
        widgets = {"direccion": forms.TextInput()}

    def __init__(self, *args, **kwargs):
        """Exige correo y aclara el selector de barrio.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["correo_electronico"].required = True
        self.fields["correo_electronico"].help_text = (
            "Lo usaremos para recuperar su contraseña y enviarle avisos."
        )
        self.fields["barrio"].empty_label = "Seleccione su barrio"

    def clean_correo_electronico(self):
        """Rechaza un correo que ya pertenece a otra cuenta.

        Returns:
            str: Correo normalizado en minúsculas.

        Raises:
            ValidationError: Si el correo ya está registrado.
        """
        correo = self.cleaned_data["correo_electronico"].lower()
        if Usuario.objects.filter(correo_electronico__iexact=correo).exists():
            raise ValidationError(
                "Ya existe una cuenta registrada con este correo electrónico.",
            )
        return correo

    def clean_password2(self):
        """Comprueba que las dos contraseñas coincidan.

        Returns:
            str: Confirmación de la contraseña, si ambas coinciden.

        Raises:
            ValidationError: Si las contraseñas son distintas.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return password2

    def _post_clean(self):
        """Aplica los validadores de contraseña de Django al alta.

        Returns:
            None
        """
        super()._post_clean()
        password = self.cleaned_data.get("password2")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as error:
                logger.info("La contraseña del registro no cumple los validadores.")
                self.add_error("password2", error)

    def save(self, commit=True):
        """Guarda el usuario con la contraseña hasheada y el rol Usuario.

        Args:
            commit: Si es False, devuelve la instancia sin persistirla.

        Returns:
            Usuario: Cuenta creada.
        """
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password1"])
        usuario.rol = Rol.objects.filter(nombre_rol="Usuario").first()
        if commit:
            usuario.save()
        return usuario


class RecuperarForm(EstiloBootstrapMixin, PasswordResetForm):
    """Solicitud de recuperación de contraseña por correo."""

    def __init__(self, *args, **kwargs):
        """Traduce la etiqueta del correo.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Correo electrónico"
        self.fields["email"].widget.attrs["placeholder"] = "Correo electrónico"


class NuevaContrasenhaForm(EstiloBootstrapMixin, SetPasswordForm):
    """Elección de la nueva contraseña desde el enlace de recuperación."""


class BarrioForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un barrio."""

    class Meta:
        """Campos editables del barrio."""

        model = Barrio
        fields = ["nombre_barrio", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class RolForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un rol."""

    class Meta:
        """Campos editables del rol."""

        model = Rol
        fields = ["nombre_rol", "fecha_alta", "activo"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class CargoFuncionarioForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un cargo de funcionario."""

    class Meta:
        """Campos editables del cargo."""

        model = CargoFuncionario
        fields = ["nombre_cargo", "clase_reclamo_atiende", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        """Aclara el selector de clasificación.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["clase_reclamo_atiende"].empty_label = "Seleccione la clasificación"


class ClasificacionReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de una clasificación de reclamo."""

    class Meta:
        """Campos editables de la clasificación."""

        model = ClasificacionReclamo
        fields = ["nombre", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class EstadoReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un estado de reclamo."""

    class Meta:
        """Campos editables del estado."""

        model = EstadoReclamo
        fields = ["nombre_estado", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class FuncionarioForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un funcionario."""

    class Meta:
        """Campos editables del funcionario."""

        model = Funcionario
        fields = ["nombre_apellido", "cargo", "cant_maxima_despachada", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        """Aclara el selector de cargo.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["cargo"].empty_label = "Seleccione el cargo"


class PrioridadForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de una prioridad."""

    class Meta:
        """Campos editables de la prioridad."""

        model = Prioridad
        fields = ["nombre_prioridad", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class TipoReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un tipo de reclamo."""

    class Meta:
        """Campos editables del tipo de reclamo."""

        model = TipoReclamo
        fields = ["reclamo", "clase_reclamo", "plazo_dias", "fecha_alta"]
        widgets = {
            "fecha_alta": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        """Aclara el selector de clasificación.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["clase_reclamo"].empty_label = "Seleccione la clasificación"


class PerfilUsuarioForm(EstiloBootstrapMixin, forms.ModelForm):
    """Edición del perfil del usuario autenticado, sin cambiar el documento."""

    class Meta:
        """Datos que el titular puede actualizar."""

        model = Usuario
        fields = [
            "num_documento",
            "nombre",
            "apellido",
            "telefono",
            "correo_electronico",
            "barrio",
            "direccion",
        ]
        widgets = {"direccion": forms.TextInput()}

    def __init__(self, *args, **kwargs):
        """Bloquea el número de documento y exige el correo.

        Args:
            *args: Argumentos del formulario.
            **kwargs: Argumentos con nombre del formulario.
        """
        super().__init__(*args, **kwargs)
        self.fields["num_documento"].disabled = True
        self.fields["num_documento"].help_text = (
            "El número de documento no se puede modificar."
        )
        self.fields["correo_electronico"].required = True

    def clean_num_documento(self):
        """Conserva el documento guardado aunque el envío intente cambiarlo.

        Returns:
            str: Número de documento actual de la cuenta.
        """
        return self.instance.num_documento

    def clean_correo_electronico(self):
        """Rechaza un correo que ya usa otra cuenta.

        Returns:
            str: Correo normalizado en minúsculas.

        Raises:
            ValidationError: Si el correo pertenece a otro usuario.
        """
        correo = self.cleaned_data["correo_electronico"].lower()
        duplicado = Usuario.objects.filter(correo_electronico__iexact=correo).exclude(
            pk=self.instance.pk
        )
        if duplicado.exists():
            raise ValidationError(
                "Ya existe una cuenta registrada con este correo electrónico.",
            )
        return correo


class UsuarioForm(EstiloBootstrapMixin, forms.ModelForm):
    """Alta y edición de un usuario desde la administración."""

    contrasenha_plana = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Al editar, déjela vacía para conservar la contraseña actual.",
    )

    class Meta:
        """Campos editables del usuario."""

        model = Usuario
        fields = [
            "num_documento",
            "nombre",
            "apellido",
            "telefono",
            "correo_electronico",
            "direccion",
            "barrio",
            "rol",
            "is_active",
        ]
        widgets = {"direccion": forms.Textarea(attrs={"rows": 2})}

    def clean(self):
        """Exige contraseña en el alta y la valida cuando viene informada.

        Returns:
            dict: Datos limpios del formulario.
        """
        datos = super().clean()
        contrasenha = datos.get("contrasenha_plana")
        if not self.instance.pk and not contrasenha:
            self.add_error(
                "contrasenha_plana",
                "La contraseña es obligatoria para usuarios nuevos.",
            )
        elif contrasenha:
            try:
                validate_password(contrasenha, self.instance)
            except ValidationError as error:
                logger.info("La contraseña del usuario no cumple los validadores.")
                self.add_error("contrasenha_plana", error)
        return datos

    def save(self, commit=True):
        """Guarda el usuario y actualiza la contraseña solo si fue informada.

        Args:
            commit: Si es False, devuelve la instancia sin persistirla.

        Returns:
            Usuario: Instancia guardada o pendiente de guardar.
        """
        usuario = super().save(commit=False)
        if self.cleaned_data.get("contrasenha_plana"):
            usuario.set_password(self.cleaned_data["contrasenha_plana"])
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario


class UsuarioAdminForm(UsuarioForm):
    """Formulario del administrador de Django, con permisos de personal."""

    class Meta(UsuarioForm.Meta):
        """Agrega los campos de personal del sitio al formulario de usuario."""

        fields = UsuarioForm.Meta.fields + [
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        ]
