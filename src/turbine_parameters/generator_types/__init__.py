"""
Módulo generator_types - Gerenciamento de entidades Tipo de Gerador

Este módulo contém:
- GeneratorType: Entidade de domínio representando um tipo de gerador eólico
- GeneratorTypeRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.turbine_parameters.generator_types import GeneratorType, GeneratorTypeRepository
    
    # Criar um novo tipo de gerador
    generator_type = GeneratorType(
        type="PMSG",
        description="Permanent Magnet Synchronous Generator - alta eficiência"
    )
    
    # Salvar no banco
    repo = GeneratorTypeRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    type_id = repo.salvar(generator_type)
    
    # Buscar tipo de gerador
    type_encontrado = repo.buscar_por_tipo("PMSG")
"""

from .entity import GeneratorType
from .repository import GeneratorTypeRepository

__all__ = ['GeneratorType', 'GeneratorTypeRepository']
