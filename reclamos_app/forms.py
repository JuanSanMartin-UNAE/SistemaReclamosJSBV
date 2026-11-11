from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import password_validators_help_text_html, validate_password
from django.core.exceptions import ValidationError

from .models import (
    Barrio, CargoFuncionario, ClasificacionReclamo, EstadoReclamo, Funcionario,
    Prioridad, Rol, TipoReclamo, Usuario,
)
from .models.usuario import obtener_rol_externo


class EstiloBootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(campo.widget, forms.Select):
                campo.widget.attrs.setdefault('class', 'form-select')
            else:
                campo.widget.attrs.setdefault('class', 'form-control')
                # form-floating de Bootstrap necesita un placeholder para posicionar la etiqueta
                campo.widget.attrs.setdefault('placeholder', campo.label or ' ')

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                widget = self.fields[nombre].widget
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} is-invalid".strip()


class IngresoForm(EstiloBootstrapMixin, AuthenticationForm):
    recordarme = forms.BooleanField(label='Recordarme', required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Número de documento'
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Número de documento', 'autocomplete': 'username', 'inputmode': 'text'}
        )
        self.fields['password'].label = 'Contraseña'
        self.fields['password'].widget.attrs['placeholder'] = 'Contraseña'


class RegistroForm(EstiloBootstrapMixin, forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = Usuario
        fields = ['num_documento', 'nombre', 'apellido', 'telefono', 'correo_electronico', 'barrio', 'direccion']
        widgets = {'direccion': forms.TextInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo_electronico'].required = True
        self.fields['correo_electronico'].help_text = 'Lo usaremos para recuperar su contraseña y enviarle avisos.'
        self.fields['barrio'].empty_label = 'Seleccione su barrio'

    def clean_correo_electronico(self):
        correo = self.cleaned_data['correo_electronico'].lower()
        if Usuario.objects.filter(correo_electronico__iexact=correo).exists():
            raise ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        return correo

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        """Guarda el ciudadano con la contraseña hasheada y el rol USUARIO EXTERNO.

        Args:
            commit: Si es False, devuelve la instancia sin persistirla.

        Returns:
            Usuario: Cuenta creada.
        """
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password1'])
        usuario.rol = obtener_rol_externo()
        if commit:
            usuario.save()
        return usuario


class RecuperarForm(EstiloBootstrapMixin, PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Correo electrónico'
        self.fields['email'].widget.attrs['placeholder'] = 'Correo electrónico'


class NuevaContrasenhaForm(EstiloBootstrapMixin, SetPasswordForm):
    pass


class BarrioForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Barrio
        fields = ['nombre_barrio', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class RolForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre_rol', 'fecha_alta', 'activo']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class CargoFuncionarioForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = CargoFuncionario
        fields = ['nombre_cargo', 'clase_reclamo_atiende', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clase_reclamo_atiende'].empty_label = 'Seleccione la clasificación'


class ClasificacionReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = ClasificacionReclamo
        fields = ['nombre', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class EstadoReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = EstadoReclamo
        fields = ['nombre_estado', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class FuncionarioForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nombre_apellido', 'cargo', 'cant_maxima_despachada', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cargo'].empty_label = 'Seleccione el cargo'


class PrioridadForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Prioridad
        fields = ['nombre_prioridad', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class TipoReclamoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = TipoReclamo
        fields = ['reclamo', 'clase_reclamo', 'plazo_dias', 'fecha_alta']
        widgets = {'fecha_alta': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clase_reclamo'].empty_label = 'Seleccione la clasificación'


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
    contrasenha_plana = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text='Al editar, déjela vacía para conservar la contraseña actual.',
    )

    class Meta:
        model = Usuario
        fields = [
            'num_documento', 'nombre', 'apellido', 'telefono',
            'correo_electronico', 'direccion', 'barrio', 'rol', 'is_active',
        ]
        widgets = {'direccion': forms.Textarea(attrs={'rows': 2})}

    def clean(self):
        datos = super().clean()
        contrasenha = datos.get('contrasenha_plana')
        if not self.instance.pk and not contrasenha:
            self.add_error('contrasenha_plana', 'La contraseña es obligatoria para usuarios nuevos.')
        elif contrasenha:
            try:
                validate_password(contrasenha, self.instance)
            except ValidationError as error:
                self.add_error('contrasenha_plana', error)
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get('contrasenha_plana'):
            usuario.set_password(self.cleaned_data['contrasenha_plana'])
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario


class UsuarioAdminForm(UsuarioForm):
    class Meta(UsuarioForm.Meta):
        fields = UsuarioForm.Meta.fields + ['is_staff', 'is_superuser', 'groups', 'user_permissions']
