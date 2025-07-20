"""
Módulo Meteorológico - Sistema de Simulação de Turbinas Eólicas

Este módulo implementa funcionalidades para gerenciamento de dados meteorológicos,
incluindo fontes de dados e medições meteorológicas.

Submodules:
    meteorological_data_source: Entidades e repositórios para fontes de dados
    meteorological_data: Entidades e repositórios para dados meteorológicos

Arquitetura:
    - Separação clara entre entidades (models) e repositórios (data access)
    - Padrão Repository para abstração de dados
    - Validações de domínio nas entidades
    - Consultas relacionais avançadas nos repositórios
"""

from .meteorological_data_source.entity import MeteorologicalDataSource
from .meteorological_data_source.repository import MeteorologicalDataSourceRepository
from .meteorological_data.entity import MeteorologicalData
from .meteorological_data.repository import MeteorologicalDataRepository

__all__ = [
    'MeteorologicalDataSource',
    'MeteorologicalDataSourceRepository',
    'MeteorologicalData',
    'MeteorologicalDataRepository'
]
