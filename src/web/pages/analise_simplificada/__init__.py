"""
Pacote para análise simplificada modular de turbinas eólicas.

Este pacote contém módulos organizados para:
- Processamento de dados meteorológicos
- Cálculos de perfil de vento
- Visualização e exibição de resultados
- Configurações e constantes
"""

__version__ = "1.0.0"
__author__ = "Wind Turbine Modeling System"

# Imports principais para facilitar uso do pacote
from .config import *
from .data_processor import *
from .wind_profile import *
from .display_utils import *