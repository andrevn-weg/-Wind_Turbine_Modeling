"""
Módulo control_types - Gerenciamento de entidades Tipo de Controle

Este módulo contém:
- ControlType: Entidade de domínio representando um tipo de controle de turbina eólica
- ControlTypeRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.turbine_parameters.control_types import ControlType, ControlTypeRepository
    
    # Criar um novo tipo de controle
    control_type = ControlType(
        type="Pitch",
        description="Controle ativo através do ângulo das pás"
    )
    
    # Salvar no banco
    repo = ControlTypeRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    type_id = repo.salvar(control_type)
    
    # Buscar tipo de controle
    type_encontrado = repo.buscar_por_tipo("Pitch")
"""

from .entity import ControlType
from .repository import ControlTypeRepository

__all__ = ['ControlType', 'ControlTypeRepository']
