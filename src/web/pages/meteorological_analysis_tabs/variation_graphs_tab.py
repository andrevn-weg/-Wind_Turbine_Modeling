"""
Tab de Gráficos de Variação - Análises Meteorológicas

Contém a funcionalidade da aba "Gráficos de Variação" com visualizações
temporais dos dados meteorológicos separados por fonte e altura.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_variation_graphs_tab(df):
    """
    Renderiza a aba de Gráficos de Variação dos dados meteorológicos
    
    Args:
        df: DataFrame com dados meteorológicos processados
    """
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para gerar gráficos.")
        return
    
    st.markdown("""
    <div class='section-header-minor'>
        <h4>📈 Variação dos Dados Meteorológicos ao Longo do Tempo</h4>
        <p>Dados separados por fonte e altura de captura para análise precisa.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar coluna combinada para fonte + altura
    df['fonte_altura'] = df['fonte'] + ' - ' + df['altura_captura'].astype(str) + 'm'
    
    # Gráfico de Velocidade do Vento
    if 'velocidade_vento' in df.columns and df['velocidade_vento'].notna().any():
        st.subheader("🌪️ Velocidade do Vento por Fonte e Altura")
        
        fig_vento = px.line(
            df, 
            x='data_hora', 
            y='velocidade_vento',
            color='fonte_altura',
            title="Variação da Velocidade do Vento (Separado por Fonte e Altura)",
            labels={
                'velocidade_vento': 'Velocidade (m/s)', 
                'data_hora': 'Data/Hora',
                'fonte_altura': 'Fonte - Altura'
            }
        )
        fig_vento.update_layout(
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_vento, use_container_width=True)
        
        # Adicionar informação explicativa
        st.info("💡 Cada linha representa uma combinação única de fonte de dados e altura de captura. Isso permite comparar diferentes condições de medição.")
    
    # Gráficos de Temperatura e Umidade lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        if 'temperatura' in df.columns and df['temperatura'].notna().any():
            st.subheader("🌡️ Temperatura por Fonte e Altura")
            
            df_temp = df.dropna(subset=['temperatura'])
            if not df_temp.empty:
                fig_temp = px.line(
                    df_temp, 
                    x='data_hora', 
                    y='temperatura',
                    color='fonte_altura',
                    title="Variação da Temperatura",
                    labels={
                        'temperatura': 'Temperatura (°C)', 
                        'data_hora': 'Data/Hora',
                        'fonte_altura': 'Fonte - Altura'
                    }
                )
                fig_temp.update_layout(height=400)
                st.plotly_chart(fig_temp, use_container_width=True)
            else:
                st.info("Nenhum dado de temperatura disponível.")
    
    with col2:
        if 'umidade' in df.columns and df['umidade'].notna().any():
            st.subheader("💧 Umidade por Fonte e Altura")
            
            df_umidade = df.dropna(subset=['umidade'])
            if not df_umidade.empty:
                fig_umidade = px.line(
                    df_umidade, 
                    x='data_hora', 
                    y='umidade',
                    color='fonte_altura',
                    title="Variação da Umidade",
                    labels={
                        'umidade': 'Umidade (%)', 
                        'data_hora': 'Data/Hora',
                        'fonte_altura': 'Fonte - Altura'
                    }
                )
                fig_umidade.update_layout(height=400)
                st.plotly_chart(fig_umidade, use_container_width=True)
            else:
                st.info("Nenhum dado de umidade disponível.")
    
    # Gráfico de dispersão: Velocidade vs Temperatura (se ambos disponíveis)
    if ('temperatura' in df.columns and df['temperatura'].notna().any() and 
        'velocidade_vento' in df.columns and df['velocidade_vento'].notna().any()):
        
        st.markdown("---")
        st.subheader("🔗 Correlação: Velocidade do Vento vs Temperatura")
        
        df_correlacao = df.dropna(subset=['temperatura', 'velocidade_vento'])
        
        if not df_correlacao.empty:
            fig_scatter = px.scatter(
                df_correlacao,
                x='temperatura',
                y='velocidade_vento',
                color='fonte_altura',
                size='altura_captura',
                title="Correlação entre Velocidade do Vento e Temperatura",
                labels={
                    'temperatura': 'Temperatura (°C)',
                    'velocidade_vento': 'Velocidade do Vento (m/s)',
                    'fonte_altura': 'Fonte - Altura'
                },
                hover_data=['data_hora']
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Análise por período do dia (se temos dados suficientes)
    if len(df) > 24:  # Pelo menos 24 registros para análise por hora
        st.markdown("---")
        st.subheader("🕐 Análise por Período do Dia")
        
        # Extrair hora do dia
        df_periodo = df.copy()
        df_periodo['hora'] = df_periodo['data_hora'].dt.hour
        
        # Agrupar por hora e fonte_altura
        vento_por_hora = df_periodo.groupby(['hora', 'fonte_altura'])['velocidade_vento'].mean().reset_index()
        
        fig_hora = px.line(
            vento_por_hora,
            x='hora',
            y='velocidade_vento',
            color='fonte_altura',
            title="Velocidade Média do Vento por Hora do Dia",
            labels={
                'hora': 'Hora do Dia',
                'velocidade_vento': 'Velocidade Média (m/s)',
                'fonte_altura': 'Fonte - Altura'
            }
        )
        fig_hora.update_layout(height=400)
        st.plotly_chart(fig_hora, use_container_width=True)
        
        st.info("📊 Este gráfico mostra o padrão médio de velocidade do vento ao longo do dia, separado por fonte e altura.")
    
    # Gráfico de barras: Distribuição de registros por fonte/altura
    st.markdown("---")
    st.subheader("📊 Distribuição de Registros por Fonte e Altura")
    
    contagem_fonte_altura = df['fonte_altura'].value_counts().reset_index()
    contagem_fonte_altura.columns = ['fonte_altura', 'count']
    
    fig_barras = px.bar(
        contagem_fonte_altura,
        x='fonte_altura',
        y='count',
        title="Número de Registros por Fonte e Altura",
        labels={
            'fonte_altura': 'Fonte - Altura',
            'count': 'Número de Registros'
        }
    )
    fig_barras.update_layout(
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_barras, use_container_width=True)
