"""
Módulo manufacturers - Gerenciamento de entidades Fabricante

Este módulo contém:
- Manufacturer: Entidade de domínio representando um fabricante de turbinas eólicas
- ManufacturerRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.turbine_parameters.manufacturers import Manufacturer, ManufacturerRepository
    
    # Criar um novo fabricante
    manufacturer = Manufacturer(
        name="Vestas Wind Systems",
        country="Denmark",
        official_website="https://www.vestas.com"
    )
    
    # Salvar no banco
    repo = ManufacturerRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    manufacturer_id = repo.salvar(manufacturer)
    
    # Buscar fabricante
    manufacturer_encontrado = repo.buscar_por_nome("Vestas Wind Systems")
"""

from .entity import Manufacturer
from .repository import ManufacturerRepository

__all__ = ['Manufacturer', 'ManufacturerRepository']
