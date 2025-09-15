"""
Configurações e constantes para a análise simplificada
"""

# Opções de fonte de dados para o selectbox
OPCOES_FONTE_DADOS = ["nasa_power", "openmeteo", "todos"]

# Mapeamento de nomes de fontes
MAPEAMENTO_FONTES = {
    'nasa_power': ['NASA_POWER', 'NASA POWER', 'nasa_power'],
    'openmeteo': ['OPEN_METEO', 'OPENMETEO', 'OPEN METEO', 'openmeteo']
}

# Configurações padrão para cálculos
CONFIGURACOES_PADRAO = {
    'altura_turbina': 80.0,
    'rugosidade_alpha': 0.20,
    'rugosidade_z0': 0.1,
    'metodo_perfil': 'power_law'
}

# Tipos de terreno e suas rugosidades
TIPOS_TERRENO = {
    'agua_aberta': {
        'nome': 'Água Aberta / Mar',
        'alpha': 0.10,
        'z0': 0.0002,
        'descricao': 'Superfícies de água calma, oceano'
    },
    'campo_aberto': {
        'nome': 'Campo Aberto',
        'alpha': 0.15,
        'z0': 0.01,
        'descricao': 'Pastagens, campos sem obstruções'
    },
    'rural_disperso': {
        'nome': 'Rural com Obstruções Esparsas',
        'alpha': 0.20,
        'z0': 0.1,
        'descricao': 'Áreas agrícolas com casas e árvores dispersas'
    },
    'suburban': {
        'nome': 'Suburbano / Florestal',
        'alpha': 0.25,
        'z0': 0.5,
        'descricao': 'Subúrbios, florestas densas'
    },
    'urbano': {
        'nome': 'Urbano',
        'alpha': 0.30,
        'z0': 1.0,
        'descricao': 'Cidades, muitos edifícios'
    },
    'muito_rugoso': {
        'nome': 'Muito Rugoso',
        'alpha': 0.35,
        'z0': 2.0,
        'descricao': 'Centros urbanos densos, arranha-céus'
    }
}

# Cores para gráficos por fonte
CORES_FONTES = {
    'NASA_POWER': '#1f77b4',  # Azul
    'OPEN_METEO': '#ff7f0e',  # Laranja
    'Nasa Power': '#1f77b4',
    'Open Meteo': '#ff7f0e'
}

# Configurações de exibição
FORMATO_DATA = '%d/%m/%Y'
FORMATO_DATETIME = '%d/%m/%Y %H:%M'

# Limites de validação
LIMITES_VALIDACAO = {
    'velocidade_min': 0.0,
    'velocidade_max': 50.0,  # m/s
    'altura_min': 1.0,
    'altura_max': 200.0,  # metros
    'alpha_min': 0.05,
    'alpha_max': 0.5,
    'z0_min': 0.0001,
    'z0_max': 10.0
}

# Mensagens de help
HELP_MESSAGES = {
    'altura_turbina': 'Altura do cubo da turbina eólica em metros (padrão: 80m)',
    'rugosidade_terreno': 'Tipo de terreno que afeta o perfil de vento',
    'metodo_perfil': 'Método matemático para extrapolação do perfil de vento',
    'fonte_dados': 'Fonte dos dados meteorológicos (NASA Power, OpenMeteo ou todos)',
    'periodo_analise': 'Período para análise dos dados meteorológicos'
}