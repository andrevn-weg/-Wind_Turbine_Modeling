"""
Inicialização do módulo de modelos climáticos.

Este módulo contém as entidades e estruturas de dados
para o sistema climático e eólico.
"""

from .entity import (
    DadosClimaticos,
    DadosEolicos,
    LocalizacaoClimatica,
    SerieTemporalVento
)

from .repository import (
    DadosClimaticosRepository,
    DadosEolicosRepository,
    LocalizacaoClimaticaRepository
)

__all__ = [
    'DadosClimaticos',
    'DadosEolicos', 
    'LocalizacaoClimatica',
    'SerieTemporalVento',
    'DadosClimaticosRepository',
    'DadosEolicosRepository',
    'LocalizacaoClimaticaRepository'
]
