from django.urls import reverse_lazy

from ..forms import CargoFuncionarioForm
from ..models import CargoFuncionario
from .base import CrearView, EditarView, EliminarView, ListaView


class CargoFuncionarioLista(ListaView):
    model = CargoFuncionario
    template_name = 'reclamos_app/cargos_funcionarios/lista.html'
    context_object_name = 'cargos'
    queryset = CargoFuncionario.objects.select_related('clase_reclamo_atiende')


class CargoFuncionarioCrear(CrearView):
    model = CargoFuncionario
    form_class = CargoFuncionarioForm
    titulo = 'Nuevo cargo'
    icono = 'bi-briefcase'
    success_url = reverse_lazy('reclamos_app:cargo_funcionario_lista')


class CargoFuncionarioEditar(EditarView):
    model = CargoFuncionario
    form_class = CargoFuncionarioForm
    titulo = 'Editar cargo'
    icono = 'bi-briefcase'
    success_url = reverse_lazy('reclamos_app:cargo_funcionario_lista')


class CargoFuncionarioEliminar(EliminarView):
    model = CargoFuncionario
    success_url = reverse_lazy('reclamos_app:cargo_funcionario_lista')
