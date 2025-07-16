"""
Inicialização do módulo de APIs climáticas.

Este módulo contém clientes para diferentes APIs meteorológicas
para obtenção de dados climáticos e eólicos.
"""

from .open_meteo_client import (
    OpenMeteoClient,
    APIError,
    client,
    obter_dados_historicos_simples
)

__all__ = [
    'OpenMeteoClient',
    'APIError',
    'client',
    'obter_dados_historicos_simples'
]
