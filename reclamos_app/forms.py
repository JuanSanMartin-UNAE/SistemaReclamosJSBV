from django import forms

from .models import Barrio, Rol, Usuario


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


class UsuarioForm(EstiloBootstrapMixin, forms.ModelForm):
    contrasenha_plana = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        required=False,
        help_text='Al editar, déjela vacía para conservar la contraseña actual.',
    )

    class Meta:
        model = Usuario
        fields = [
            'num_documento', 'nombre', 'apellido', 'telefono',
            'correo_electronico', 'direccion', 'barrio', 'rol', 'activo',
        ]
        widgets = {'direccion': forms.Textarea(attrs={'rows': 2})}

    def clean(self):
        datos = super().clean()
        if not self.instance.pk and not datos.get('contrasenha_plana'):
            self.add_error('contrasenha_plana', 'La contraseña es obligatoria para usuarios nuevos.')
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get('contrasenha_plana'):
            usuario.set_contrasenha(self.cleaned_data['contrasenha_plana'])
        if commit:
            usuario.save()
        return usuario
