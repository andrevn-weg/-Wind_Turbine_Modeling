"""
Módulo Meteorológico - Sistema de Simulação de Turbinas Eólicas

Este módulo implementa funcionalidades para gerenciamento de dados meteorológicos,
incluindo fontes de dados, medições meteorológicas e APIs externas.

Submodules:
    meteorological_data_source: Entidades e repositórios para fontes de dados
    meteorological_data: Entidades e repositórios para dados meteorológicos
    api: Clientes para APIs meteorológicas externas (Open-Meteo, NASA POWER)

Arquitetura:
    - Separação clara entre entidades (models) e repositórios (data access)
    - Padrão Repository para abstração de dados
    - Validações de domínio nas entidades
    - Consultas relacionais avançadas nos repositórios
    - Clientes padronizados para APIs externas
"""

from .meteorological_data_source.entity import MeteorologicalDataSource
from .meteorological_data_source.repository import MeteorologicalDataSourceRepository
from .meteorological_data.entity import MeteorologicalData
from .meteorological_data.repository import MeteorologicalDataRepository

# APIs externas
from .api.open_meteo import OpenMeteoClient
from .api.nasa_power import NASAPowerClient

__all__ = [
    'MeteorologicalDataSource',
    'MeteorologicalDataSourceRepository',
    'MeteorologicalData',
    'MeteorologicalDataRepository',
    'OpenMeteoClient',
    'NASAPowerClient'
]
