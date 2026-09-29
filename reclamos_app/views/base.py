from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import CreateView, DeleteView, UpdateView


class FormularioMixin:
    template_name = 'reclamos_app/comun/formulario.html'
    titulo = ''
    mensaje_exito = 'Registro guardado correctamente.'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = self.titulo
        contexto['url_volver'] = self.success_url
        return contexto

    def form_valid(self, form):
        messages.success(self.request, self.mensaje_exito)
        return super().form_valid(form)


class CrearView(FormularioMixin, CreateView):
    pass


class EditarView(FormularioMixin, UpdateView):
    pass


class EliminarView(DeleteView):
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
