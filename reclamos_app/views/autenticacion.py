from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from ..forms import IngresoForm, NuevaContrasenhaForm, RecuperarForm, RegistroForm

PLANTILLAS = 'reclamos_app/autenticacion/'


def bienvenida(request):
    if request.user.is_authenticated:
        return redirect('reclamos_app:panel')
    return render(request, 'reclamos_app/bienvenida.html')


class Ingresar(auth_views.LoginView):
    template_name = PLANTILLAS + 'ingresar.html'
    authentication_form = IngresoForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        if not form.cleaned_data.get('recordarme'):
            self.request.session.set_expiry(0)
        messages.success(self.request, f'¡Bienvenido/a, {self.request.user.get_short_name()}!')
        return respuesta


class Salir(auth_views.LogoutView):
    pass


class Registro(CreateView):
    template_name = PLANTILLAS + 'registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('reclamos_app:panel')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('reclamos_app:panel')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, '¡Su cuenta fue creada correctamente! Ya puede utilizar el sistema.')
        return respuesta


class Recuperar(auth_views.PasswordResetView):
    template_name = PLANTILLAS + 'recuperar.html'
    form_class = RecuperarForm
    email_template_name = PLANTILLAS + 'correo_recuperacion.txt'
    html_email_template_name = PLANTILLAS + 'correo_recuperacion.html'
    subject_template_name = PLANTILLAS + 'correo_recuperacion_asunto.txt'
    success_url = reverse_lazy('reclamos_app:recuperar_enviado')


class RecuperarEnviado(auth_views.PasswordResetDoneView):
    template_name = PLANTILLAS + 'recuperar_enviado.html'


class RecuperarConfirmar(auth_views.PasswordResetConfirmView):
    template_name = PLANTILLAS + 'recuperar_confirmar.html'
    form_class = NuevaContrasenhaForm
    success_url = reverse_lazy('reclamos_app:recuperar_completo')


class RecuperarCompleto(auth_views.PasswordResetCompleteView):
    template_name = PLANTILLAS + 'recuperar_completo.html'
