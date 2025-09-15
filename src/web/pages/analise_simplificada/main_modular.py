"""
Módulo principal da análise simplificada - versão modular
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

# Adicionar diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from database.repositories.MeteorologicalDataRepository import MeteorologicalDataRepository
from database.repositories.GeographicLocationRepository import GeographicLocationRepository
from database.repositories.MeteorologicalDataSourceRepository import MeteorologicalDataSourceRepository

# Imports dos módulos locais
from .config import *
from .data_processor import *
from .wind_profile import *
from .display_utils import *


def main():
    """
    Função principal da análise simplificada modular.
    """
    st.title("🌪️ Análise Simplificada de Vento - Versão Modular")
    
    # Inicializar repositórios
    try:
        met_repo = MeteorologicalDataRepository()
        geo_repo = GeographicLocationRepository()
        source_repo = MeteorologicalDataSourceRepository()
    except Exception as e:
        st.error(f"❌ Erro ao conectar com banco de dados: {e}")
        return
    
    # Sidebar com controles
    configurar_sidebar(geo_repo, source_repo)
    
    # Verificar se local foi selecionado
    if 'local_selecionado' not in st.session_state or not st.session_state.local_selecionado:
        st.info("👈 Selecione um local geográfico na barra lateral para começar a análise.")
        return
    
    # Executar análise principal
    executar_analise_principal(met_repo, source_repo)


def configurar_sidebar(geo_repo, source_repo):
    """
    Configura sidebar com controles de parâmetros.
    """
    with st.sidebar:
        st.header("⚙️ Configurações da Análise")
        
        # Seleção de local geográfico
        configurar_selecao_local(geo_repo)
        
        # Configurações de análise
        configurar_parametros_analise()
        
        # Configurações de perfil de vento
        configurar_parametros_perfil()
        
        # Informações sobre métodos
        exibir_info_metodos_perfil()


def configurar_selecao_local(geo_repo):
    """
    Configura seleção de local geográfico.
    """
    st.subheader("📍 Local de Análise")
    
    try:
        locais = geo_repo.get_all()
        if not locais:
            st.warning("⚠️ Nenhum local geográfico cadastrado.")
            return
        
        opcoes_locais = [f"{local.nome} ({local.estado})" for local in locais]
        
        local_selecionado = st.selectbox(
            "Selecione o local:",
            opcoes_locais,
            key="selectbox_local",
            help=HELP_MESSAGES['fonte_dados']
        )
        
        if local_selecionado:
            indice = opcoes_locais.index(local_selecionado)
            st.session_state.local_selecionado = locais[indice]
            
            # Exibir informações do local
            local = st.session_state.local_selecionado
            st.info(f"""
            **📍 Local Selecionado:**
            - **Nome:** {local.nome}
            - **Estado:** {local.estado}
            - **Coordenadas:** {local.latitude:.4f}, {local.longitude:.4f}
            """)
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar locais: {e}")


def configurar_parametros_analise():
    """
    Configura parâmetros gerais da análise.
    """
    st.subheader("📊 Parâmetros de Análise")
    
    # Período de análise
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input(
            "Data Início:",
            value=date.today() - timedelta(days=30),
            key="data_inicio",
            help=HELP_MESSAGES['periodo_analise']
        )
    
    with col2:
        data_fim = st.date_input(
            "Data Fim:",
            value=date.today(),
            key="data_fim",
            help=HELP_MESSAGES['periodo_analise']
        )
    
    st.session_state.data_inicio = data_inicio
    st.session_state.data_fim = data_fim
    
    # Fonte de dados
    fonte_dados = st.selectbox(
        "Fonte de Dados:",
        OPCOES_FONTE_DADOS,
        index=2,  # "todos" como padrão
        key="fonte_dados",
        help=HELP_MESSAGES['fonte_dados']
    )
    
    st.session_state.fonte_dados = fonte_dados


def configurar_parametros_perfil():
    """
    Configura parâmetros do perfil de vento.
    """
    st.subheader("🌬️ Perfil de Vento")
    
    # Altura da turbina
    altura_turbina = st.number_input(
        "Altura da Turbina (m):",
        min_value=LIMITES_VALIDACAO['altura_min'],
        max_value=LIMITES_VALIDACAO['altura_max'],
        value=CONFIGURACOES_PADRAO['altura_turbina'],
        step=1.0,
        key="altura_turbina",
        help=HELP_MESSAGES['altura_turbina']
    )
    
    st.session_state.altura_turbina = altura_turbina
    
    # Tipo de terreno
    tipo_terreno = st.selectbox(
        "Tipo de Terreno:",
        list(TIPOS_TERRENO.keys()),
        format_func=lambda x: TIPOS_TERRENO[x]['nome'],
        index=2,  # 'rural_disperso' como padrão
        key="tipo_terreno",
        help=HELP_MESSAGES['rugosidade_terreno']
    )
    
    st.session_state.tipo_terreno = tipo_terreno
    
    # Mostrar descrição do terreno
    terreno_info = TIPOS_TERRENO[tipo_terreno]
    st.caption(f"💡 {terreno_info['descricao']}")
    
    # Método de cálculo
    metodo_perfil = st.radio(
        "Método de Cálculo:",
        ["power_law", "logarithmic"],
        format_func=lambda x: "Lei da Potência" if x == "power_law" else "Perfil Logarítmico",
        key="metodo_perfil",
        help=HELP_MESSAGES['metodo_perfil']
    )
    
    st.session_state.metodo_perfil = metodo_perfil
    
    # Mostrar parâmetros de rugosidade
    if metodo_perfil == "power_law":
        st.caption(f"📐 Coeficiente α: {terreno_info['alpha']}")
    else:
        st.caption(f"📐 Comprimento z₀: {terreno_info['z0']} m")


def executar_analise_principal(met_repo, source_repo):
    """
    Executa a análise principal com os parâmetros configurados.
    """
    local = st.session_state.local_selecionado
    
    # Carregar dados meteorológicos
    with st.spinner("🔄 Carregando dados meteorológicos..."):
        dados_originais = carregar_dados_meteorologicos(met_repo, local.id)
    
    if not dados_originais:
        exibir_alerta_dados_insuficientes()
        return
    
    # Carregar fontes de dados
    fontes = source_repo.get_all()
    source_map = obter_mapeamento_fontes_correto(fontes)
    
    # Filtrar dados por período e fonte
    dados_filtrados, mensagem_filtro = filtrar_dados_por_fonte_e_periodo(
        dados_originais,
        st.session_state.fonte_dados,
        source_map,
        st.session_state.data_inicio,
        st.session_state.data_fim
    )
    
    st.info(mensagem_filtro)
    
    if not dados_filtrados:
        exibir_alerta_dados_insuficientes()
        return
    
    # Agrupar dados por fonte e altura
    dados_por_fonte_altura = agrupar_dados_por_fonte_altura(dados_filtrados, fontes)
    dados_por_fonte_altura = calcular_estatisticas_por_grupo(dados_por_fonte_altura)
    
    # Exibir valores de referência das APIs
    exibir_valores_referencia_api(dados_por_fonte_altura)
    
    # Executar análise de perfil de vento
    executar_analise_perfil_vento(dados_por_fonte_altura)
    
    # Exibir gráficos e tabelas
    exibir_visualizacoes(dados_por_fonte_altura)


def carregar_dados_meteorologicos(met_repo, location_id):
    """
    Carrega dados meteorológicos para um local específico.
    """
    try:
        dados = met_repo.get_by_location_id(location_id)
        return dados
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados meteorológicos: {e}")
        return []


def executar_analise_perfil_vento(dados_por_fonte_altura):
    """
    Executa análise de perfil de vento para cada grupo fonte-altura.
    """
    if not dados_por_fonte_altura:
        return
    
    st.subheader("🌬️ Análise de Perfil de Vento")
    
    # Obter parâmetros de rugosidade
    tipo_terreno = st.session_state.tipo_terreno
    terreno_info = TIPOS_TERRENO[tipo_terreno]
    
    altura_turbina = st.session_state.altura_turbina
    metodo_perfil = st.session_state.metodo_perfil
    
    # Calcular velocidades corrigidas para cada grupo
    resultados_perfil = {}
    
    for chave, info in dados_por_fonte_altura.items():
        altura_ref = info['altura']
        velocidade_media = info['media']
        
        if metodo_perfil == "power_law":
            rugosidade = terreno_info['alpha']
        else:
            rugosidade = terreno_info['z0']
        
        velocidade_corrigida = calcular_velocidade_corrigida(
            velocidade_media,
            altura_ref,
            altura_turbina,
            rugosidade,
            metodo_perfil
        )
        
        resultados_perfil[chave] = {
            'velocidade_original': velocidade_media,
            'altura_original': altura_ref,
            'velocidade_corrigida': velocidade_corrigida,
            'altura_turbina': altura_turbina,
            'fator_correcao': velocidade_corrigida / velocidade_media if velocidade_media > 0 else 1
        }
    
    # Exibir resultados
    exibir_resultados_perfil(resultados_perfil, metodo_perfil, terreno_info)


def exibir_resultados_perfil(resultados_perfil, metodo_perfil, terreno_info):
    """
    Exibe resultados da análise de perfil de vento.
    """
    st.subheader("📊 Velocidades Corrigidas para Altura da Turbina")
    
    # Criar tabela de resultados
    dados_tabela = []
    for chave, resultado in resultados_perfil.items():
        dados_tabela.append({
            'Fonte e Altura': chave,
            'Velocidade Original (m/s)': f"{resultado['velocidade_original']:.2f}",
            'Altura Original (m)': f"{resultado['altura_original']:.0f}",
            'Velocidade Corrigida (m/s)': f"{resultado['velocidade_corrigida']:.2f}",
            'Altura Turbina (m)': f"{resultado['altura_turbina']:.0f}",
            'Fator de Correção': f"{resultado['fator_correcao']:.3f}"
        })
    
    df_resultados = pd.DataFrame(dados_tabela)
    st.dataframe(df_resultados, use_container_width=True)
    
    # Exibir informações do método usado
    metodo_nome = "Lei da Potência" if metodo_perfil == "power_law" else "Perfil Logarítmico"
    
    st.info(f"""
    **🔬 Método Utilizado:** {metodo_nome}
    
    **🏞️ Tipo de Terreno:** {terreno_info['nome']}
    
    **📐 Parâmetro de Rugosidade:** {terreno_info['alpha'] if metodo_perfil == 'power_law' else terreno_info['z0']} {'(α)' if metodo_perfil == 'power_law' else '(z₀ em metros)'}
    """)


def exibir_visualizacoes(dados_por_fonte_altura):
    """
    Exibe gráficos e visualizações dos dados.
    """
    if not dados_por_fonte_altura:
        return
    
    st.subheader("📈 Visualizações")
    
    # Gráfico de comparação
    fig_comparacao = criar_grafico_comparacao_fontes(dados_por_fonte_altura)
    if fig_comparacao:
        st.plotly_chart(fig_comparacao, use_container_width=True)
    
    # Seletor para histograma
    chaves_disponiveis = list(dados_por_fonte_altura.keys())
    if len(chaves_disponiveis) > 1:
        chave_hist = st.selectbox(
            "Selecione fonte-altura para histograma:",
            chaves_disponiveis,
            key="chave_histograma"
        )
        
        fig_hist = criar_grafico_distribuicao_velocidades(dados_por_fonte_altura, chave_hist)
        if fig_hist:
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # Tabela resumo
    st.subheader("📋 Resumo Completo")
    df_resumo = criar_tabela_resumo_fontes(dados_por_fonte_altura)
    if df_resumo is not None:
        st.dataframe(df_resumo, use_container_width=True)


if __name__ == "__main__":
    main()