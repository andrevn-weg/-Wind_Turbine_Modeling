"""
Módulo de APIs Meteorológicas

Este módulo contém clientes para diferentes APIs meteorológicas,
permitindo a obtenção de dados históricos de vento e outras variáveis meteorológicas.

APIs Implementadas:
    - Open-Meteo: Dados meteorológicos de código aberto
    - NASA POWER: Dados de energia solar e meteorológicos da NASA

Cada cliente implementa métodos específicos para sua API,
respeitando as limitações e características particulares de cada serviço.
"""

from .open_meteo import OpenMeteoClient
from .nasa_power import NASAPowerClient

__all__ = [
    'OpenMeteoClient',
    'NASAPowerClient'
]
