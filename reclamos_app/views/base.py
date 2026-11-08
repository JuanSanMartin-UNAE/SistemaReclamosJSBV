from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView


class AdministradorRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.es_administrador

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'No tiene permisos para acceder a esa sección.')
            return redirect('reclamos_app:panel')
        return super().handle_no_permission()


class ListaView(AdministradorRequeridoMixin, ListView):
    paginate_by = 20


class FormularioMixin(AdministradorRequeridoMixin):
    template_name = 'reclamos_app/comun/formulario.html'
    titulo = ''
    icono = 'bi-pencil-square'
    mensaje_exito = 'Registro guardado correctamente.'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = self.titulo
        contexto['icono'] = self.icono
        contexto['url_volver'] = self.success_url
        return contexto

    def form_valid(self, form):
        messages.success(self.request, self.mensaje_exito)
        return super().form_valid(form)


class CrearView(FormularioMixin, CreateView):
    pass


class EditarView(FormularioMixin, UpdateView):
    pass


class EliminarView(AdministradorRequeridoMixin, DeleteView):
    template_name = 'reclamos_app/comun/confirmar_eliminar.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['url_volver'] = self.success_url
        return contexto

    def form_valid(self, form):
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, 'No se puede eliminar: hay registros que dependen de este.')
            return redirect(self.success_url)
        messages.success(self.request, 'Registro eliminado correctamente.')
        return respuesta
