"""
Inicialização do módulo de serviços climáticos.

Este módulo contém os serviços para processamento, análise
e gerenciamento de dados climáticos e eólicos.
"""

from .analise_service import (
    AnaliseEolicaService,
    ProcessamentoSerieTemporalService
)

from .coleta_service import (
    ColetaDadosService,
    GerenciamentoLocalizacoesService
)

__all__ = [
    'AnaliseEolicaService',
    'ProcessamentoSerieTemporalService',
    'ColetaDadosService',
    'GerenciamentoLocalizacoesService'
]
