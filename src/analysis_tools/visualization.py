"""
Módulo de Visualização para Análises de Turbinas Eólicas

Este módulo implementa as funções de plotagem e visualização para:
- Perfis de vento
- Componentes do vento
- Performance de turbinas
- Análises comparativas

Utiliza Plotly para gráficos interativos compatíveis com Streamlit.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import streamlit as st

from .wind_profile import WindProfile
from .wind_components import WindComponents
from .turbine_performance import TurbinePerformance


class AnalysisVisualizer:
    """
    Classe para geração de visualizações das análises de turbinas eólicas.
    
    Todas as visualizações são otimizadas para exibição em Streamlit usando Plotly.
    """
    
    # Cores padrão para consistência visual
    COLORS = {
        'power_law': '#1f77b4',      # Azul
        'logarithmic': '#ff7f0e',    # Laranja
        'mean_wind': '#2ca02c',      # Verde
        'waves': '#d62728',          # Vermelho
        'turbulence': '#9467bd',     # Roxo
        'air_flow': '#8c564b',       # Marrom
        'power_curve': '#e377c2',    # Rosa
        'cp_curve': '#7f7f7f',       # Cinza
        'intersection': '#ffff00'     # Amarelo
    }
    
    def __init__(self):
        """Inicializa o visualizador."""
        pass
    
    def plot_wind_profile(self, profile: WindProfile, highlighted_points: Dict = None,
                         show_intersection: bool = True, height: int = 600) -> go.Figure:
        """
        Cria gráfico do perfil vertical de vento.
        
        Args:
            profile: Dados do perfil de vento
            highlighted_points: Pontos destacados (opcional)
            show_intersection: Se deve mostrar ponto de intersecção
            height: Altura do gráfico
        
        Returns:
            go.Figure: Figura do Plotly
        """
        fig = go.Figure()
        
        # Adicionar curva da Lei de Potência
        fig.add_trace(go.Scatter(
            x=profile.heights,
            y=profile.power_law_speeds,
            mode='lines',
            name='Lei de Potência',
            line=dict(color=self.COLORS['power_law'], width=3),
            hovertemplate='<b>Lei de Potência</b><br>' +
                         'Altura: %{x:.1f} m<br>' +
                         'Velocidade: %{y:.2f} m/s<extra></extra>'
        ))
        
        # Adicionar curva da Lei Logarítmica
        fig.add_trace(go.Scatter(
            x=profile.heights,
            y=profile.logarithmic_speeds,
            mode='lines',
            name='Lei Logarítmica',
            line=dict(color=self.COLORS['logarithmic'], width=3),
            hovertemplate='<b>Lei Logarítmica</b><br>' +
                         'Altura: %{x:.1f} m<br>' +
                         'Velocidade: %{y:.2f} m/s<extra></extra>'
        ))
        
        # Adicionar pontos destacados se fornecidos
        if highlighted_points:
            fig.add_trace(go.Scatter(
                x=highlighted_points['heights'],
                y=highlighted_points['power_law_speeds'],
                mode='markers',
                name='Pontos Lei de Potência',
                marker=dict(color=self.COLORS['power_law'], size=8),
                showlegend=False,
                hovertemplate='<b>Ponto Destacado</b><br>' +
                             'Altura: %{x:.0f} m<br>' +
                             'Velocidade (LP): %{y:.2f} m/s<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=highlighted_points['heights'],
                y=highlighted_points['logarithmic_speeds'],
                mode='markers',
                name='Pontos Lei Logarítmica',
                marker=dict(color=self.COLORS['logarithmic'], size=8),
                showlegend=False,
                hovertemplate='<b>Ponto Destacado</b><br>' +
                             'Altura: %{x:.0f} m<br>' +
                             'Velocidade (LL): %{y:.2f} m/s<extra></extra>'
            ))
        
        # Adicionar ponto de intersecção
        if show_intersection and profile.intersection_height and profile.intersection_speed:
            fig.add_trace(go.Scatter(
                x=[profile.intersection_height],
                y=[profile.intersection_speed],
                mode='markers',
                name=f'Intersecção ({profile.intersection_height:.1f}m, {profile.intersection_speed:.2f}m/s)',
                marker=dict(color=self.COLORS['intersection'], size=12, 
                           symbol='star', line=dict(color='black', width=2)),
                hovertemplate='<b>Intersecção</b><br>' +
                             'Altura: %{x:.1f} m<br>' +
                             'Velocidade: %{y:.2f} m/s<extra></extra>'
            ))
        
        # Configurar layout
        fig.update_layout(
            title=dict(
                text='Perfil Vertical de Vento: Lei de Potência vs Lei Logarítmica',
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title='Altura (m)',
            yaxis_title='Velocidade do Vento (m/s)',
            height=height,
            hovermode='closest',
            legend=dict(x=0.02, y=0.98),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
        )
        
        # Adicionar informações dos parâmetros como anotação
        fig.add_annotation(
            x=0.02, y=0.85,
            xref='paper', yref='paper',
            text=f'<b>Parâmetros:</b><br>' +
                 f'V<sub>ref</sub> = {profile.reference_speed:.1f} m/s<br>' +
                 f'H<sub>ref</sub> = {profile.reference_height:.0f} m<br>' +
                 f'n = {profile.power_law_coefficient:.2f}<br>' +
                 f'z<sub>0</sub> = {profile.roughness_length:.3f} m',
            showarrow=False,
            bgcolor='white',
            bordercolor='black',
            borderwidth=1
        )
        
        return fig
    
    def plot_wind_components(self, components: WindComponents, height: int = 800) -> go.Figure:
        """
        Cria gráfico dos componentes do vento.
        
        Args:
            components: Dados dos componentes do vento
            height: Altura do gráfico
        
        Returns:
            go.Figure: Figura do Plotly
        """
        # Criar subplots: 3 componentes individuais + 1 resultado
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Vento Médio (Mean Wind)', 'Ondas (Waves)', 
                          'Turbulência (Turbulence)', 'Fluxo de Ar Resultante (Air Flow)'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'colspan': 1, 'secondary_y': False}]]
        )
        
        # Vento médio
        fig.add_trace(
            go.Scatter(x=components.time, y=components.mean_wind,
                      mode='lines', name='Vento Médio',
                      line=dict(color=self.COLORS['mean_wind'], width=2)),
            row=1, col=1
        )
        
        # Ondas
        fig.add_trace(
            go.Scatter(x=components.time, y=components.waves,
                      mode='lines', name='Ondas',
                      line=dict(color=self.COLORS['waves'], width=2)),
            row=1, col=2
        )
        
        # Turbulência
        fig.add_trace(
            go.Scatter(x=components.time, y=components.turbulence,
                      mode='lines', name='Turbulência',
                      line=dict(color=self.COLORS['turbulence'], width=2)),
            row=2, col=1
        )
        
        # Fluxo de ar resultante
        fig.add_trace(
            go.Scatter(x=components.time, y=components.air_flow,
                      mode='lines', name='Fluxo de Ar',
                      line=dict(color=self.COLORS['air_flow'], width=3)),
            row=2, col=2
        )
        
        # Configurar layout
        fig.update_layout(
            title=dict(
                text='Componentes do Vento - Idealização dos Componentes',
                x=0.5,
                font=dict(size=16)
            ),
            height=height,
            showlegend=False
        )
        
        # Configurar eixos
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(title_text='Tempo (h)', row=i, col=j)
                fig.update_yaxes(title_text='Velocidade (m/s)', row=i, col=j)
        
        return fig
    
    def plot_turbine_power_curve(self, performance: TurbinePerformance, 
                                show_regions: bool = True, height: int = 600) -> go.Figure:
        """
        Cria gráfico da curva de potência da turbina.
        
        Args:
            performance: Dados de performance da turbina
            show_regions: Se deve mostrar regiões operacionais
            height: Altura do gráfico
        
        Returns:
            go.Figure: Figura do Plotly
        """
        fig = go.Figure()
        
        # Curva de potência principal
        fig.add_trace(go.Scatter(
            x=performance.wind_speeds,
            y=performance.power_output,
            mode='lines',
            name='Curva de Potência',
            line=dict(color=self.COLORS['power_curve'], width=3),
            hovertemplate='<b>Curva de Potência</b><br>' +
                         'Velocidade: %{x:.1f} m/s<br>' +
                         'Potência: %{y:.0f} kW<extra></extra>'
        ))
        
        # Adicionar regiões operacionais se solicitado
        if show_regions:
            regions = performance.operating_regions
            
            # Região MPPT
            mppt_start, mppt_end = regions['mppt']
            fig.add_vrect(
                x0=mppt_start, x1=mppt_end,
                fillcolor='green', opacity=0.1,
                annotation_text='MPPT',
                annotation_position='top left'
            )
            
            # Região de potência nominal
            rated_start, rated_end = regions['rated']
            fig.add_vrect(
                x0=rated_start, x1=rated_end,
                fillcolor='blue', opacity=0.1,
                annotation_text='Potência Nominal',
                annotation_position='top right'
            )
            
            # Região parada
            stopped_start, stopped_end = regions['stopped']
            fig.add_vrect(
                x0=stopped_start, x1=stopped_end,
                fillcolor='red', opacity=0.1,
                annotation_text='Parado',
                annotation_position='top left'
            )
        
        # Configurar layout
        fig.update_layout(
            title=dict(
                text='Curva de Potência da Turbina Eólica',
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title='Velocidade do Vento (m/s)',
            yaxis_title='Potência (kW)',
            height=height,
            hovermode='closest'
        )
        
        return fig
    
    def plot_cp_curve(self, performance: TurbinePerformance, height: int = 600) -> go.Figure:
        """
        Cria gráfico do coeficiente de performance (Cp).
        
        Args:
            performance: Dados de performance da turbina
            height: Altura do gráfico
        
        Returns:
            go.Figure: Figura do Plotly
        """
        fig = go.Figure()
        
        # Curva de Cp
        fig.add_trace(go.Scatter(
            x=performance.wind_speeds,
            y=performance.cp_values,
            mode='lines',
            name='Coeficiente Cp',
            line=dict(color=self.COLORS['cp_curve'], width=3),
            hovertemplate='<b>Coeficiente Cp</b><br>' +
                         'Velocidade: %{x:.1f} m/s<br>' +
                         'Cp: %{y:.4f}<extra></extra>'
        ))
        
        # Adicionar linha do limite de Betz
        fig.add_hline(
            y=0.593,
            line_dash='dash',
            line_color='red',
            annotation_text='Limite de Betz (0.593)',
            annotation_position='top right'
        )
        
        # Destacar Cp máximo
        max_cp_idx = np.argmax(performance.cp_values)
        max_cp = performance.cp_values[max_cp_idx]
        max_cp_speed = performance.wind_speeds[max_cp_idx]
        
        fig.add_trace(go.Scatter(
            x=[max_cp_speed],
            y=[max_cp],
            mode='markers',
            name=f'Cp Máximo ({max_cp:.4f})',
            marker=dict(color='red', size=12, symbol='star'),
            hovertemplate=f'<b>Cp Máximo</b><br>' +
                         f'Velocidade: {max_cp_speed:.1f} m/s<br>' +
                         f'Cp: {max_cp:.4f}<extra></extra>'
        ))
        
        # Configurar layout
        fig.update_layout(
            title=dict(
                text='Coeficiente de Performance (Cp) vs Velocidade do Vento',
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title='Velocidade do Vento (m/s)',
            yaxis_title='Coeficiente de Performance (Cp)',
            height=height,
            hovermode='closest'
        )
        
        return fig
    
    def plot_comparative_analysis(self, data_dict: Dict[str, Any], 
                                analysis_type: str = 'wind_profile', height: int = 600) -> go.Figure:
        """
        Cria gráfico comparativo entre diferentes cenários.
        
        Args:
            data_dict: Dicionário com dados para comparação
            analysis_type: Tipo de análise ('wind_profile', 'turbine_performance')
            height: Altura do gráfico
        
        Returns:
            go.Figure: Figura do Plotly
        """
        fig = go.Figure()
        
        if analysis_type == 'wind_profile':
            for name, profile in data_dict.items():
                fig.add_trace(go.Scatter(
                    x=profile.heights,
                    y=profile.power_law_speeds,
                    mode='lines',
                    name=f'{name} - Lei Potência',
                    line=dict(width=2),
                    hovertemplate=f'<b>{name} - Lei Potência</b><br>' +
                                 'Altura: %{x:.1f} m<br>' +
                                 'Velocidade: %{y:.2f} m/s<extra></extra>'
                ))
            
            fig.update_layout(
                title='Comparação de Perfis de Vento',
                xaxis_title='Altura (m)',
                yaxis_title='Velocidade do Vento (m/s)'
            )
        
        elif analysis_type == 'turbine_performance':
            for name, performance in data_dict.items():
                fig.add_trace(go.Scatter(
                    x=performance.wind_speeds,
                    y=performance.power_output,
                    mode='lines',
                    name=name,
                    line=dict(width=2),
                    hovertemplate=f'<b>{name}</b><br>' +
                                 'Velocidade: %{x:.1f} m/s<br>' +
                                 'Potência: %{y:.0f} kW<extra></extra>'
                ))
            
            fig.update_layout(
                title='Comparação de Curvas de Potência',
                xaxis_title='Velocidade do Vento (m/s)',
                yaxis_title='Potência (kW)'
            )
        
        fig.update_layout(
            height=height,
            hovermode='closest'
        )
        
        return fig
    
    def create_analysis_summary_cards(self, analysis_data: Dict) -> None:
        """
        Cria cards de resumo da análise usando Streamlit.
        
        Args:
            analysis_data: Dados da análise para exibir
        """
        if 'operational_range' in analysis_data:
            # Performance de turbina
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Faixa Operacional",
                    f"{analysis_data['operational_range']['min_wind_speed']:.1f} - "
                    f"{analysis_data['operational_range']['max_wind_speed']:.1f} m/s"
                )
            
            with col2:
                st.metric(
                    "Potência Máxima",
                    f"{analysis_data['power_statistics']['max_power']:.0f} kW"
                )
            
            with col3:
                st.metric(
                    "Cp Máximo",
                    f"{analysis_data['cp_statistics']['max_cp']:.4f}"
                )
            
            with col4:
                st.metric(
                    "Fator de Capacidade",
                    f"{analysis_data['efficiency_metrics']['capacity_factor_estimate']:.1%}"
                )
        
        elif 'correlations' in analysis_data:
            # Componentes do vento
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Correlação Vento Médio",
                    f"{analysis_data['correlations']['mean_wind_vs_air_flow']:.3f}"
                )
            
            with col2:
                st.metric(
                    "Correlação Ondas",
                    f"{analysis_data['correlations']['waves_vs_air_flow']:.3f}"
                )
            
            with col3:
                st.metric(
                    "Correlação Turbulência",
                    f"{analysis_data['correlations']['turbulence_vs_air_flow']:.3f}"
                )
    
    @staticmethod
    def save_figure_as_html(fig: go.Figure, filename: str = 'analysis_plot.html') -> str:
        """
        Salva figura como arquivo HTML.
        
        Args:
            fig: Figura do Plotly
            filename: Nome do arquivo
        
        Returns:
            str: Caminho do arquivo salvo
        """
        fig.write_html(filename)
        return filename
    
    def plot_wind_profile_comparison(self, profile_data: Dict, height: int = 600) -> go.Figure:
        """
        Cria gráfico comparativo dos métodos de correção do perfil de vento.
        
        Args:
            profile_data: Dados do perfil de vento
            height: Altura do gráfico
            
        Returns:
            Figura Plotly com comparação dos perfis
        """
        fig = go.Figure()
        
        # Obter parâmetros
        params = profile_data.get('parameters', {})
        profile = profile_data.get('profile')  # WindProfile object
        
        v_ref = params.get('v_ref', 10)
        h_ref = params.get('h_ref', 10)
        altura_turbina = params.get('altura_turbina', 80)
        
        # Velocidade original
        fig.add_trace(go.Scatter(
            x=[v_ref, v_ref],
            y=[h_ref, altura_turbina],
            mode='lines+markers',
            name='Velocidade Original',
            line=dict(color='gray', width=2, dash='dash'),
            marker=dict(size=8)
        ))
        
        # Lei da Potência
        if hasattr(profile, 'heights') and hasattr(profile, 'power_law_speeds'):
            alturas = profile.heights
            velocidades_power = profile.power_law_speeds
            
            fig.add_trace(go.Scatter(
                x=velocidades_power,
                y=alturas,
                mode='lines+markers',
                name='Lei da Potência',
                line=dict(color=self.COLORS['power_law'], width=3),
                marker=dict(size=6)
            ))
        
        # Lei Logarítmica
        if hasattr(profile, 'logarithmic_speeds'):
            velocidades_log = profile.logarithmic_speeds
            
            fig.add_trace(go.Scatter(
                x=velocidades_log,
                y=alturas,
                mode='lines+markers',
                name='Lei Logarítmica',
                line=dict(color=self.COLORS['logarithmic'], width=3),
                marker=dict(size=6)
            ))
        
        # Destacar altura da turbina
        fig.add_hline(
            y=altura_turbina,
            line_dash="dot",
            annotation_text="Altura da Turbina"
        )
        
        fig.update_layout(
            title='Comparação dos Métodos de Correção do Perfil de Vento',
            xaxis_title='Velocidade do Vento (m/s)',
            yaxis_title='Altura (m)',
            height=height,
            legend=dict(x=0.7, y=0.2)
        )
        
        return fig
    
    def plot_complete_temporal_analysis(self, wind_components: 'WindComponents', 
                                      performance_data: Optional[Dict] = None, 
                                      height: int = 800) -> go.Figure:
        """
        Cria análise temporal completa integrando vento e performance.
        
        Args:
            wind_components: Componentes do vento
            performance_data: Dados de performance da turbina
            height: Altura do gráfico
            
        Returns:
            Figura Plotly com análise temporal
        """
        if performance_data:
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=['Componentes do Vento', 'Fluxo de Ar Resultante', 'Potência Gerada'],
                vertical_spacing=0.08,
                shared_xaxes=True
            )
        else:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=['Componentes do Vento', 'Fluxo de Ar Resultante'],
                vertical_spacing=0.1,
                shared_xaxes=True
            )
        
        # Tempo baseado na duração
        n_points = len(wind_components.air_flow)
        tempo = np.linspace(0, 24, n_points)  # Assumindo 24h como padrão
        
        # Componentes do vento
        fig.add_trace(go.Scatter(
            x=tempo, y=wind_components.mean_wind,
            name='Vento Médio', line=dict(color=self.COLORS['mean_wind'])
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=tempo, y=wind_components.waves,
            name='Ondas', line=dict(color=self.COLORS['waves'])
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=tempo, y=wind_components.turbulence,
            name='Turbulência', line=dict(color=self.COLORS['turbulence'])
        ), row=1, col=1)
        
        # Fluxo de ar resultante
        fig.add_trace(go.Scatter(
            x=tempo, y=wind_components.air_flow,
            name='Fluxo de Ar', line=dict(color=self.COLORS['air_flow'], width=2)
        ), row=2, col=1)
        
        # Performance da turbina (se disponível)
        if performance_data:
            fig.add_trace(go.Scatter(
                x=tempo, y=performance_data['power_output'],
                name='Potência', line=dict(color=self.COLORS['power_curve'], width=2)
            ), row=3, col=1)
        
        fig.update_layout(
            title='Análise Temporal Completa',
            height=height,
            showlegend=True
        )
        
        fig.update_xaxes(title_text='Tempo (horas)', row=2 if not performance_data else 3, col=1)
        fig.update_yaxes(title_text='Velocidade (m/s)', row=1, col=1)
        fig.update_yaxes(title_text='Velocidade (m/s)', row=2, col=1)
        
        if performance_data:
            fig.update_yaxes(title_text='Potência (kW)', row=3, col=1)
        
        return fig
    
    def plot_wind_speed_distribution(self, wind_speeds: np.ndarray, height: int = 500) -> go.Figure:
        """
        Cria histograma da distribuição de velocidades do vento.
        
        Args:
            wind_speeds: Array de velocidades do vento
            height: Altura do gráfico
            
        Returns:
            Figura Plotly com distribuição
        """
        fig = go.Figure()
        
        # Histograma
        fig.add_trace(go.Histogram(
            x=wind_speeds,
            nbinsx=30,
            name='Distribuição',
            marker_color=self.COLORS['mean_wind'],
            opacity=0.7
        ))
        
        # Estatísticas
        media = np.mean(wind_speeds)
        mediana = np.median(wind_speeds)
        
        fig.add_vline(x=media, line_dash="dash", annotation_text=f"Média: {media:.2f} m/s")
        fig.add_vline(x=mediana, line_dash="dot", annotation_text=f"Mediana: {mediana:.2f} m/s")
        
        fig.update_layout(
            title='Distribuição de Velocidades do Vento',
            xaxis_title='Velocidade do Vento (m/s)',
            yaxis_title='Frequência',
            height=height
        )
        
        return fig
    
    def plot_power_curve_with_real_data(self, power_curve: Dict, real_wind_speeds: np.ndarray, 
                                       height: int = 600) -> go.Figure:
        """
        Sobrepõe a curva de potência teórica com dados reais de vento.
        
        Args:
            power_curve: Dados da curva de potência
            real_wind_speeds: Velocidades reais do vento
            height: Altura do gráfico
            
        Returns:
            Figura Plotly com curva e dados reais
        """
        fig = go.Figure()
        
        # Curva de potência teórica
        fig.add_trace(go.Scatter(
            x=power_curve['wind_speeds'],
            y=power_curve['power_output'],
            mode='lines',
            name='Curva de Potência',
            line=dict(color=self.COLORS['power_curve'], width=3)
        ))
        
        # Distribuição dos dados reais
        hist, bin_edges = np.histogram(real_wind_speeds, bins=30)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Normalizar para escala de potência
        hist_normalized = hist / np.max(hist) * np.max(power_curve['power_output']) * 0.3
        
        fig.add_trace(go.Scatter(
            x=bin_centers,
            y=hist_normalized,
            mode='lines',
            name='Distribuição do Vento',
            fill='tozeroy',
            line=dict(color=self.COLORS['mean_wind']),
            opacity=0.3,
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Curva de Potência vs Distribuição Real do Vento',
            xaxis_title='Velocidade do Vento (m/s)',
            height=height,
            yaxis=dict(title='Potência (kW)'),
            yaxis2=dict(
                title='Frequência Relativa',
                overlaying='y',
                side='right'
            )
        )
        
        return fig
    
    def plot_sensitivity_analysis(self, x_values: np.ndarray, y_values: np.ndarray,
                                x_label: str, y_label: str, height: int = 500) -> go.Figure:
        """
        Cria gráfico de análise de sensibilidade.
        
        Args:
            x_values: Valores do eixo X
            y_values: Valores do eixo Y
            x_label: Rótulo do eixo X
            y_label: Rótulo do eixo Y
            height: Altura do gráfico
            
        Returns:
            Figura Plotly com análise de sensibilidade
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name='Sensibilidade',
            line=dict(color=self.COLORS['power_curve'], width=3),
            marker=dict(size=8)
        ))
        
        # Linha de break-even se aplicável
        if 'VPL' in y_label or 'NPV' in y_label:
            fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even")
        
        fig.update_layout(
            title=f'Análise de Sensibilidade: {y_label} vs {x_label}',
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=height
        )
        
        return fig
    
    def create_analysis_summary_cards(self, analysis: Dict):
        """
        Cria cards de resumo da análise usando métricas do Streamlit.
        
        Args:
            analysis: Dados da análise
        """
        col1, col2, col3, col4 = st.columns(4)
        
        # Card 1: Vento Médio
        with col1:
            mean_wind_stats = analysis['mean_wind']
            st.metric(
                "Vento Médio",
                f"{mean_wind_stats['mean']:.2f} m/s",
                delta=f"±{mean_wind_stats['std']:.2f}"
            )
        
        # Card 2: Turbulência
        with col2:
            turb_stats = analysis['turbulence']
            st.metric(
                "Turbulência",
                f"{turb_stats['mean']:.2f} m/s",
                delta=f"±{turb_stats['std']:.2f}"
            )
        
        # Card 3: Fluxo de Ar
        with col3:
            air_stats = analysis['air_flow']
            st.metric(
                "Fluxo de Ar",
                f"{air_stats['mean']:.2f} m/s",
                delta=f"Range: {air_stats['max'] - air_stats['min']:.2f}"
            )
        
        # Card 4: Correlação
        with col4:
            corr = analysis['correlations']['mean_wind_vs_air_flow']
            st.metric(
                "Correlação",
                f"{corr:.3f}",
                delta="Vento-Fluxo"
            )
    
    def plot_temporal_performance(self, performance_data: Dict, wind_data: np.ndarray, 
                                height: int = 800) -> go.Figure:
        """
        Cria gráfico temporal da performance da turbina.
        
        Args:
            performance_data: Dados de performance temporal
            wind_data: Dados do vento
            height: Altura do gráfico
            
        Returns:
            Figura Plotly com performance temporal
        """
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=['Velocidade do Vento', 'Potência Gerada', 'RPM e Cp'],
            vertical_spacing=0.08,
            shared_xaxes=True,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}], 
                   [{"secondary_y": True}]]
        )
        
        # Tempo baseado na duração
        n_points = len(wind_data)
        tempo = np.linspace(0, 24, n_points)  # Assumindo 24h
        
        # Velocidade do vento
        fig.add_trace(go.Scatter(
            x=tempo, y=wind_data,
            name='Velocidade do Vento',
            line=dict(color=self.COLORS['mean_wind'], width=2)
        ), row=1, col=1)
        
        # Potência gerada
        fig.add_trace(go.Scatter(
            x=tempo, y=performance_data['power_output'],
            name='Potência',
            line=dict(color=self.COLORS['power_curve'], width=2)
        ), row=2, col=1)
        
        # RPM (eixo principal)
        if 'rpm' in performance_data:
            fig.add_trace(go.Scatter(
                x=tempo, y=performance_data['rpm'],
                name='RPM',
                line=dict(color=self.COLORS['turbulence'], width=2)
            ), row=3, col=1)
        
        # Cp (eixo secundário)
        if 'cp' in performance_data:
            fig.add_trace(go.Scatter(
                x=tempo, y=performance_data['cp'],
                name='Cp',
                line=dict(color=self.COLORS['cp_curve'], width=2)
            ), row=3, col=1, secondary_y=True)
        
        fig.update_layout(
            title='Performance Temporal da Turbina',
            height=height,
            showlegend=True
        )
        
        fig.update_xaxes(title_text='Tempo (horas)', row=3, col=1)
        fig.update_yaxes(title_text='Velocidade (m/s)', row=1, col=1)
        fig.update_yaxes(title_text='Potência (kW)', row=2, col=1)
        fig.update_yaxes(title_text='RPM', row=3, col=1)
        
        if 'cp' in performance_data:
            fig.update_yaxes(title_text='Cp', row=3, col=1, secondary_y=True)
        
        return fig
    
    @staticmethod
    def configure_plotly_theme():
        """Configura tema padrão para gráficos Plotly."""
        import plotly.io as pio
        
        # Configurar tema personalizado
        custom_theme = {
            'layout': {
                'font': {'family': 'Arial, sans-serif', 'size': 12},
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white',
                'colorway': list(AnalysisVisualizer.COLORS.values())
            }
        }
        
        pio.templates['wind_turbine'] = custom_theme
        pio.templates.default = 'wind_turbine'
