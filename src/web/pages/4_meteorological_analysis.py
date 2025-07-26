"""
Página de Análises Meteorológicas por Cidade

Esta página permite visualizar e analisar dados meteorológicos organizados por cidade,
utilizando tabs modulares para diferentes tipos de análises e visualizações.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
from geographic import CidadeRepository, RegiaoRepository, PaisRepository

# Importar funções modulares dos tabs
from web.pages.meteorological_analysis_tabs import (
    render_summary_tab,
    render_variation_graphs_tab,
    render_source_comparison_tab,
    render_full_table_tab,
    render_advanced_details_tab
)


def inicializar_repositorios():
    """Inicializa todos os repositórios necessários"""
    try:
        met_repo = MeteorologicalDataRepository()
        fonte_repo = MeteorologicalDataSourceRepository()
        cidade_repo = CidadeRepository()
        regiao_repo = RegiaoRepository()
        pais_repo = PaisRepository()
        
        return met_repo, fonte_repo, cidade_repo, regiao_repo, pais_repo
    except Exception as e:
        st.error(f"Erro ao inicializar repositórios: {e}")
        return None, None, None, None, None


def carregar_dados_cidade(cidade_id, met_repo, fonte_repo):
    """Carrega todos os dados meteorológicos de uma cidade"""
    try:
        # Buscar todos os dados da cidade
        dados_cidade = met_repo.buscar_por_cidade(cidade_id)
        
        if not dados_cidade:
            return None, None
        
        # Carregar informações das fontes
        fontes = {f.id: f for f in fonte_repo.listar_todos()}
        
        # Converter para DataFrame para análises
        df_data = []
        for dado in dados_cidade:
            df_data.append({
                'id': dado.id,
                'data_hora': dado.data_hora,
                'fonte': fontes.get(dado.meteorological_data_source_id, {}).name if dado.meteorological_data_source_id in fontes else 'Desconhecida',
                'fonte_id': dado.meteorological_data_source_id,
                'altura_captura': dado.altura_captura,
                'velocidade_vento': dado.velocidade_vento,
                'temperatura': dado.temperatura,
                'umidade': dado.umidade,
                'classificacao_vento': dado.classificar_vento(),
                'created_at': dado.created_at
            })
        
        df = pd.DataFrame(df_data)
        if not df.empty:
            # Normalizar timestamps para evitar problemas de timezone
            df['data_hora'] = pd.to_datetime(df['data_hora'], utc=True).dt.tz_localize(None)
            df = df.sort_values('data_hora')
        
        return dados_cidade, df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados da cidade: {e}")
        return None, None


def render_cidade_selector(cidades, regioes, paises):
    """Renderiza o seletor de cidade e gerencia session state"""
    st.markdown("""
    <div class="page-main-header">
        <h1>🌦️ Análises Meteorológicas por Cidade</h1>
        <p>Selecione uma cidade e explore as principais análises dos dados climáticos registrados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not cidades:
        st.markdown("""
        <div class='warning-box'>
            <h4>❌ Nenhuma cidade cadastrada</h4>
            <p>Cadastre cidades primeiro para visualizar análises meteorológicas.</p>
        </div>
        """, unsafe_allow_html=True)
        return None
    
    # Preparar opções de cidades
    opcoes_cidades = {}
    for cidade in cidades:
        regiao_nome = regioes.get(cidade.regiao_id, "N/A")
        pais_codigo = paises.get(cidade.pais_id, "N/A")
        display_text = f"{cidade.nome} - {regiao_nome} - {pais_codigo}"
        opcoes_cidades[display_text] = cidade
    
    # Seletor de cidade
    st.markdown("""
    <div class='section-header-minor'>
        <h4>🏙️ Selecione a Cidade para Análise</h4>
    </div>
    """, unsafe_allow_html=True)
    
    cidade_selecionada_text = st.selectbox(
        "Cidade para análise",
        options=list(opcoes_cidades.keys()),
        key="cidade_selector",
        help="Selecione a cidade cujos dados meteorológicos você deseja analisar"
    )
    
    cidade_selecionada = opcoes_cidades.get(cidade_selecionada_text)
    
    # Armazenar no session state
    if cidade_selecionada:
        st.session_state["cidade"] = cidade_selecionada
        st.info(f"📍 **Cidade selecionada:** {cidade_selecionada.nome} - Lat: {cidade_selecionada.latitude:.4f}, Lon: {cidade_selecionada.longitude:.4f}")
    
    return cidade_selecionada


def main():
    """Função principal da página de análises meteorológicas"""
    
    # Inicializar repositórios
    met_repo, fonte_repo, cidade_repo, regiao_repo, pais_repo = inicializar_repositorios()
    
    if not all([met_repo, fonte_repo, cidade_repo, regiao_repo, pais_repo]):
        st.error("Erro ao inicializar o sistema. Verifique a conexão com o banco de dados.")
        return
    
    # Carregar dados básicos
    try:
        cidades = cidade_repo.listar_todos()
        regioes = {r.id: r.nome for r in regiao_repo.listar_todos()}
        paises = {p.id: p.codigo for p in pais_repo.listar_todos()}
    except Exception as e:
        st.error(f"Erro ao carregar dados básicos: {e}")
        return
    
    # Renderizar seletor de cidade
    cidade_selecionada = render_cidade_selector(cidades, regioes, paises)
    
    if not cidade_selecionada:
        return
    
    # Carregar dados meteorológicos da cidade
    dados_cidade, df = carregar_dados_cidade(cidade_selecionada.id, met_repo, fonte_repo)
    
    # Criar tabs para análises
    st.markdown("---")
    
    tabs = st.tabs([
        "📊 Resumo Geral",
        "📈 Gráficos de Variação", 
        "🔍 Comparação entre Fontes",
        "📋 Tabela Completa",
        "🔬 Detalhamento Avançado"
    ])
    
    with tabs[0]:
        render_summary_tab(dados_cidade, df)
    
    with tabs[1]:
        render_variation_graphs_tab(df)
    
    with tabs[2]:
        render_source_comparison_tab(df)
    
    with tabs[3]:
        render_full_table_tab(df)
    
    with tabs[4]:
        render_advanced_details_tab(df)


if __name__ == "__main__":
    main()
