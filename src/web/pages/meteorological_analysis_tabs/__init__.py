"""
Módulo para análises meteorológicas em tabs

Este módulo contém as funções especializadas para cada tipo de análise
meteorológica, organizadas por tabs na interface web.
"""

from .summary_tab import render_summary_tab
from .variation_graphs_tab import render_variation_graphs_tab
from .source_comparison_tab import render_source_comparison_tab
from .full_table_tab import render_full_table_tab
from .advanced_details_tab import render_advanced_details_tab

__all__ = [
    'render_summary_tab',
    'render_variation_graphs_tab', 
    'render_source_comparison_tab',
    'render_full_table_tab',
    'render_advanced_details_tab'
]
