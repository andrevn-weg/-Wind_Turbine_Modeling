"""
Módulo turbine_types - Gerenciamento de entidades Tipo de Turbina

Este módulo contém:
- TurbineType: Entidade de domínio representando um tipo de turbina eólica
- TurbineTypeRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.turbine_parameters.turbine_types import TurbineType, TurbineTypeRepository
    
    # Criar um novo tipo de turbina
    turbine_type = TurbineType(
        type="Horizontal",
        description="Turbinas de eixo horizontal - tipo mais comum"
    )
    
    # Salvar no banco
    repo = TurbineTypeRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    type_id = repo.salvar(turbine_type)
    
    # Buscar tipo de turbina
    type_encontrado = repo.buscar_por_tipo("Horizontal")
"""

from .entity import TurbineType
from .repository import TurbineTypeRepository

__all__ = ['TurbineType', 'TurbineTypeRepository']
