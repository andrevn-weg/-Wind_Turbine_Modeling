"""
Módulo de análise de turbinas eólicas

Contém as subpáginas para análise completa de turbinas eólicas:
- initial_parameters: Configuração de parâmetros iniciais
- wind_profile_analysis: Análise de perfil vertical do vento
- wind_components_analysis: Simulação de componentes do vento
- turbine_simulation: Simulação de performance de turbinas
- results_reports: Resultados e relatórios finais
"""

from .initial_parameters import render_initial_parameters_tab
from .wind_profile_analysis import render_wind_profile_tab
from .wind_components_analysis import render_wind_components_tab
from .turbine_simulation import render_turbine_simulation_tab
from .results_reports import render_results_reports_tab

__all__ = [
    'render_initial_parameters_tab',
    'render_wind_profile_tab', 
    'render_wind_components_tab',
    'render_turbine_simulation_tab',
    'render_results_reports_tab'
]
