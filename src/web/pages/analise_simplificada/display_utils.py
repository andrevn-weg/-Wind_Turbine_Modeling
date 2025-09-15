"""
Módulo para visualização e exibição de dados da análise simplificada
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime


def exibir_valores_referencia_api(dados_por_fonte_altura):
    """
    Exibe valores de referência separados por fonte e altura de forma organizada.
    """
    if not dados_por_fonte_altura:
        st.info("📊 Nenhum dado encontrado para exibir valores de referência das APIs.")
        return
    
    st.subheader("📊 Valores de Referência das APIs por Fonte e Altura")
    
    # Organizar dados por fonte
    from .data_processor import organizar_por_fonte
    fontes_organizadas = organizar_por_fonte(dados_por_fonte_altura)
    
    # Criar tabs para cada fonte
    if len(fontes_organizadas) > 1:
        tabs = st.tabs(list(fontes_organizadas.keys()))
        
        for i, (fonte_nome, dados_fonte) in enumerate(fontes_organizadas.items()):
            with tabs[i]:
                _exibir_dados_fonte(dados_fonte, fonte_nome)
    else:
        # Se só há uma fonte, exibir diretamente
        fonte_nome, dados_fonte = list(fontes_organizadas.items())[0]
        _exibir_dados_fonte(dados_fonte, fonte_nome)


def _exibir_dados_fonte(dados_fonte, fonte_nome):
    """
    Exibe dados de uma fonte específica com suas diferentes alturas.
    """
    st.markdown(f"**{fonte_nome}**")
    
    # Criar colunas para cada altura
    if len(dados_fonte) > 1:
        cols = st.columns(len(dados_fonte))
        
        for i, (chave, info) in enumerate(dados_fonte):
            with cols[i]:
                _exibir_card_altura(chave, info)
    else:
        # Se só há uma altura, exibir em largura total
        chave, info = dados_fonte[0]
        _exibir_card_altura(chave, info)


def _exibir_card_altura(chave, info):
    """
    Exibe card com informações de uma altura específica.
    """
    with st.container():
        st.markdown(f"**{chave}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📊 Registros", f"{info['registros']:,}")
            st.metric("📈 Média", f"{info['media']:.2f} m/s")
            st.metric("📊 Mediana", f"{info['mediana']:.2f} m/s")
        
        with col2:
            st.metric("⬇️ Mínima", f"{info['minima']:.2f} m/s")
            st.metric("⬆️ Máxima", f"{info['maxima']:.2f} m/s")
            
            # Mostrar período de dados
            periodo = f"{info['data_inicio'].strftime('%d/%m/%Y')} a {info['data_fim'].strftime('%d/%m/%Y')}"
            st.caption(f"📅 Período: {periodo}")


def criar_grafico_comparacao_fontes(dados_por_fonte_altura):
    """
    Cria gráfico comparando estatísticas entre diferentes fontes e alturas.
    """
    if not dados_por_fonte_altura:
        return None
    
    # Preparar dados para o gráfico
    dados_graf = []
    for chave, info in dados_por_fonte_altura.items():
        dados_graf.append({
            'Fonte-Altura': chave,
            'Média': info['media'],
            'Mediana': info['mediana'],
            'Mínima': info['minima'],
            'Máxima': info['maxima'],
            'Registros': info['registros']
        })
    
    df = pd.DataFrame(dados_graf)
    
    # Criar gráfico de barras com múltiplas métricas
    fig = go.Figure()
    
    # Adicionar barras para cada métrica
    fig.add_trace(go.Bar(
        name='Média',
        x=df['Fonte-Altura'],
        y=df['Média'],
        marker_color='blue',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        name='Mediana',
        x=df['Fonte-Altura'],
        y=df['Mediana'],
        marker_color='green',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Comparação de Velocidades por Fonte e Altura',
        xaxis_title='Fonte e Altura',
        yaxis_title='Velocidade do Vento (m/s)',
        barmode='group',
        height=500
    )
    
    return fig


def criar_grafico_distribuicao_velocidades(dados_por_fonte_altura, chave_selecionada):
    """
    Cria histograma de distribuição de velocidades para uma fonte-altura específica.
    """
    if chave_selecionada not in dados_por_fonte_altura:
        return None
    
    info = dados_por_fonte_altura[chave_selecionada]
    velocidades = info['velocidades']
    
    fig = go.Figure(data=[go.Histogram(
        x=velocidades,
        nbinsx=30,
        marker_color='skyblue',
        opacity=0.7
    )])
    
    fig.update_layout(
        title=f'Distribuição de Velocidades - {chave_selecionada}',
        xaxis_title='Velocidade do Vento (m/s)',
        yaxis_title='Frequência',
        height=400
    )
    
    # Adicionar linhas para média e mediana
    fig.add_vline(x=info['media'], line_dash="dash", line_color="red", 
                  annotation_text=f"Média: {info['media']:.2f} m/s")
    fig.add_vline(x=info['mediana'], line_dash="dash", line_color="green", 
                  annotation_text=f"Mediana: {info['mediana']:.2f} m/s")
    
    return fig


def criar_tabela_resumo_fontes(dados_por_fonte_altura):
    """
    Cria tabela resumo com todas as fontes e suas estatísticas.
    """
    if not dados_por_fonte_altura:
        return None
    
    dados_tabela = []
    for chave, info in dados_por_fonte_altura.items():
        dados_tabela.append({
            'Fonte e Altura': chave,
            'Registros': f"{info['registros']:,}",
            'Média (m/s)': f"{info['media']:.2f}",
            'Mediana (m/s)': f"{info['mediana']:.2f}",
            'Mínima (m/s)': f"{info['minima']:.2f}",
            'Máxima (m/s)': f"{info['maxima']:.2f}",
            'Período': f"{info['data_inicio'].strftime('%d/%m/%Y')} - {info['data_fim'].strftime('%d/%m/%Y')}"
        })
    
    df = pd.DataFrame(dados_tabela)
    return df


def exibir_info_metodos_perfil():
    """
    Exibe informações sobre os métodos de perfil de vento.
    """
    with st.expander("ℹ️ Informações sobre Métodos de Perfil de Vento"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Lei da Potência**
            
            `v(h) = v_ref × (h/h_ref)^α`
            
            **Coeficiente α (rugosidade):**
            - 0.10: Água, campos abertos
            - 0.15: Terreno agrícola
            - 0.20: Áreas rurais dispersas
            - 0.25: Subúrbios, florestas
            - 0.30+: Áreas urbanas
            """)
        
        with col2:
            st.markdown("""
            **Perfil Logarítmico**
            
            `v(h) = v_ref × ln(h/z0) / ln(h_ref/z0)`
            
            **Comprimento z0 (rugosidade):**
            - 0.0002m: Água calma
            - 0.01m: Campos abertos
            - 0.1m: Áreas agrícolas
            - 1.0m: Florestas
            - 2.0m+: Áreas urbanas
            """)


def exibir_alerta_dados_insuficientes():
    """
    Exibe alerta quando não há dados suficientes.
    """
    st.warning("""
    ⚠️ **Dados Insuficientes**
    
    Não foram encontrados dados meteorológicos no período e fonte selecionados.
    
    **Sugestões:**
    - Verifique se o período selecionado possui dados
    - Tente selecionar "Todos" na fonte de dados
    - Verifique se há dados meteorológicos cadastrados para este local
    """)


def formatar_numero_brasileiro(numero, decimais=2):
    """
    Formata número no padrão brasileiro (vírgula decimal, ponto milhares).
    """
    if numero is None:
        return "N/A"
    
    return f"{numero:,.{decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")