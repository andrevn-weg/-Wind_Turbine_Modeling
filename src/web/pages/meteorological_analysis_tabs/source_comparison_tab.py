"""
Tab de Comparação entre Fontes - Análises Meteorológicas

Contém a funcionalidade da aba "Comparação entre Fontes" com análises
comparativas entre diferentes origens de dados e alturas de captura.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_source_comparison_tab(df):
    """
    Renderiza a aba de Comparação entre Fontes dos dados meteorológicos
    
    Args:
        df: DataFrame com dados meteorológicos processados
    """
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para comparação.")
        return
    
    st.markdown("""
    <div class='section-header-minor'>
        <h4>🔍 Comparação entre Fontes de Dados e Alturas</h4>
        <p>Análise comparativa separando por origem dos dados e altura de captura.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar coluna combinada para fonte + altura
    df['fonte_altura'] = df['fonte'] + ' - ' + df['altura_captura'].astype(str) + 'm'
    
    fontes_alturas = df['fonte_altura'].unique()
    
    if len(fontes_alturas) < 2:
        st.info("É necessário dados de pelo menos 2 combinações de fonte/altura diferentes para comparação.")
        return
    
    # Estatísticas por fonte e altura
    st.subheader("📊 Estatísticas Detalhadas por Fonte e Altura")
    
    # Agrupar estatísticas por fonte_altura
    stats_fonte_altura = df.groupby('fonte_altura').agg({
        'velocidade_vento': ['count', 'mean', 'std', 'min', 'max', 'median'],
        'temperatura': ['count', 'mean', 'std', 'min', 'max'],
        'umidade': ['count', 'mean', 'std', 'min', 'max'],
        'data_hora': ['min', 'max']
    }).round(2)
    
    # Flatten e renomear colunas
    stats_fonte_altura.columns = [f"{col[0]}_{col[1]}" for col in stats_fonte_altura.columns]
    
    rename_dict = {
        'velocidade_vento_count': 'Registros',
        'velocidade_vento_mean': 'Vento Médio (m/s)',
        'velocidade_vento_std': 'Desvio Padrão',
        'velocidade_vento_min': 'Vento Mín (m/s)',
        'velocidade_vento_max': 'Vento Máx (m/s)',
        'velocidade_vento_median': 'Mediana (m/s)',
        'temperatura_count': 'Reg. Temp',
        'temperatura_mean': 'Temp Média (°C)',
        'temperatura_std': 'Temp Desvio',
        'temperatura_min': 'Temp Mín (°C)',
        'temperatura_max': 'Temp Máx (°C)',
        'umidade_count': 'Reg. Umidade',
        'umidade_mean': 'Umidade Média (%)',
        'umidade_std': 'Umidade Desvio',
        'umidade_min': 'Umidade Mín (%)',
        'umidade_max': 'Umidade Máx (%)',
        'data_hora_min': 'Primeiro Registro',
        'data_hora_max': 'Último Registro'
    }
    
    stats_fonte_altura.rename(columns=rename_dict, inplace=True)
    
    st.dataframe(stats_fonte_altura, use_container_width=True, height=400)
    
    # Gráficos comparativos
    st.markdown("---")
    
    # Box plots para comparação de distribuições
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌪️ Distribuição da Velocidade do Vento")
        
        fig_box_vento = px.box(
            df, 
            x='fonte_altura', 
            y='velocidade_vento',
            title="Distribuição da Velocidade do Vento por Fonte/Altura",
            labels={
                'velocidade_vento': 'Velocidade (m/s)', 
                'fonte_altura': 'Fonte - Altura'
            }
        )
        fig_box_vento.update_layout(
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_box_vento, use_container_width=True)
    
    with col2:
        if 'temperatura' in df.columns and df['temperatura'].notna().any():
            st.subheader("🌡️ Distribuição da Temperatura")
            
            df_temp = df.dropna(subset=['temperatura'])
            if not df_temp.empty:
                fig_box_temp = px.box(
                    df_temp, 
                    x='fonte_altura', 
                    y='temperatura',
                    title="Distribuição da Temperatura por Fonte/Altura",
                    labels={
                        'temperatura': 'Temperatura (°C)', 
                        'fonte_altura': 'Fonte - Altura'
                    }
                )
                fig_box_temp.update_layout(
                    height=400,
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_box_temp, use_container_width=True)
        else:
            st.info("Dados de temperatura não disponíveis para comparação.")
    
    # Gráfico de violino para análise mais detalhada da distribuição
    st.markdown("---")
    st.subheader("🎻 Análise Detalhada da Distribuição - Velocidade do Vento")
    
    fig_violin = px.violin(
        df,
        x='fonte_altura',
        y='velocidade_vento',
        title="Distribuição Detalhada da Velocidade do Vento",
        labels={
            'velocidade_vento': 'Velocidade (m/s)',
            'fonte_altura': 'Fonte - Altura'
        },
        box=True
    )
    fig_violin.update_layout(
        height=500,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_violin, use_container_width=True)
    
    # Comparação temporal entre fontes/alturas
    st.markdown("---")
    st.subheader("📈 Comparação Temporal")
    
    # Resample para dados diários para melhor visualização comparativa
    df_temp_comparison = df.copy()
    df_temp_comparison.set_index('data_hora', inplace=True)
    
    # Agrupar por dia e fonte_altura
    daily_avg = df_temp_comparison.groupby(['fonte_altura', pd.Grouper(freq='D')])['velocidade_vento'].mean().reset_index()
    
    if not daily_avg.empty:
        fig_temporal = px.line(
            daily_avg,
            x='data_hora',
            y='velocidade_vento',
            color='fonte_altura',
            title="Comparação Temporal - Velocidade Média Diária do Vento",
            labels={
                'velocidade_vento': 'Velocidade Média Diária (m/s)',
                'data_hora': 'Data',
                'fonte_altura': 'Fonte - Altura'
            }
        )
        fig_temporal.update_layout(height=500)
        st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Matriz de correlação entre diferentes fontes/alturas
    st.markdown("---")
    st.subheader("🔗 Correlação entre Fontes/Alturas")
    
    # Pivot table para correlação
    pivot_vento = df.pivot_table(
        values='velocidade_vento',
        index='data_hora',
        columns='fonte_altura',
        aggfunc='mean'
    )
    
    if not pivot_vento.empty and len(pivot_vento.columns) > 1:
        correlacao = pivot_vento.corr()
        
        fig_corr = px.imshow(
            correlacao,
            text_auto=True,
            aspect="auto",
            title="Matriz de Correlação - Velocidade do Vento entre Fontes/Alturas",
            labels={
                'x': 'Fonte - Altura',
                'y': 'Fonte - Altura',
                'color': 'Correlação'
            }
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.info("💡 Valores próximos a 1 indicam alta correlação positiva, próximos a -1 indicam correlação negativa, e próximos a 0 indicam baixa correlação.")
    
    # Análise de consistência temporal
    st.markdown("---")
    st.subheader("⏱️ Análise de Consistência Temporal")
    
    # Calcular gaps temporais para cada fonte/altura
    consistency_data = []
    
    for fonte_altura in fontes_alturas:
        df_subset = df[df['fonte_altura'] == fonte_altura].sort_values('data_hora')
        
        if len(df_subset) > 1:
            gaps = df_subset['data_hora'].diff().dt.total_seconds() / 3600  # gaps em horas
            gaps = gaps.dropna()
            
            consistency_data.append({
                'fonte_altura': fonte_altura,
                'total_registros': len(df_subset),
                'primeiro_registro': df_subset['data_hora'].min(),
                'ultimo_registro': df_subset['data_hora'].max(),
                'gap_medio_horas': gaps.mean() if len(gaps) > 0 else 0,
                'gap_maximo_horas': gaps.max() if len(gaps) > 0 else 0,
                'gaps_grandes': (gaps > 24).sum() if len(gaps) > 0 else 0  # gaps > 24h
            })
    
    if consistency_data:
        df_consistency = pd.DataFrame(consistency_data)
        st.dataframe(df_consistency, use_container_width=True)
        
        st.info("📊 Esta tabela mostra a consistência temporal dos dados. Gaps grandes podem indicar períodos sem coleta de dados.")
