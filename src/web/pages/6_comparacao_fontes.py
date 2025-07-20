"""
Página de Comparação de Fontes - Dados Climáticos de Múltiplas APIs.

Esta página permite comparar dados de diferentes fontes de APIs meteorológicas
(Open-Meteo vs NASA POWER) para validação e análise de precisão.

Autor: André Vinícius Lima do Nascimento
Data: Janeiro 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import os
import sys

# Adicionar src ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports do projeto
from utils.css_loader import load_css
from climate.api import OpenMeteoClient, NASAPowerClient
from climate.models.entity import LocalizacaoClimatica
from climate import AnaliseEolicaService

# Carregar CSS
css_path = os.path.join(project_root, "web", "static", "styles.css")
load_css(css_path)

def main():
    """Função principal da página de comparação de fontes."""
    
    # Título da página
    st.markdown("""
    <div class="page-main-header">
        <h1>🔍 Comparação de <span style="color: rgb(52, 152, 219);">Fontes</span></h1>
        <p>Análise Comparativa: Open-Meteo vs NASA POWER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Seção de configuração
    with st.container():
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Configuração da Análise</h3>
            <p>Configure os parâmetros para comparação entre fontes de dados</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📍 Localização")
            
            # Localizações pré-definidas
            localizacoes_predefinidas = {
                "Jaraguá do Sul - Morro das Antenas": (-26.5165, -49.0559),
                "Cachoeira do Sul": (-30.0383, -52.8956),
                "Porto Alegre": (-30.0346, -51.2177),
                "Florianópolis": (-27.5954, -48.5480),
                "Santa Maria": (-29.6842, -53.8069),
                "Coordenadas Customizadas": None
            }
            
            localizacao_selecionada = st.selectbox(
                "Escolha a localização:",
                list(localizacoes_predefinidas.keys())
            )
            
            if localizacao_selecionada == "Coordenadas Customizadas":
                latitude = st.number_input("Latitude:", value=-26.5165, min_value=-90.0, max_value=90.0, step=0.0001, format="%.4f")
                longitude = st.number_input("Longitude:", value=-49.0559, min_value=-180.0, max_value=180.0, step=0.0001, format="%.4f")
                nome_local = st.text_input("Nome do Local:", value="Local Customizado")
            else:
                coords = localizacoes_predefinidas[localizacao_selecionada]
                if coords:
                    latitude, longitude = coords
                    nome_local = localizacao_selecionada
                    st.info(f"📍 Lat: {latitude:.4f}, Lng: {longitude:.4f}")
        
        with col2:
            st.subheader("📅 Período")
            
            periodo_opcoes = {
                "Última semana": 7,
                "Último mês": 30,
                "Últimos 3 meses": 90,
                "Último semestre": 180,
                "Último ano": 365
            }
            
            periodo_selecionado = st.selectbox(
                "Período de análise:",
                list(periodo_opcoes.keys())
            )
            
            dias = periodo_opcoes[periodo_selecionado]
            
            data_fim = datetime.now()
            data_inicio = data_fim - timedelta(days=dias)
            
            st.info(f"📅 {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
            st.info(f"📊 {dias} dias de dados")
        
        with col3:
            st.subheader("⚙️ Parâmetros")
            
            altura_vento = st.selectbox(
                "Altura de medição:",
                [10, 50, 80],
                help="Altura em metros para medição do vento"
            )
            
            incluir_nasa = st.checkbox(
                "Incluir NASA POWER",
                value=True,
                help="NASA POWER pode ser mais lento"
            )
            
            incluir_comparacao_estatistica = st.checkbox(
                "Análise estatística detalhada",
                value=True
            )
    
    st.markdown("---")
    
    # Botão para executar análise
    if st.button("🚀 Executar Análise Comparativa", type="primary", use_container_width=True):
        
        with st.spinner("Coletando dados das APIs..."):
            
            # Placeholder para resultados
            dados_open_meteo = None
            dados_nasa_power = None
            
            # Coletar dados Open-Meteo
            st.info("📡 Coletando dados da Open-Meteo...")
            try:
                client_open_meteo = OpenMeteoClient()
                dados_open_meteo = client_open_meteo.obter_dados_historicos(
                    latitude=latitude,
                    longitude=longitude,
                    inicio=data_inicio,
                    fim=data_fim,
                    altura_vento=altura_vento,
                    nome_cidade=nome_local
                )
                st.success(f"✅ Open-Meteo: {len(dados_open_meteo)} registros coletados")
            except Exception as e:
                st.error(f"❌ Erro ao coletar dados Open-Meteo: {str(e)}")
            
            # Coletar dados NASA POWER
            if incluir_nasa:
                st.info("🛰️ Coletando dados da NASA POWER...")
                try:
                    # Nota: NASA POWER só tem dados para 10m e 50m
                    altura_nasa = 10 if altura_vento <= 10 else 50
                    if altura_nasa != altura_vento:
                        st.warning(f"⚠️ NASA POWER: usando {altura_nasa}m (mais próximo de {altura_vento}m)")
                    
                    client_nasa = NASAPowerClient()
                    dados_nasa_power = client_nasa.obter_dados_vento(
                        latitude=latitude,
                        longitude=longitude,
                        inicio=data_inicio,
                        fim=data_fim,
                        altura_vento=altura_nasa,
                        nome_cidade=nome_local
                    )
                    st.success(f"✅ NASA POWER: {len(dados_nasa_power)} registros coletados")
                except Exception as e:
                    st.error(f"❌ Erro ao coletar dados NASA POWER: {str(e)}")
                    incluir_nasa = False
        
        # Análise e visualização dos dados
        if dados_open_meteo or dados_nasa_power:
            
            st.markdown("---")
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Resultados da Comparação</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Preparar DataFrames para visualização
            df_comparacao = []
            
            if dados_open_meteo:
                df_open_meteo = pd.DataFrame([{
                    'data': d.data,
                    'velocidade_vento': d.velocidade_vento,
                    'temperatura': d.temperatura,
                    'umidade': d.umidade,
                    'fonte': 'Open-Meteo'
                } for d in dados_open_meteo])
                df_comparacao.append(df_open_meteo)
            
            if dados_nasa_power:
                df_nasa = pd.DataFrame([{
                    'data': d.data,
                    'velocidade_vento': d.velocidade_vento,
                    'temperatura': d.temperatura,
                    'umidade': d.umidade,
                    'fonte': 'NASA POWER'
                } for d in dados_nasa_power])
                df_comparacao.append(df_nasa)
            
            if df_comparacao:
                df_completo = pd.concat(df_comparacao, ignore_index=True)
                
                # Visualizações
                tab1, tab2, tab3, tab4 = st.tabs(["🌬️ Vento", "🌡️ Temperatura", "💧 Umidade", "📈 Estatísticas"])
                
                with tab1:
                    st.subheader("Velocidade do Vento - Comparação Temporal")
                    
                    fig_vento = px.line(
                        df_completo,
                        x='data',
                        y='velocidade_vento',
                        color='fonte',
                        title=f"Velocidade do Vento - {nome_local}",
                        labels={
                            'data': 'Data',
                            'velocidade_vento': 'Velocidade do Vento (m/s)',
                            'fonte': 'Fonte de Dados'
                        }
                    )
                    
                    fig_vento.update_layout(height=500)
                    st.plotly_chart(fig_vento, use_container_width=True)
                    
                    # Box plot para distribuição
                    fig_box_vento = px.box(
                        df_completo,
                        x='fonte',
                        y='velocidade_vento',
                        title="Distribuição da Velocidade do Vento por Fonte",
                        labels={
                            'fonte': 'Fonte de Dados',
                            'velocidade_vento': 'Velocidade do Vento (m/s)'
                        }
                    )
                    st.plotly_chart(fig_box_vento, use_container_width=True)
                
                with tab2:
                    st.subheader("Temperatura - Comparação Temporal")
                    
                    fig_temp = px.line(
                        df_completo,
                        x='data',
                        y='temperatura',
                        color='fonte',
                        title=f"Temperatura - {nome_local}",
                        labels={
                            'data': 'Data',
                            'temperatura': 'Temperatura (°C)',
                            'fonte': 'Fonte de Dados'
                        }
                    )
                    
                    fig_temp.update_layout(height=500)
                    st.plotly_chart(fig_temp, use_container_width=True)
                
                with tab3:
                    st.subheader("Umidade Relativa - Comparação Temporal")
                    
                    fig_umidade = px.line(
                        df_completo,
                        x='data',
                        y='umidade',
                        color='fonte',
                        title=f"Umidade Relativa - {nome_local}",
                        labels={
                            'data': 'Data',
                            'umidade': 'Umidade Relativa (%)',
                            'fonte': 'Fonte de Dados'
                        }
                    )
                    
                    fig_umidade.update_layout(height=500)
                    st.plotly_chart(fig_umidade, use_container_width=True)
                
                with tab4:
                    st.subheader("Análise Estatística Comparativa")
                    
                    # Calcular estatísticas por fonte
                    stats_por_fonte = df_completo.groupby('fonte').agg({
                        'velocidade_vento': ['mean', 'std', 'min', 'max', 'median'],
                        'temperatura': ['mean', 'std', 'min', 'max'],
                        'umidade': ['mean', 'std', 'min', 'max']
                    }).round(2)
                    
                    st.markdown("#### 🌬️ Estatísticas do Vento")
                    
                    if incluir_comparacao_estatistica:
                        # Análise detalhada de potencial eólico
                        analise_service = AnaliseEolicaService()
                        
                        col1, col2 = st.columns(2)
                        
                        if dados_open_meteo:
                            with col1:
                                st.markdown("**Open-Meteo**")
                                stats_om = analise_service.calcular_estatisticas_completas(dados_open_meteo)
                                vento = stats_om['vento']
                                st.metric("Velocidade Média", f"{vento['media']:.2f} m/s")
                                st.metric("Velocidade Máxima", f"{vento['maximo']:.2f} m/s")
                                st.metric("Desvio Padrão", f"{vento['desvio_padrao']:.2f} m/s")
                                # st.metric("Dias Viáveis", f"{stats_om['dias_viaveis']}")
                        
                        if dados_nasa_power:
                            with col2:
                                st.markdown("**NASA POWER**")
                                stats_nasa = analise_service.calcular_estatisticas_completas(dados_nasa_power)
                                vento = stats_nasa['vento']
                                print(vento)
                                st.metric("Velocidade Média", f"{vento['media']:.2f} m/s")
                                st.metric("Velocidade Máxima", f"{vento['maximo']:.2f} m/s")
                                st.metric("Desvio Padrão", f"{vento['desvio_padrao']:.2f} m/s")
                                # st.metric("Dias Viáveis", f"{stats_nasa['dias_viaveis']}")
                    
                    # Tabela comparativa
                    st.markdown("#### 📊 Tabela Comparativa Completa")
                    st.dataframe(stats_por_fonte, use_container_width=True)
                    
                    # Correlação entre fontes (se ambas disponíveis)
                    if len(df_comparacao) == 2 and incluir_comparacao_estatistica:
                        st.markdown("#### 🔗 Análise de Correlação")
                        
                        # Merge dos dados por data para correlação
                        df_om = df_comparacao[0].set_index('data')
                        df_nasa = df_comparacao[1].set_index('data')
                        
                        df_merged = df_om.merge(df_nasa, left_index=True, right_index=True, suffixes=('_om', '_nasa'))
                        
                        if not df_merged.empty:
                            correlacao_vento = df_merged['velocidade_vento_om'].corr(df_merged['velocidade_vento_nasa'])
                            correlacao_temp = df_merged['temperatura_om'].corr(df_merged['temperatura_nasa'])
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Correlação Vento", f"{correlacao_vento:.3f}")
                            with col2:
                                st.metric("Correlação Temperatura", f"{correlacao_temp:.3f}")
                            with col3:
                                rmse_vento = np.sqrt(np.mean((df_merged['velocidade_vento_om'] - df_merged['velocidade_vento_nasa'])**2))
                                st.metric("RMSE Vento", f"{rmse_vento:.3f} m/s")
                            
                            # Scatter plot para correlação
                            fig_scatter = px.scatter(
                                df_merged.reset_index(),
                                x='velocidade_vento_om',
                                y='velocidade_vento_nasa',
                                title="Correlação de Velocidade do Vento: Open-Meteo vs NASA POWER",
                                labels={
                                    'velocidade_vento_om': 'Open-Meteo (m/s)',
                                    'velocidade_vento_nasa': 'NASA POWER (m/s)'
                                },
                                trendline="ols"
                            )
                            
                            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.markdown("---")
            
            # Conclusões e recomendações
            st.markdown("""
            <div class="metric-card">
                <h3>💡 Conclusões e Recomendações</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            **Sobre as Fontes de Dados:**
            
            - **Open-Meteo**: API gratuita, rápida, com boa resolução temporal e alta disponibilidade
            - **NASA POWER**: Dados oficiais da NASA, validados cientificamente, mas com menor resolução temporal
            
            **Recomendações de Uso:**
            - Para análises exploratórias: **Open-Meteo** (rapidez e facilidade)
            - Para estudos acadêmicos: **NASA POWER** (validação científica)
            - Para projetos comerciais: Considere ambas para validação cruzada
            """)
        
        else:
            st.error("❌ Não foi possível coletar dados de nenhuma fonte. Verifique a conexão e tente novamente.")


if __name__ == "__main__":
    main()
