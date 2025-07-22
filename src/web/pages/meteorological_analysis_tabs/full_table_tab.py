"""
Tab de Tabela Completa - Análises Meteorológicas

Contém a funcionalidade da aba "Tabela Completa" com visualização tabular
detalhada dos dados meteorológicos com filtros por fonte e altura.
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render_full_table_tab(df):
    """
    Renderiza a aba de Tabela Completa dos dados meteorológicos
    
    Args:
        df: DataFrame com dados meteorológicos processados
    """
    if df is None or df.empty:
        st.warning("Nenhum dado disponível.")
        return
    
    st.markdown("""
    <div class='section-header-minor'>
        <h4>📋 Tabela Completa dos Dados Meteorológicos</h4>
        <p>Visualização detalhada com filtros por fonte, altura e período.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros organizados
    st.subheader("🔍 Filtros de Dados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filtro por fonte
        fontes_disponiveis = ['Todas'] + sorted(list(df['fonte'].unique()))
        fonte_filtro = st.selectbox("Fonte de Dados", fontes_disponiveis, key="fonte_filter")
    
    with col2:
        # Filtro por altura
        alturas_disponiveis = ['Todas'] + sorted([str(x) for x in df['altura_captura'].dropna().unique()])
        altura_filtro = st.selectbox("Altura de Captura", alturas_disponiveis, key="altura_filter")
    
    with col3:
        # Filtro de período
        data_min = df['data_hora'].min().date()
        data_max = df['data_hora'].max().date()
        data_inicio = st.date_input(
            "Data Início", 
            value=data_min, 
            min_value=data_min, 
            max_value=data_max,
            key="data_inicio_filter"
        )
    
    with col4:
        data_fim = st.date_input(
            "Data Fim", 
            value=data_max, 
            min_value=data_min, 
            max_value=data_max,
            key="data_fim_filter"
        )
    
    # Filtros adicionais
    col5, col6, col7 = st.columns(3)
    
    with col5:
        # Filtro por classificação do vento
        if 'classificacao_vento' in df.columns:
            classificacoes = ['Todas'] + sorted(list(df['classificacao_vento'].dropna().unique()))
            classificacao_filtro = st.selectbox("Classificação do Vento", classificacoes, key="class_filter")
        else:
            classificacao_filtro = 'Todas'
    
    with col6:
        # Filtro por faixa de velocidade do vento
        vento_min = float(df['velocidade_vento'].min())
        vento_max = float(df['velocidade_vento'].max())
        vento_range = st.slider(
            "Faixa Velocidade Vento (m/s)",
            min_value=vento_min,
            max_value=vento_max,
            value=(vento_min, vento_max),
            step=0.1,
            key="vento_range_filter"
        )
    
    with col7:
        # Limite de registros para exibição
        limite_registros = st.selectbox(
            "Limite de Registros",
            [100, 500, 1000, 5000, "Todos"],
            index=1,
            key="limite_filter"
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro por fonte
    if fonte_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['fonte'] == fonte_filtro]
    
    # Filtro por altura
    if altura_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['altura_captura'] == float(altura_filtro)]
    
    # Filtro por período
    df_filtrado = df_filtrado[
        (df_filtrado['data_hora'].dt.date >= data_inicio) & 
        (df_filtrado['data_hora'].dt.date <= data_fim)
    ]
    
    # Filtro por classificação
    if classificacao_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['classificacao_vento'] == classificacao_filtro]
    
    # Filtro por velocidade do vento
    df_filtrado = df_filtrado[
        (df_filtrado['velocidade_vento'] >= vento_range[0]) &
        (df_filtrado['velocidade_vento'] <= vento_range[1])
    ]
    
    # Aplicar limite de registros
    if limite_registros != "Todos":
        df_filtrado = df_filtrado.tail(limite_registros)
    
    # Mostrar estatísticas dos dados filtrados
    st.markdown("---")
    st.subheader("📊 Resumo dos Dados Filtrados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", len(df_filtrado))
    
    with col2:
        if not df_filtrado.empty:
            vento_medio_filtrado = df_filtrado['velocidade_vento'].mean()
            st.metric("Vento Médio (m/s)", f"{vento_medio_filtrado:.2f}")
        else:
            st.metric("Vento Médio (m/s)", "N/A")
    
    with col3:
        if not df_filtrado.empty:
            fontes_filtradas = df_filtrado['fonte'].nunique()
            st.metric("Fontes Únicas", fontes_filtradas)
        else:
            st.metric("Fontes Únicas", 0)
    
    with col4:
        if not df_filtrado.empty:
            alturas_filtradas = df_filtrado['altura_captura'].nunique()
            st.metric("Alturas Únicas", alturas_filtradas)
        else:
            st.metric("Alturas Únicas", 0)
    
    # Exibir tabela filtrada
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados.")
        return
    
    st.markdown("---")
    st.subheader("📋 Dados Detalhados")
    
    # Preparar colunas para exibição
    colunas_exibicao = [
        'data_hora', 
        'fonte', 
        'altura_captura', 
        'velocidade_vento', 
        'classificacao_vento'
    ]
    
    # Adicionar colunas opcionais se disponíveis
    if 'temperatura' in df_filtrado.columns and df_filtrado['temperatura'].notna().any():
        colunas_exibicao.insert(-1, 'temperatura')
    
    if 'umidade' in df_filtrado.columns and df_filtrado['umidade'].notna().any():
        colunas_exibicao.insert(-1, 'umidade')
    
    # Configurar exibição da tabela
    df_display = df_filtrado[colunas_exibicao].copy()
    
    # Formatar colunas para melhor visualização
    df_display['data_hora'] = df_display['data_hora'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_display['velocidade_vento'] = df_display['velocidade_vento'].round(2)
    
    if 'temperatura' in df_display.columns:
        df_display['temperatura'] = df_display['temperatura'].round(1)
    
    if 'umidade' in df_display.columns:
        df_display['umidade'] = df_display['umidade'].round(1)
    
    # Renomear colunas para melhor legibilidade
    rename_columns = {
        'data_hora': 'Data/Hora',
        'fonte': 'Fonte',
        'altura_captura': 'Altura (m)',
        'velocidade_vento': 'Vento (m/s)',
        'temperatura': 'Temp (°C)',
        'umidade': 'Umidade (%)',
        'classificacao_vento': 'Classificação'
    }
    
    df_display.rename(columns=rename_columns, inplace=True)
    
    # Exibir tabela com configuração avançada
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=600
    )
    
    # Seção de exportação
    st.markdown("---")
    st.subheader("📥 Exportar Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Botão de download CSV
        if not df_filtrado.empty:
            csv = df_filtrado[colunas_exibicao].to_csv(index=False)
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"dados_meteorologicos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        # Estatísticas para download
        if not df_filtrado.empty:
            stats_df = df_filtrado.groupby(['fonte', 'altura_captura']).agg({
                'velocidade_vento': ['count', 'mean', 'std', 'min', 'max'],
                'temperatura': 'mean',
                'umidade': 'mean'
            }).round(2)
            
            stats_csv = stats_df.to_csv()
            st.download_button(
                label="📊 Baixar Estatísticas",
                data=stats_csv,
                file_name=f"estatisticas_meteorologicas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Informações sobre os filtros aplicados
        if st.button("📋 Resumo dos Filtros"):
            filtros_aplicados = {
                'Fonte': fonte_filtro,
                'Altura': altura_filtro,
                'Período': f"{data_inicio} a {data_fim}",
                'Classificação Vento': classificacao_filtro,
                'Faixa Velocidade': f"{vento_range[0]} - {vento_range[1]} m/s",
                'Limite Registros': limite_registros,
                'Total Encontrado': len(df_filtrado)
            }
            
            st.json(filtros_aplicados)
    
    # Análise rápida dos dados filtrados
    if not df_filtrado.empty and len(df_filtrado) > 1:
        st.markdown("---")
        st.subheader("⚡ Análise Rápida dos Dados Filtrados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌪️ Velocidade do Vento**")
            vento_stats = df_filtrado['velocidade_vento'].describe()
            st.write(f"• Média: {vento_stats['mean']:.2f} m/s")
            st.write(f"• Desvio Padrão: {vento_stats['std']:.2f} m/s")
            st.write(f"• Mínimo: {vento_stats['min']:.2f} m/s")
            st.write(f"• Máximo: {vento_stats['max']:.2f} m/s")
        
        with col2:
            st.markdown("**📊 Distribuição por Fonte/Altura**")
            distribuicao = df_filtrado.groupby(['fonte', 'altura_captura']).size()
            for (fonte, altura), count in distribuicao.items():
                st.write(f"• {fonte} - {altura}m: {count} registros")
