from django.urls import reverse_lazy

from ..forms import FuncionarioForm
from ..models import Funcionario
from .base import CrearView, EditarView, EliminarView, ListaView


class FuncionarioLista(ListaView):
    model = Funcionario
    template_name = 'reclamos_app/funcionarios/lista.html'
    context_object_name = 'funcionarios'
    queryset = Funcionario.objects.select_related('cargo', 'cargo__clase_reclamo_atiende')


class FuncionarioCrear(CrearView):
    model = Funcionario
    form_class = FuncionarioForm
    titulo = 'Nuevo funcionario'
    icono = 'bi-person-gear'
    success_url = reverse_lazy('reclamos_app:funcionario_lista')


class FuncionarioEditar(EditarView):
    model = Funcionario
    form_class = FuncionarioForm
    titulo = 'Editar funcionario'
    icono = 'bi-person-gear'
    success_url = reverse_lazy('reclamos_app:funcionario_lista')


class FuncionarioEliminar(EliminarView):
    model = Funcionario
    success_url = reverse_lazy('reclamos_app:funcionario_lista')
