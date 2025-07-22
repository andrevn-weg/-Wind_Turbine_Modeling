"""
Tab de Resumo Geral - Análises Meteorológicas

Contém a funcionalidade da aba "Resumo Geral" com estatísticas
gerais dos dados meteorológicos organizados por fonte e altura.
"""

import streamlit as st
import pandas as pd


def render_summary_tab(dados_cidade, df):
    """
    Renderiza a aba de Resumo Geral dos dados meteorológicos
    
    Args:
        dados_cidade: Lista de objetos MeteorologicalData
        df: DataFrame com dados meteorológicos processados
    """
    if df is None or df.empty:
        st.markdown("""
        <div class='warning-box'>
            <h4>📊 Nenhum dado disponível</h4>
            <p>Não há dados meteorológicos registrados para esta cidade.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="wind-info-card">
            <h4 class="wind-info-title">📈 Total de Registros</h4>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Registros", len(df))
    
    with col2:
        st.markdown("""
        <div class="wind-info-card">
            <h4 class="wind-info-title">📅 Período dos Dados</h4>
        </div>
        """, unsafe_allow_html=True)
        periodo_dias = (df['data_hora'].max() - df['data_hora'].min()).days
        st.metric("Dias", f"{periodo_dias + 1}")
    
    with col3:
        st.markdown("""
        <div class="wind-info-card">
            <h4 class="wind-info-title">🌪️ Vento Médio</h4>
        </div>
        """, unsafe_allow_html=True)
        vento_medio = df['velocidade_vento'].mean() if 'velocidade_vento' in df.columns else 0
        st.metric("m/s", f"{vento_medio:.2f}")
    
    with col4:
        st.markdown("""
        <div class="wind-info-card">
            <h4 class="wind-info-title">🔗 Fontes de Dados</h4>
        </div>
        """, unsafe_allow_html=True)
        fontes_unicas = df['fonte'].nunique()
        st.metric("Fontes", fontes_unicas)
    
    # Resumo por fonte e altura
    st.markdown("---")
    st.markdown("""
    <div class='section-header-minor'>
        <h4>📋 Resumo por Fonte e Altura de Captura</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar resumo agrupado por fonte e altura
    resumo_fonte_altura = df.groupby(['fonte', 'altura_captura']).agg({
        'velocidade_vento': ['count', 'mean', 'std', 'min', 'max'],
        'temperatura': ['count', 'mean'],
        'umidade': ['count', 'mean'],
        'data_hora': ['min', 'max']
    }).round(2)
    
    # Flatten column names
    resumo_fonte_altura.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in resumo_fonte_altura.columns]
    
    # Renomear colunas para melhor legibilidade
    rename_dict = {
        'velocidade_vento_count': 'Registros',
        'velocidade_vento_mean': 'Vento Médio (m/s)',
        'velocidade_vento_std': 'Desvio Padrão Vento',
        'velocidade_vento_min': 'Vento Mín (m/s)',
        'velocidade_vento_max': 'Vento Máx (m/s)',
        'temperatura_count': 'Registros Temp',
        'temperatura_mean': 'Temp Média (°C)',
        'umidade_count': 'Registros Umidade', 
        'umidade_mean': 'Umidade Média (%)',
        'data_hora_min': 'Primeiro Registro',
        'data_hora_max': 'Último Registro'
    }
    
    resumo_fonte_altura.rename(columns=rename_dict, inplace=True)
    
    # Exibir tabela com índice visível
    st.dataframe(
        resumo_fonte_altura,
        use_container_width=True,
        height=300
    )
    
    # Últimos registros por fonte/altura
    st.markdown("---")
    st.markdown("""
    <div class='section-header-minor'>
        <h4>📋 Últimos 5 Registros por Fonte/Altura</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Agrupar por fonte e altura para mostrar últimos registros
    combinacoes = df.groupby(['fonte', 'altura_captura'])
    
    for (fonte, altura), grupo in combinacoes:
        st.markdown(f"**{fonte} - {altura}m**")
        
        ultimos_registros = grupo.tail(5)[['data_hora', 'velocidade_vento', 'temperatura', 'umidade', 'classificacao_vento']]
        st.dataframe(
            ultimos_registros,
            use_container_width=True,
            hide_index=True,
            height=200
        )
        st.markdown("---")
    
    # Estatísticas de qualidade dos dados
    st.markdown("""
    <div class='section-header-minor'>
        <h4>📊 Qualidade dos Dados</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🌪️ Velocidade do Vento**")
        vento_validos = df['velocidade_vento'].notna().sum()
        vento_total = len(df)
        vento_percent = (vento_validos / vento_total * 100) if vento_total > 0 else 0
        st.metric("Completude", f"{vento_percent:.1f}%", f"{vento_validos}/{vento_total}")
    
    with col2:
        st.markdown("**🌡️ Temperatura**")
        if 'temperatura' in df.columns:
            temp_validos = df['temperatura'].notna().sum()
            temp_percent = (temp_validos / vento_total * 100) if vento_total > 0 else 0
            st.metric("Completude", f"{temp_percent:.1f}%", f"{temp_validos}/{vento_total}")
        else:
            st.metric("Completude", "0%", "0/0")
    
    with col3:
        st.markdown("**💧 Umidade**")
        if 'umidade' in df.columns:
            umidade_validos = df['umidade'].notna().sum()
            umidade_percent = (umidade_validos / vento_total * 100) if vento_total > 0 else 0
            st.metric("Completude", f"{umidade_percent:.1f}%", f"{umidade_validos}/{vento_total}")
        else:
            st.metric("Completude", "0%", "0/0")
