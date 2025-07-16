"""
Página de Coleta de Dados Climáticos - Sistema de Coleta e Armazenamento.

Esta página permite coletar dados climáticos de APIs externas,
gerenciar localidades e configurar coletas automáticas.

Autor: André Vinícius Lima do Nascimento
Data: Janeiro 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import numpy as np
from pathlib import Path
import os
import sys

# Adicionar src ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports do projeto
from utils.css_loader import load_css
from climate import (
    ColetaDadosService,
    GerenciamentoLocalizacoesService,
    LocalizacaoClimaticaRepository,
    DadosClimaticosRepository,
    api_client
)

# Carregar CSS
css_path = os.path.join(project_root, "web", "static", "styles.css")
load_css(css_path)

def main():
    """Função principal da página de coleta de dados."""
    
    # Título da página
    st.markdown("""
    <div class="page-main-header">
        <h1>📥 Coleta de <span style="color: rgb(46, 204, 113);">Dados</span></h1>
        <p>Coleta e Armazenamento de Dados Climáticos</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inicializar serviços
    coleta_service = ColetaDadosService()
    gerenciamento_service = GerenciamentoLocalizacoesService()
    localizacao_repo = LocalizacaoClimaticaRepository()
    dados_repo = DadosClimaticosRepository()
    
    # Tabs para diferentes seções
    tabs = st.tabs([
        "🌍 Nova Localidade", 
        "📋 Coleta Manual", 
        "⚡ Coleta Rápida",
        "🗂️ Dados Armazenados"
    ])
    
    with tabs[0]:
        nova_localidade_tab(gerenciamento_service, localizacao_repo)
    
    with tabs[1]:
        coleta_manual_tab(coleta_service, localizacao_repo)
    
    with tabs[2]:
        coleta_rapida_tab(coleta_service)
    
    with tabs[3]:
        dados_armazenados_tab(dados_repo, localizacao_repo)

def nova_localidade_tab(gerenciamento_service, localizacao_repo):
    """Tab para cadastrar nova localidade."""
    
    st.markdown("### 🌍 Cadastrar Nova Localidade")
    st.markdown("Adicione uma nova localidade para monitoramento climático contínuo.")
    
    # Formulário de cadastro
    with st.form("nova_localidade_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome da Localidade *",
                placeholder="Ex: Jaraguá do Sul",
                help="Nome identificador da localidade"
            )
            
            latitude = st.number_input(
                "Latitude *", 
                value=0.0, 
                min_value=-90.0, 
                max_value=90.0,
                format="%.6f",
                help="Latitude em graus decimais"
            )
        
        with col2:
            descricao = st.text_area(
                "Descrição (opcional)",
                placeholder="Ex: Região industrial, próxima ao mar...",
                help="Descrição adicional da localidade"
            )
            
            longitude = st.number_input(
                "Longitude *", 
                value=0.0, 
                min_value=-180.0, 
                max_value=180.0,
                format="%.6f",
                help="Longitude em graus decimais"
            )
        
        # Opções de coleta inicial
        st.markdown("**Coleta Inicial de Dados:**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            coletar_dados_iniciais = st.checkbox(
                "Coletar dados históricos",
                value=True,
                help="Coletar dados climáticos históricos ao cadastrar"
            )
        
        with col4:
            if coletar_dados_iniciais:
                periodo_inicial = st.select_slider(
                    "Período inicial (dias)",
                    options=[7, 15, 30, 60, 90, 180, 365],
                    value=30,
                    help="Quantos dias de histórico coletar"
                )
            else:
                periodo_inicial = 0
        
        submitted = st.form_submit_button("🌍 Cadastrar Localidade")
    
    if submitted:
        if not nome or latitude == 0.0 or longitude == 0.0:
            st.error("Por favor, preencha todos os campos obrigatórios.")
        else:
            with st.spinner("Cadastrando localidade..."):
                try:
                    # Verificar se já existe
                    localidades_existentes = localizacao_repo.listar_todas()
                    if any(loc.nome.lower() == nome.lower() for loc in localidades_existentes):
                        st.warning("⚠️ Já existe uma localidade com este nome.")
                        return
                    
                    # Cadastrar localidade
                    localizacao_id = gerenciamento_service.cadastrar_localizacao(
                        nome, latitude, longitude, descricao
                    )
                    
                    st.success(f"✅ Localidade '{nome}' cadastrada com sucesso!")
                    
                    # Coletar dados iniciais se solicitado
                    if coletar_dados_iniciais and periodo_inicial > 0:
                        with st.spinner("Coletando dados históricos..."):
                            try:
                                dados_coletados = gerenciamento_service.coletar_dados_localizacao(
                                    localizacao_id, periodo_inicial
                                )
                                
                                if dados_coletados:
                                    st.success(f"📊 Coletados {len(dados_coletados)} registros de dados históricos!")
                                else:
                                    st.warning("Não foi possível coletar dados históricos.")
                            
                            except Exception as e:
                                st.error(f"Erro ao coletar dados históricos: {str(e)}")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro ao cadastrar localidade: {str(e)}")

def coleta_manual_tab(coleta_service, localizacao_repo):
    """Tab para coleta manual de dados."""
    
    st.markdown("### 📋 Coleta Manual de Dados")
    st.markdown("Colete dados climáticos para localidades específicas com controle total dos parâmetros.")
    
    # Listar localidades cadastradas
    localidades = localizacao_repo.listar_todas()
    
    if not localidades:
        st.info("📍 Cadastre uma localidade na aba 'Nova Localidade' para começar.")
        return
    
    # Formulário de coleta
    with st.form("coleta_manual_form"):
        # Seleção de localidade
        nomes_localidades = [f"{loc.nome} ({loc.latitude:.4f}, {loc.longitude:.4f})" 
                           for loc in localidades]
        
        localidade_selecionada_idx = st.selectbox(
            "Localidade",
            range(len(nomes_localidades)),
            format_func=lambda x: nomes_localidades[x],
            help="Selecione a localidade para coleta"
        )
        
        localidade_selecionada = localidades[localidade_selecionada_idx]
        
        # Parâmetros de coleta
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_coleta = st.selectbox(
                "Tipo de Coleta",
                ["Histórico", "Previsão", "Ano Completo"],
                help="Tipo de dados a coletar"
            )
            
            if tipo_coleta == "Histórico":
                periodo_dias = st.number_input(
                    "Período (dias)",
                    min_value=1,
                    max_value=365,
                    value=30,
                    help="Número de dias para coleta histórica"
                )
            elif tipo_coleta == "Previsão":
                periodo_dias = st.number_input(
                    "Dias de Previsão",
                    min_value=1,
                    max_value=14,
                    value=7,
                    help="Número de dias de previsão"
                )
            else:  # Ano Completo
                ano_coleta = st.number_input(
                    "Ano",
                    min_value=2020,
                    max_value=datetime.now().year,
                    value=datetime.now().year - 1,
                    help="Ano para coleta completa"
                )
        
        with col2:
            # Opções avançadas
            st.markdown("**Opções Avançadas:**")
            
            salvar_dados = st.checkbox(
                "Salvar no banco de dados",
                value=True,
                help="Salvar dados coletados no banco local"
            )
            
            mostrar_preview = st.checkbox(
                "Mostrar preview dos dados",
                value=True,
                help="Exibir amostra dos dados coletados"
            )
            
            if tipo_coleta == "Histórico":
                sobrescrever = st.checkbox(
                    "Sobrescrever dados existentes",
                    value=False,
                    help="Sobrescrever dados que já existem no banco"
                )
        
        submitted = st.form_submit_button("📥 Coletar Dados")
    
    if submitted:
        with st.spinner(f"Coletando dados {tipo_coleta.lower()}..."):
            try:
                dados_coletados = None
                
                if tipo_coleta == "Histórico":
                    dados_coletados = coleta_service.coletar_dados_historicos(
                        localidade_selecionada.latitude,
                        localidade_selecionada.longitude,
                        localidade_selecionada.nome,
                        periodo_dias
                    )
                elif tipo_coleta == "Previsão":
                    dados_coletados = coleta_service.coletar_dados_previsao(
                        localidade_selecionada.latitude,
                        localidade_selecionada.longitude,
                        localidade_selecionada.nome,
                        periodo_dias
                    )
                else:  # Ano Completo
                    dados_coletados = coleta_service.coletar_dados_ano_completo(
                        localidade_selecionada.latitude,
                        localidade_selecionada.longitude,
                        localidade_selecionada.nome,
                        ano_coleta
                    )
                
                if dados_coletados:
                    st.success(f"✅ Coletados {len(dados_coletados)} registros de dados!")
                    
                    # Mostrar preview se solicitado
                    if mostrar_preview:
                        mostrar_preview_dados(dados_coletados)
                    
                    # Salvar se solicitado
                    if salvar_dados:
                        with st.spinner("Salvando dados no banco..."):
                            dados_salvos = 0
                            for dado in dados_coletados:
                                # Associar à localização
                                dado.localizacao_id = localidade_selecionada.id
                                dados_salvos += 1
                            
                            st.success(f"💾 {dados_salvos} registros salvos no banco de dados!")
                
                else:
                    st.error("Não foi possível coletar dados para esta localidade.")
                    
            except Exception as e:
                st.error(f"Erro ao coletar dados: {str(e)}")

def coleta_rapida_tab(coleta_service):
    """Tab para coleta rápida sem salvar."""
    
    st.markdown("### ⚡ Coleta Rápida")
    st.markdown("Coleta rápida de dados para análise imediata sem salvar no banco.")
    
    # Formulário simples
    with st.form("coleta_rapida_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latitude = st.number_input("Latitude", value=-26.52, format="%.6f")
            longitude = st.number_input("Longitude", value=-49.06, format="%.6f")
        
        with col2:
            nome_local = st.text_input("Nome Local", value="Local Temporário")
            periodo_dias = st.selectbox("Período", [1, 3, 7, 15, 30], index=2)
        
        with col3:
            st.markdown("**Dados a Coletar:**")
            incluir_temperatura = st.checkbox("Temperatura", value=True)
            incluir_umidade = st.checkbox("Umidade", value=True)
            incluir_pressao = st.checkbox("Pressão", value=False)
        
        submitted = st.form_submit_button("⚡ Coleta Rápida")
    
    if submitted:
        with st.spinner("Realizando coleta rápida..."):
            try:
                dados = coleta_service.coletar_dados_historicos(
                    latitude, longitude, nome_local, periodo_dias
                )
                
                if dados:
                    st.success(f"✅ Coletados {len(dados)} registros!")
                    
                    # Exibir resumo
                    mostrar_resumo_coleta_rapida(dados, nome_local)
                    
                    # Preview dos dados
                    mostrar_preview_dados(dados, limite=10)
                
                else:
                    st.error("Não foi possível coletar dados.")
                    
            except Exception as e:
                st.error(f"Erro na coleta rápida: {str(e)}")

def dados_armazenados_tab(dados_repo, localizacao_repo):
    """Tab para visualizar dados armazenados."""
    
    st.markdown("### 🗂️ Dados Armazenados")
    st.markdown("Visualize e gerencie dados climáticos armazenados no banco.")
    
    # Estatísticas gerais
    total_registros = dados_repo.contar_total_registros()
    total_localidades = len(localizacao_repo.listar_todas())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", f"{total_registros:,}")
    
    with col2:
        st.metric("Localidades", total_localidades)
    
    with col3:
        if total_registros > 0:
            dados_mais_recentes = dados_repo.obter_dados_recentes(1)
            if dados_mais_recentes:
                ultimo_dado = dados_mais_recentes[0].data_medicao
                dias_atras = (datetime.now().date() - ultimo_dado.date()).days
                st.metric("Último Dado", f"{dias_atras} dias atrás")
            else:
                st.metric("Último Dado", "N/A")
        else:
            st.metric("Último Dado", "N/A")
    
    with col4:
        # Calcular cobertura temporal
        if total_registros > 0:
            dados_periodo = dados_repo.obter_periodo_dados()
            if dados_periodo:
                inicio, fim = dados_periodo
                dias_cobertura = (fim.date() - inicio.date()).days
                st.metric("Cobertura", f"{dias_cobertura} dias")
            else:
                st.metric("Cobertura", "N/A")
        else:
            st.metric("Cobertura", "N/A")
    
    if total_registros == 0:
        st.info("📊 Nenhum dado armazenado. Use as outras abas para coletar dados.")
        return
    
    st.markdown("---")
    
    # Filtros e visualização
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Filtros:**")
        
        # Filtro por localidade
        localidades = localizacao_repo.listar_todas()
        nomes_localidades = ["Todas"] + [loc.nome for loc in localidades]
        
        localidade_filtro = st.selectbox(
            "Localidade",
            nomes_localidades,
            help="Filtrar por localidade específica"
        )
        
        # Filtro por período
        periodo_filtro = st.selectbox(
            "Período",
            ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todos"],
            index=1,
            help="Filtrar por período temporal"
        )
        
        # Botão para aplicar filtros
        if st.button("🔍 Aplicar Filtros"):
            with st.spinner("Aplicando filtros..."):
                dados_filtrados = aplicar_filtros_dados(
                    dados_repo, localidade_filtro, periodo_filtro, localidades
                )
                
                if dados_filtrados:
                    st.session_state['dados_filtrados'] = dados_filtrados
                    st.success(f"Filtros aplicados - {len(dados_filtrados)} registros encontrados")
                else:
                    st.warning("Nenhum dado encontrado com os filtros aplicados.")
    
    with col2:
        st.markdown("**Visualização:**")
        
        # Verificar se há dados filtrados na sessão
        if 'dados_filtrados' in st.session_state:
            dados_para_mostrar = st.session_state['dados_filtrados']
            mostrar_graficos_dados_armazenados(dados_para_mostrar)
        else:
            # Mostrar dados recentes por padrão
            dados_recentes = dados_repo.obter_dados_recentes(100)
            if dados_recentes:
                mostrar_graficos_dados_armazenados(dados_recentes)

def mostrar_preview_dados(dados, limite=5):
    """Mostra preview dos dados coletados."""
    
    st.markdown("#### 👀 Preview dos Dados")
    
    if not dados:
        st.warning("Nenhum dado para mostrar.")
        return
    
    # Preparar dados para exibição
    df_preview = pd.DataFrame([{
        'Data/Hora': d.data_medicao.strftime('%d/%m/%Y %H:%M'),
        'Velocidade Vento (m/s)': f"{d.velocidade_vento:.2f}",
        'Temperatura (°C)': f"{d.temperatura:.1f}",
        'Umidade (%)': f"{d.umidade:.1f}",
        'Pressão (hPa)': f"{d.pressao:.1f}" if d.pressao else "N/A"
    } for d in dados[:limite]])
    
    st.dataframe(df_preview, use_container_width=True)
    
    if len(dados) > limite:
        st.info(f"Mostrando {limite} de {len(dados)} registros.")

def mostrar_resumo_coleta_rapida(dados, nome_local):
    """Mostra resumo da coleta rápida."""
    
    if not dados:
        return
    
    # Calcular estatísticas básicas
    velocidades = [d.velocidade_vento for d in dados]
    temperaturas = [d.temperatura for d in dados]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Vel. Vento Média", f"{np.mean(velocidades):.2f} m/s")
    
    with col2:
        st.metric("Vel. Vento Máxima", f"{np.max(velocidades):.2f} m/s")
    
    with col3:
        st.metric("Temperatura Média", f"{np.mean(temperaturas):.1f} °C")
    
    with col4:
        st.metric("Registros", len(dados))

def aplicar_filtros_dados(dados_repo, localidade_filtro, periodo_filtro, localidades):
    """Aplica filtros aos dados armazenados."""
    
    try:
        # Filtro por período
        data_limite = None
        if periodo_filtro == "Últimos 7 dias":
            data_limite = datetime.now() - timedelta(days=7)
        elif periodo_filtro == "Últimos 30 dias":
            data_limite = datetime.now() - timedelta(days=30)
        elif periodo_filtro == "Últimos 90 dias":
            data_limite = datetime.now() - timedelta(days=90)
        
        # Filtro por localidade
        localizacao_id = None
        if localidade_filtro != "Todas":
            localidade_obj = next((loc for loc in localidades if loc.nome == localidade_filtro), None)
            if localidade_obj:
                localizacao_id = localidade_obj.id
        
        # Buscar dados com filtros
        if data_limite and localizacao_id:
            dados = dados_repo.obter_por_periodo_e_localizacao(data_limite, datetime.now(), localizacao_id)
        elif data_limite:
            dados = dados_repo.obter_por_periodo(data_limite, datetime.now())
        elif localizacao_id:
            dados = dados_repo.obter_por_localizacao(localizacao_id)
        else:
            dados = dados_repo.obter_dados_recentes(1000)  # Limite para performance
        
        return dados
        
    except Exception as e:
        st.error(f"Erro ao aplicar filtros: {str(e)}")
        return []

def mostrar_graficos_dados_armazenados(dados):
    """Mostra gráficos dos dados armazenados."""
    
    if not dados:
        st.info("Nenhum dado para visualizar.")
        return
    
    # Preparar DataFrame
    df = pd.DataFrame([{
        'data': d.data_medicao,
        'velocidade_vento': d.velocidade_vento,
        'temperatura': d.temperatura,
        'umidade': d.umidade,
        'pressao': d.pressao if d.pressao else 0
    } for d in dados])
    
    # Gráfico de velocidade do vento
    fig_vento = px.line(
        df, 
        x='data', 
        y='velocidade_vento',
        title='Velocidade do Vento ao Longo do Tempo',
        labels={'velocidade_vento': 'Velocidade (m/s)', 'data': 'Data/Hora'}
    )
    fig_vento.update_layout(height=300)
    st.plotly_chart(fig_vento, use_container_width=True)
    
    # Gráficos de temperatura e umidade
    col1, col2 = st.columns(2)
    
    with col1:
        fig_temp = px.line(
            df, 
            x='data', 
            y='temperatura',
            title='Temperatura',
            labels={'temperatura': 'Temperatura (°C)', 'data': 'Data/Hora'}
        )
        fig_temp.update_layout(height=250)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        fig_umidade = px.line(
            df, 
            x='data', 
            y='umidade',
            title='Umidade Relativa',
            labels={'umidade': 'Umidade (%)', 'data': 'Data/Hora'}
        )
        fig_umidade.update_layout(height=250)
        st.plotly_chart(fig_umidade, use_container_width=True)

if __name__ == "__main__":
    main()
