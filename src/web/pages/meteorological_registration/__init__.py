"""
Módulo de cadastro meteorológico

Contém as subpáginas para cadastro de dados meteorológicos:
- create_meteorological_data_source: Cadastro de fontes de dados
- create_meteorological_data: Cadastro de dados meteorológicos
"""

from .create_meteorological_data_source import create_meteorological_data_source
from .create_meteorological_data import create_meteorological_data

__all__ = [
    'create_meteorological_data_source',
    'create_meteorological_data'
]
