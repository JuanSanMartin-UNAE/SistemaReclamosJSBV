from django.urls import reverse_lazy
from django.views.generic import ListView

from ..forms import BarrioForm
from ..models import Barrio
from .base import CrearView, EditarView, EliminarView


class BarrioLista(ListView):
    model = Barrio
    template_name = 'reclamos_app/barrios/lista.html'
    context_object_name = 'barrios'
    paginate_by = 20


class BarrioCrear(CrearView):
    model = Barrio
    form_class = BarrioForm
    titulo = 'Nuevo barrio'
    success_url = reverse_lazy('reclamos_app:barrio_lista')


class BarrioEditar(EditarView):
    model = Barrio
    form_class = BarrioForm
    titulo = 'Editar barrio'
    success_url = reverse_lazy('reclamos_app:barrio_lista')


class BarrioEliminar(EliminarView):
    model = Barrio
    success_url = reverse_lazy('reclamos_app:barrio_lista')
