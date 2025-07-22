"""
Tab de Detalhamento Avançado - Análises Meteorológicas

Contém a funcionalidade da aba "Detalhamento Avançado" com análises
estatísticas avançadas, correlações e insights detalhados por fonte e altura.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def render_advanced_details_tab(df):
    """
    Renderiza a aba de Detalhamento Avançado dos dados meteorológicos
    
    Args:
        df: DataFrame com dados meteorológicos processados
    """
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para análise avançada.")
        return
    
    st.markdown("""
    <div class='section-header-minor'>
        <h4>🔬 Análise Avançada dos Dados Meteorológicos</h4>
        <p>Análises estatísticas detalhadas separadas por fonte e altura de captura.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar coluna combinada para fonte + altura
    df['fonte_altura'] = df['fonte'] + ' - ' + df['altura_captura'].astype(str) + 'm'
    
    # Análise de extremos por fonte/altura
    st.subheader("🎯 Análise de Valores Extremos por Fonte/Altura")
    
    extremos_data = []
    
    for fonte_altura in df['fonte_altura'].unique():
        df_subset = df[df['fonte_altura'] == fonte_altura]
        
        if not df_subset.empty:
            # Velocidade do vento
            vento_max_idx = df_subset['velocidade_vento'].idxmax()
            vento_min_idx = df_subset['velocidade_vento'].idxmin()
            
            extremos_data.append({
                'fonte_altura': fonte_altura,
                'vento_max': df_subset.loc[vento_max_idx, 'velocidade_vento'],
                'vento_max_data': df_subset.loc[vento_max_idx, 'data_hora'],
                'vento_min': df_subset.loc[vento_min_idx, 'velocidade_vento'],
                'vento_min_data': df_subset.loc[vento_min_idx, 'data_hora'],
                'total_registros': len(df_subset)
            })
            
            # Adicionar temperatura e umidade se disponível
            if 'temperatura' in df_subset.columns and df_subset['temperatura'].notna().any():
                temp_data = df_subset.dropna(subset=['temperatura'])
                if not temp_data.empty:
                    temp_max_idx = temp_data['temperatura'].idxmax()
                    temp_min_idx = temp_data['temperatura'].idxmin()
                    extremos_data[-1]['temp_max'] = temp_data.loc[temp_max_idx, 'temperatura']
                    extremos_data[-1]['temp_max_data'] = temp_data.loc[temp_max_idx, 'data_hora']
                    extremos_data[-1]['temp_min'] = temp_data.loc[temp_min_idx, 'temperatura']
                    extremos_data[-1]['temp_min_data'] = temp_data.loc[temp_min_idx, 'data_hora']
    
    if extremos_data:
        df_extremos = pd.DataFrame(extremos_data)
        st.dataframe(df_extremos, use_container_width=True)
    
    # Análise de distribuição estatística
    st.markdown("---")
    st.subheader("📊 Análise de Distribuição Estatística")
    
    # Histogramas por fonte/altura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌪️ Distribuição da Velocidade do Vento**")
        
        fig_hist = px.histogram(
            df,
            x='velocidade_vento',
            color='fonte_altura',
            title="Distribuição da Velocidade do Vento por Fonte/Altura",
            labels={
                'velocidade_vento': 'Velocidade (m/s)',
                'count': 'Frequência',
                'fonte_altura': 'Fonte - Altura'
            },
            barmode='overlay',
            opacity=0.7
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        if 'temperatura' in df.columns and df['temperatura'].notna().any():
            st.markdown("**🌡️ Distribuição da Temperatura**")
            
            df_temp = df.dropna(subset=['temperatura'])
            if not df_temp.empty:
                fig_hist_temp = px.histogram(
                    df_temp,
                    x='temperatura',
                    color='fonte_altura',
                    title="Distribuição da Temperatura por Fonte/Altura",
                    labels={
                        'temperatura': 'Temperatura (°C)',
                        'count': 'Frequência',
                        'fonte_altura': 'Fonte - Altura'
                    },
                    barmode='overlay',
                    opacity=0.7
                )
                fig_hist_temp.update_layout(height=400)
                st.plotly_chart(fig_hist_temp, use_container_width=True)
        else:
            st.info("Dados de temperatura não disponíveis.")
    
    # Classificação do vento por fonte/altura
    st.markdown("---")
    st.subheader("🌀 Análise da Classificação do Vento por Fonte/Altura")
    
    if 'classificacao_vento' in df.columns:
        # Criar tabela cruzada
        classificacao_crosstab = pd.crosstab(
            df['classificacao_vento'], 
            df['fonte_altura'], 
            margins=True
        )
        
        st.dataframe(classificacao_crosstab, use_container_width=True)
        
        # Gráfico de barras empilhadas
        df_class_plot = df.groupby(['fonte_altura', 'classificacao_vento']).size().reset_index(name='count')
        
        fig_class = px.bar(
            df_class_plot,
            x='fonte_altura',
            y='count',
            color='classificacao_vento',
            title="Distribuição das Classificações de Vento por Fonte/Altura",
            labels={
                'count': 'Número de Registros',
                'fonte_altura': 'Fonte - Altura',
                'classificacao_vento': 'Classificação'
            }
        )
        fig_class.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_class, use_container_width=True)
    
    # Análise de correlação avançada
    st.markdown("---")
    st.subheader("🔗 Análise de Correlação Avançada")
    
    # Preparar dados para correlação
    colunas_numericas = ['velocidade_vento', 'altura_captura']
    
    if 'temperatura' in df.columns:
        colunas_numericas.append('temperatura')
    if 'umidade' in df.columns:
        colunas_numericas.append('umidade')
    
    # Adicionar variáveis temporais
    df_corr = df.copy()
    df_corr['hora'] = df_corr['data_hora'].dt.hour
    df_corr['dia_ano'] = df_corr['data_hora'].dt.dayofyear
    df_corr['mes'] = df_corr['data_hora'].dt.month
    
    colunas_numericas.extend(['hora', 'dia_ano', 'mes'])
    
    # Matriz de correlação por fonte/altura
    for fonte_altura in df['fonte_altura'].unique()[:3]:  # Limitar a 3 para performance
        st.markdown(f"**📈 Correlação para {fonte_altura}**")
        
        df_subset = df_corr[df_corr['fonte_altura'] == fonte_altura]
        
        if len(df_subset) > 1:
            correlation_matrix = df_subset[colunas_numericas].corr()
            
            fig_corr = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title=f"Matriz de Correlação - {fonte_altura}",
                color_continuous_scale='RdBu_r'
            )
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
    
    # Análise temporal avançada
    st.markdown("---")
    st.subheader("⏰ Análise Temporal Avançada")
    
    # Padrões por hora do dia
    if len(df) > 24:
        df_temporal = df.copy()
        df_temporal['hora'] = df_temporal['data_hora'].dt.hour
        df_temporal['dia_semana'] = df_temporal['data_hora'].dt.day_name()
        df_temporal['mes'] = df_temporal['data_hora'].dt.month_name()
        
        # Heatmap por hora e fonte/altura
        hourly_avg = df_temporal.groupby(['hora', 'fonte_altura'])['velocidade_vento'].mean().reset_index()
        
        if not hourly_avg.empty:
            hourly_pivot = hourly_avg.pivot(index='hora', columns='fonte_altura', values='velocidade_vento')
            
            fig_hourly = px.imshow(
                hourly_pivot.T,
                title="Velocidade Média do Vento por Hora do Dia e Fonte/Altura",
                labels={
                    'x': 'Hora do Dia',
                    'y': 'Fonte - Altura',
                    'color': 'Velocidade (m/s)'
                },
                color_continuous_scale='viridis'
            )
            fig_hourly.update_layout(height=500)
            st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Análise de tendências
    st.markdown("---")
    st.subheader("📈 Análise de Tendências")
    
    # Calcular tendências para cada fonte/altura
    tendencias_data = []
    
    for fonte_altura in df['fonte_altura'].unique():
        df_subset = df[df['fonte_altura'] == fonte_altura].sort_values('data_hora')
        
        if len(df_subset) > 10:  # Necessário pelo menos 10 pontos para tendência
            # Calcular tendência linear
            x = np.arange(len(df_subset))
            y = df_subset['velocidade_vento'].values
            
            # Regressão linear simples
            coeffs = np.polyfit(x, y, 1)
            tendencia = coeffs[0]  # coeficiente angular
            
            # R² para qualidade do ajuste
            y_pred = np.polyval(coeffs, x)
            r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            tendencias_data.append({
                'fonte_altura': fonte_altura,
                'tendencia_ms_por_registro': tendencia,
                'tendencia_interpretacao': 'Crescente' if tendencia > 0 else 'Decrescente' if tendencia < 0 else 'Estável',
                'r_squared': r_squared,
                'qualidade_ajuste': 'Boa' if r_squared > 0.5 else 'Moderada' if r_squared > 0.2 else 'Baixa',
                'total_registros': len(df_subset)
            })
    
    if tendencias_data:
        df_tendencias = pd.DataFrame(tendencias_data)
        st.dataframe(df_tendencias, use_container_width=True)
        
        st.info("💡 A tendência indica se a velocidade do vento está aumentando ou diminuindo ao longo do tempo para cada fonte/altura.")
    
    # Análise de outliers
    st.markdown("---")
    st.subheader("🎯 Detecção de Outliers por Fonte/Altura")
    
    outliers_data = []
    
    for fonte_altura in df['fonte_altura'].unique():
        df_subset = df[df['fonte_altura'] == fonte_altura]
        
        if len(df_subset) > 4:  # Necessário pelo menos 5 pontos para quartis
            Q1 = df_subset['velocidade_vento'].quantile(0.25)
            Q3 = df_subset['velocidade_vento'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df_subset[
                (df_subset['velocidade_vento'] < lower_bound) | 
                (df_subset['velocidade_vento'] > upper_bound)
            ]
            
            outliers_data.append({
                'fonte_altura': fonte_altura,
                'total_registros': len(df_subset),
                'outliers_detectados': len(outliers),
                'percentual_outliers': (len(outliers) / len(df_subset) * 100) if len(df_subset) > 0 else 0,
                'limite_inferior': lower_bound,
                'limite_superior': upper_bound,
                'outlier_maximo': outliers['velocidade_vento'].max() if len(outliers) > 0 else None,
                'outlier_minimo': outliers['velocidade_vento'].min() if len(outliers) > 0 else None
            })
    
    if outliers_data:
        df_outliers = pd.DataFrame(outliers_data)
        st.dataframe(df_outliers, use_container_width=True)
        
        st.info("📊 Outliers são valores que se desviam significativamente do padrão normal. Podem indicar eventos meteorológicos extremos ou erros de medição.")
