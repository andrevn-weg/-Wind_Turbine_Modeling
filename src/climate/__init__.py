"""
Módulo Climate - Sistema de Análise Climática e Eólica.

Este módulo fornece funcionalidades completas para coleta, armazenamento,
análise e processamento de dados climáticos e eólicos, incluindo:

- Coleta de dados de APIs meteorológicas (Open-Meteo)
- Armazenamento e recuperação de dados históricos
- Análise estatística e de tendências
- Cálculo de potencial eólico
- Processamento de séries temporais
- Gerenciamento de localizações climáticas

Exemplo de uso básico:
    >>> from climate import ColetaDadosService, AnaliseEolicaService
    >>> 
    >>> # Coleta dados históricos
    >>> coleta = ColetaDadosService()
    >>> dados = coleta.coletar_dados_historicos(-26.52, -49.06, "Jaraguá do Sul")
    >>> 
    >>> # Analisa dados coletados
    >>> analise = AnaliseEolicaService()
    >>> estatisticas = analise.calcular_estatisticas_completas(dados)
    >>> potencial = analise.calcular_potencial_eolico(dados)
"""

# Importações principais
from .models import (
    DadosClimaticos,
    DadosEolicos,
    LocalizacaoClimatica,
    SerieTemporalVento,
    DadosClimaticosRepository,
    DadosEolicosRepository,
    LocalizacaoClimaticaRepository
)

from .api import (
    OpenMeteoClient,
    APIError,
    client as api_client,
    obter_dados_historicos_simples
)

from .services import (
    AnaliseEolicaService,
    ProcessamentoSerieTemporalService,
    ColetaDadosService,
    GerenciamentoLocalizacoesService
)

# Instâncias globais para facilitar uso
analise_service = AnaliseEolicaService()
processamento_service = ProcessamentoSerieTemporalService()
coleta_service = ColetaDadosService()
gerenciamento_service = GerenciamentoLocalizacoesService()

# Metadados do módulo
__version__ = "1.0.0"
__author__ = "André Vinícius Lima do Nascimento"
__description__ = "Sistema de Análise Climática e Eólica"

# Exportações públicas
__all__ = [
    # Entidades
    'DadosClimaticos',
    'DadosEolicos',
    'LocalizacaoClimatica',
    'SerieTemporalVento',
    
    # Repositórios
    'DadosClimaticosRepository',
    'DadosEolicosRepository', 
    'LocalizacaoClimaticaRepository',
    
    # API
    'OpenMeteoClient',
    'APIError',
    'api_client',
    'obter_dados_historicos_simples',
    
    # Serviços
    'AnaliseEolicaService',
    'ProcessamentoSerieTemporalService',
    'ColetaDadosService',
    'GerenciamentoLocalizacoesService',
    
    # Instâncias globais
    'analise_service',
    'processamento_service',
    'coleta_service',
    'gerenciamento_service'
]


# Funções de conveniência para uso rápido
def obter_dados_historicos(latitude: float, longitude: float, 
                          nome_cidade: str = "", dias: int = 365) -> list:
    """
    Função de conveniência para obter dados históricos.
    
    Args:
        latitude: Latitude da localização
        longitude: Longitude da localização  
        nome_cidade: Nome da cidade (opcional)
        dias: Número de dias de histórico (padrão: 365)
    
    Returns:
        Lista de dados eólicos históricos
    
    Example:
        >>> dados = obter_dados_historicos(-26.52, -49.06, "Jaraguá do Sul")
        >>> print(f"Coletados {len(dados)} dias de dados")
    """
    return coleta_service.coletar_dados_historicos(
        latitude, longitude, nome_cidade, dias
    )


def analisar_potencial_eolico(dados: list, diametro_rotor: float = 15.0) -> dict:
    """
    Função de conveniência para análise de potencial eólico.
    
    Args:
        dados: Lista de dados eólicos
        diametro_rotor: Diâmetro do rotor em metros
    
    Returns:
        Dicionário com análise de potencial eólico
    
    Example:
        >>> dados = obter_dados_historicos(-26.52, -49.06)
        >>> potencial = analisar_potencial_eolico(dados, diametro_rotor=15)
        >>> print(f"Energia anual estimada: {potencial['energia_anual_estimada_kwh']:.2f} kWh")
    """
    return analise_service.calcular_potencial_eolico(dados, diametro_rotor)


def calcular_estatisticas(dados: list) -> dict:
    """
    Função de conveniência para cálculo de estatísticas.
    
    Args:
        dados: Lista de dados eólicos
    
    Returns:
        Dicionário com estatísticas completas
    
    Example:
        >>> dados = obter_dados_historicos(-26.52, -49.06)
        >>> stats = calcular_estatisticas(dados)
        >>> print(f"Velocidade média do vento: {stats['vento']['media']:.2f} m/s")
    """
    return analise_service.calcular_estatisticas_completas(dados)


def cadastrar_localizacao(nome: str, latitude: float, longitude: float,
                         coletar_dados: bool = True) -> object:
    """
    Função de conveniência para cadastrar nova localização.
    
    Args:
        nome: Nome da localização
        latitude: Latitude
        longitude: Longitude
        coletar_dados: Se deve coletar dados históricos automaticamente
    
    Returns:
        Objeto LocalizacaoClimatica criado
    
    Example:
        >>> loc = cadastrar_localizacao("Cachoeira do Sul", -30.04, -52.89)
        >>> print(f"Localização {loc.nome} cadastrada com sucesso")
    """
    return gerenciamento_service.cadastrar_localizacao(
        nome, latitude, longitude, coletar_dados=coletar_dados
    )


# Informações de ajuda
def help():
    """
    Exibe informações de ajuda sobre o módulo climate.
    """
    help_text = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    MÓDULO CLIMATE v1.0.0                    ║
    ║              Sistema de Análise Climática e Eólica          ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║ FUNÇÕES PRINCIPAIS:                                          ║
    ║                                                              ║
    ║ 🌍 obter_dados_historicos(lat, lon, nome, dias)             ║
    ║    → Coleta dados históricos de vento                       ║
    ║                                                              ║
    ║ ⚡ analisar_potencial_eolico(dados, diametro_rotor)         ║
    ║    → Calcula potencial energético                           ║
    ║                                                              ║
    ║ 📊 calcular_estatisticas(dados)                             ║
    ║    → Estatísticas completas de vento                        ║
    ║                                                              ║
    ║ 📍 cadastrar_localizacao(nome, lat, lon)                    ║
    ║    → Adiciona nova localização                              ║
    ║                                                              ║
    ║ EXEMPLO DE USO:                                              ║
    ║                                                              ║
    ║   import climate                                             ║
    ║                                                              ║
    ║   # Coleta dados de Jaraguá do Sul                          ║
    ║   dados = climate.obter_dados_historicos(                   ║
    ║       -26.52, -49.06, "Jaraguá do Sul", 365)               ║
    ║                                                              ║
    ║   # Analisa potencial eólico                                ║
    ║   potencial = climate.analisar_potencial_eolico(dados)      ║
    ║                                                              ║
    ║   # Exibe resultado                                          ║
    ║   print(f"Energia anual: {potencial['energia_anual']} kWh") ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(help_text)


# Configuração de logging (opcional)
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler para console se não houver nenhum configurado
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.info(f"Módulo climate v{__version__} carregado com sucesso")
