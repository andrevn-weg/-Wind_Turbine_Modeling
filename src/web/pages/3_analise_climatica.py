"""
Página de Análise Climática - Sistema de Análise de Dados Climáticos e Eólicos.

Esta página permite visualizar e analisar dados climáticos coletados,
realizar análises estatísticas e calcular potencial eólico de localidades.

Autor: André Vinícius Lima do Nascimento
Data: Janeiro 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
from climate import (
    ColetaDadosService,
    AnaliseEolicaService,
    ProcessamentoSerieTemporalService,
    GerenciamentoLocalizacoesService,
    LocalizacaoClimaticaRepository
)

# Carregar CSS
css_path = os.path.join(project_root, "web", "static", "styles.css")
load_css(css_path)

def main():
    """Função principal da páginas de análise climática."""
    
    # Título da página
    st.markdown("""
    <div class="page-main-header">
        <h1>🌤️ Análise <span style="color: rgb(52, 152, 219);">Climática</span></h1>
        <p>Análise de Dados Climáticos e Potencial Eólico</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inicializar serviços
    coleta_service = ColetaDadosService()
    analise_service = AnaliseEolicaService()
    processamento_service = ProcessamentoSerieTemporalService()
    gerenciamento_service = GerenciamentoLocalizacoesService()
    localizacao_repo = LocalizacaoClimaticaRepository()
    
    # Tabs para diferentes seções
    tabs = st.tabs([
        "📊 Análise Rápida", 
        "🗺️ Localidades Salvas", 
        "📈 Análise Detalhada",
        "🔍 Comparação de Localidades"
    ])
    
    with tabs[0]:
        analise_rapida_tab(coleta_service, analise_service)
    
    with tabs[1]:
        localidades_salvas_tab(gerenciamento_service, localizacao_repo, analise_service)
    
    with tabs[2]:
        analise_detalhada_tab(coleta_service, analise_service, processamento_service)
    
    with tabs[3]:
        comparacao_localidades_tab(gerenciamento_service, localizacao_repo, analise_service)

def analise_rapida_tab(coleta_service, analise_service):
    """Tab para análise rápida de uma localidade."""
    
    st.markdown("### 🚀 Análise Rápida de Localidade")
    st.markdown("Obtenha rapidamente dados climáticos e análise eólica de qualquer localidade.")
    
    # Formulário de entrada
    with st.form("analise_rapida_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input(
                "Latitude", 
                value=-26.52, 
                min_value=-90.0, 
                max_value=90.0,
                format="%.6f",
                help="Latitude da localidade (ex: -26.52 para Jaraguá do Sul)"
            )
            
        with col2:
            longitude = st.number_input(
                "Longitude", 
                value=-49.06, 
                min_value=-180.0, 
                max_value=180.0,
                format="%.6f",
                help="Longitude da localidade (ex: -49.06 para Jaraguá do Sul)"
            )
        
        nome_localidade = st.text_input(
            "Nome da Localidade",
            value="Jaraguá do Sul",
            help="Nome identificador da localidade"
        )
        
        periodo_dias = st.select_slider(
            "Período de Análise",
            options=[7, 15, 30, 60, 90, 180, 365],
            value=30,
            help="Número de dias para análise histórica"
        )
        
        submitted = st.form_submit_button("🔍 Analisar Localidade")
    
    if submitted:
        with st.spinner("Coletando e analisando dados climáticos..."):
            try:
                # Coletar dados
                dados_climaticos = coleta_service.coletar_dados_historicos(
                    latitude, longitude, nome_localidade, periodo_dias
                )
                
                if dados_climaticos and len(dados_climaticos) > 0:
                    # Calcular estatísticas
                    estatisticas = analise_service.calcular_estatisticas_completas(dados_climaticos)
                    potencial_eolico = analise_service.calcular_potencial_eolico(dados_climaticos)
                    
                    # Exibir resultados
                    mostrar_resultados_analise_rapida(
                        dados_climaticos, estatisticas, potencial_eolico, nome_localidade
                    )
                    
                else:
                    st.error("Não foi possível obter dados climáticos para esta localidade.")
                    
            except Exception as e:
                st.error(f"Erro ao analisar localidade: {str(e)}")

def mostrar_resultados_analise_rapida(dados_climaticos, estatisticas, potencial_eolico, nome_localidade):
    """Exibe os resultados da análise rápida."""
    
    st.success(f"✅ Análise completa para **{nome_localidade}**")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Velocidade Média do Vento", 
            f"{estatisticas.get('velocidade_media', 0):.2f} m/s",
            help="Velocidade média do vento no período"
        )
    
    with col2:
        st.metric(
            "Velocidade Máxima", 
            f"{estatisticas.get('velocidade_maxima', 0):.2f} m/s",
            help="Velocidade máxima registrada"
        )
    
    with col3:
        st.metric(
            "Potencial Eólico", 
            f"{potencial_eolico.get('potencia_media', 0):.2f} W/m²",
            help="Potencial eólico médio"
        )
    
    with col4:
        st.metric(
            "Dias Analisados", 
            f"{len(dados_climaticos)}",
            help="Número de dias com dados"
        )
    
    # Gráficos
    st.markdown("### 📊 Visualizações")
    
    # Preparar dados para gráficos
    df = pd.DataFrame([{
        'data': d.data_medicao,
        'velocidade_vento': d.velocidade_vento,
        'temperatura': d.temperatura,
        'umidade': d.umidade,
        'pressao': d.pressao
    } for d in dados_climaticos])
    
    # Gráfico de velocidade do vento
    fig_vento = px.line(
        df, 
        x='data', 
        y='velocidade_vento',
        title=f'Velocidade do Vento - {nome_localidade}',
        labels={'velocidade_vento': 'Velocidade (m/s)', 'data': 'Data'}
    )
    fig_vento.update_layout(height=400)
    st.plotly_chart(fig_vento, use_container_width=True)
    
    # Gráficos de temperatura e umidade
    col1, col2 = st.columns(2)
    
    with col1:
        fig_temp = px.line(
            df, 
            x='data', 
            y='temperatura',
            title='Temperatura',
            labels={'temperatura': 'Temperatura (°C)', 'data': 'Data'}
        )
        fig_temp.update_layout(height=300)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        fig_umidade = px.line(
            df, 
            x='data', 
            y='umidade',
            title='Umidade Relativa',
            labels={'umidade': 'Umidade (%)', 'data': 'Data'}
        )
        fig_umidade.update_layout(height=300)
        st.plotly_chart(fig_umidade, use_container_width=True)

def localidades_salvas_tab(gerenciamento_service, localizacao_repo, analise_service):
    """Tab para gerenciar localidades salvas."""
    
    st.markdown("### 🗺️ Localidades Salvas")
    st.markdown("Gerencie suas localidades favoritas e acesse análises salvas.")
    
    # Listar localidades existentes
    localidades = localizacao_repo.listar_todas()
    
    if localidades:
        st.markdown(f"**{len(localidades)} localidades salvas:**")
        
        for loc in localidades:
            with st.expander(f"📍 {loc.nome} ({loc.latitude:.4f}, {loc.longitude:.4f})"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Coordenadas:** {loc.latitude:.6f}, {loc.longitude:.6f}")
                    st.write(f"**Criada em:** {loc.data_criacao.strftime('%d/%m/%Y %H:%M')}")
                    if loc.descricao:
                        st.write(f"**Descrição:** {loc.descricao}")
                
                with col2:
                    if st.button("🔄 Atualizar Dados", key=f"update_{loc.id}"):
                        with st.spinner("Atualizando..."):
                            try:
                                gerenciamento_service.atualizar_dados_localizacao(loc.id)
                                st.success("Dados atualizados!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
                
                with col3:
                    if st.button("🗑️ Remover", key=f"remove_{loc.id}"):
                        try:
                            localizacao_repo.remover(loc.id)
                            st.success("Localidade removida!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {str(e)}")
    else:
        st.info("Nenhuma localidade salva. Use a aba 'Análise Rápida' para começar.")

def analise_detalhada_tab(coleta_service, analise_service, processamento_service):
    """Tab para análise detalhada com gráficos avançados."""
    
    st.markdown("### 📈 Análise Detalhada")
    st.markdown("Análise aprofundada com gráficos avançados e processamento de séries temporais.")
    
    # Formulário para análise detalhada
    with st.form("analise_detalhada_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input("Latitude", value=-26.52, format="%.6f")
            longitude = st.number_input("Longitude", value=-49.06, format="%.6f")
        
        with col2:
            nome_localidade = st.text_input("Nome da Localidade", value="Jaraguá do Sul")
            periodo_dias = st.select_slider(
                "Período de Análise",
                options=[30, 60, 90, 180, 365, 730],
                value=90
            )
        
        opcoes_analise = st.multiselect(
            "Análises a Realizar",
            [
                "Estatísticas Descritivas",
                "Análise de Sazonalidade",
                "Curva de Duração de Vento",
                "Detecção de Outliers",
                "Análise de Tendências",
                "Rosa dos Ventos"
            ],
            default=["Estatísticas Descritivas", "Curva de Duração de Vento"]
        )
        
        submitted = st.form_submit_button("🔬 Análise Detalhada")
    
    if submitted:
        with st.spinner("Realizando análise detalhada..."):
            try:
                # Coletar dados
                dados_climaticos = coleta_service.coletar_dados_historicos(
                    latitude, longitude, nome_localidade, periodo_dias
                )
                
                if dados_climaticos and len(dados_climaticos) > 0:
                    realizar_analise_detalhada(
                        dados_climaticos, opcoes_analise, nome_localidade,
                        analise_service, processamento_service
                    )
                else:
                    st.error("Não foi possível obter dados climáticos.")
                    
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")

def realizar_analise_detalhada(dados_climaticos, opcoes_analise, nome_localidade, 
                             analise_service, processamento_service):
    """Realiza análise detalhada com base nas opções selecionadas."""
    
    st.success(f"✅ Análise detalhada para **{nome_localidade}**")
    
    # Preparar dados
    df = pd.DataFrame([{
        'data': d.data_medicao,
        'velocidade_vento': d.velocidade_vento,
        'temperatura': d.temperatura,
        'umidade': d.umidade,
        'pressao': d.pressao
    } for d in dados_climaticos])
    
    # Realizar análises selecionadas
    if "Estatísticas Descritivas" in opcoes_analise:
        mostrar_estatisticas_descritivas(dados_climaticos, analise_service)
    
    if "Curva de Duração de Vento" in opcoes_analise:
        mostrar_curva_duracao_vento(dados_climaticos, analise_service)
    
    if "Análise de Sazonalidade" in opcoes_analise:
        mostrar_analise_sazonalidade(df, processamento_service)
    
    if "Detecção de Outliers" in opcoes_analise:
        mostrar_deteccao_outliers(dados_climaticos, analise_service)
    
    if "Análise de Tendências" in opcoes_analise:
        mostrar_analise_tendencias(df, processamento_service)

def mostrar_estatisticas_descritivas(dados_climaticos, analise_service):
    """Mostra estatísticas descritivas detalhadas."""
    
    st.markdown("#### 📊 Estatísticas Descritivas")
    
    estatisticas = analise_service.calcular_estatisticas_completas(dados_climaticos)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Velocidade do Vento:**")
        st.write(f"• Média: {estatisticas.get('velocidade_media', 0):.2f} m/s")
        st.write(f"• Mediana: {estatisticas.get('velocidade_mediana', 0):.2f} m/s")
        st.write(f"• Desvio Padrão: {estatisticas.get('velocidade_desvio_padrao', 0):.2f} m/s")
        st.write(f"• Mínima: {estatisticas.get('velocidade_minima', 0):.2f} m/s")
        st.write(f"• Máxima: {estatisticas.get('velocidade_maxima', 0):.2f} m/s")
    
    with col2:
        st.markdown("**Temperatura:**")
        st.write(f"• Média: {estatisticas.get('temperatura_media', 0):.1f} °C")
        st.write(f"• Mínima: {estatisticas.get('temperatura_minima', 0):.1f} °C")
        st.write(f"• Máxima: {estatisticas.get('temperatura_maxima', 0):.1f} °C")
        
        st.markdown("**Umidade:**")
        st.write(f"• Média: {estatisticas.get('umidade_media', 0):.1f} %")

def mostrar_curva_duracao_vento(dados_climaticos, analise_service):
    """Mostra curva de duração do vento."""
    
    st.markdown("#### 📈 Curva de Duração do Vento")
    
    try:
        curva_duracao = analise_service.calcular_curva_duracao_vento(dados_climaticos)
        
        if curva_duracao:
            df_curva = pd.DataFrame(curva_duracao)
            
            fig = px.line(
                df_curva,
                x='percentual_tempo',
                y='velocidade_vento',
                title='Curva de Duração do Vento',
                labels={
                    'percentual_tempo': 'Percentual do Tempo (%)',
                    'velocidade_vento': 'Velocidade do Vento (m/s)'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("A curva de duração mostra por quanto tempo cada velocidade de vento foi superada.")
        
    except Exception as e:
        st.error(f"Erro ao calcular curva de duração: {str(e)}")

def mostrar_analise_sazonalidade(df, processamento_service):
    """Mostra análise de sazonalidade."""
    
    st.markdown("#### 🔄 Análise de Sazonalidade")
    
    try:
        # Adicionar colunas de tempo
        df['mes'] = df['data'].dt.month
        df['hora'] = df['data'].dt.hour
        
        # Sazonalidade mensal
        sazonalidade_mensal = df.groupby('mes')['velocidade_vento'].mean().reset_index()
        sazonalidade_mensal['mes_nome'] = sazonalidade_mensal['mes'].map({
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_mensal = px.bar(
                sazonalidade_mensal,
                x='mes_nome',
                y='velocidade_vento',
                title='Velocidade Média do Vento por Mês',
                labels={'velocidade_vento': 'Velocidade (m/s)', 'mes_nome': 'Mês'}
            )
            fig_mensal.update_layout(height=300)
            st.plotly_chart(fig_mensal, use_container_width=True)
        
        with col2:
            # Sazonalidade horária
            sazonalidade_horaria = df.groupby('hora')['velocidade_vento'].mean().reset_index()
            
            fig_horaria = px.line(
                sazonalidade_horaria,
                x='hora',
                y='velocidade_vento',
                title='Velocidade Média do Vento por Hora',
                labels={'velocidade_vento': 'Velocidade (m/s)', 'hora': 'Hora do Dia'}
            )
            fig_horaria.update_layout(height=300)
            st.plotly_chart(fig_horaria, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro na análise de sazonalidade: {str(e)}")

def mostrar_deteccao_outliers(dados_climaticos, analise_service):
    """Mostra detecção de outliers."""
    
    st.markdown("#### 🔍 Detecção de Outliers")
    
    try:
        outliers = analise_service.detectar_outliers_vento(dados_climaticos)
        
        if outliers:
            st.warning(f"⚠️ {len(outliers)} outliers detectados:")
            
            df_outliers = pd.DataFrame([{
                'data': o.data_medicao,
                'velocidade_vento': o.velocidade_vento,
                'temperatura': o.temperatura
            } for o in outliers])
            
            st.dataframe(df_outliers.head(10))
            
            if len(outliers) > 10:
                st.info(f"Mostrando apenas os primeiros 10 de {len(outliers)} outliers.")
        else:
            st.success("✅ Nenhum outlier detectado nos dados.")
            
    except Exception as e:
        st.error(f"Erro na detecção de outliers: {str(e)}")

def mostrar_analise_tendencias(df, processamento_service):
    """Mostra análise de tendências."""
    
    st.markdown("#### 📊 Análise de Tendências")
    
    try:
        # Calcular média móvel
        df['media_movel_7d'] = df['velocidade_vento'].rolling(window=7, center=True).mean()
        df['media_movel_30d'] = df['velocidade_vento'].rolling(window=30, center=True).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['data'],
            y=df['velocidade_vento'],
            mode='lines',
            name='Velocidade Original',
            line=dict(color='lightblue', width=1),
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            x=df['data'],
            y=df['media_movel_7d'],
            mode='lines',
            name='Média Móvel 7 dias',
            line=dict(color='orange', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['data'],
            y=df['media_movel_30d'],
            mode='lines',
            name='Média Móvel 30 dias',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title='Análise de Tendências - Velocidade do Vento',
            xaxis_title='Data',
            yaxis_title='Velocidade do Vento (m/s)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro na análise de tendências: {str(e)}")

def comparacao_localidades_tab(gerenciamento_service, localizacao_repo, analise_service):
    """Tab para comparar diferentes localidades."""
    
    st.markdown("### 🔍 Comparação de Localidades")
    st.markdown("Compare o potencial eólico de diferentes localidades.")
    
    # Listar localidades salvas
    localidades = localizacao_repo.listar_todas()
    
    if len(localidades) < 2:
        st.info("Você precisa ter pelo menos 2 localidades salvas para fazer comparações.")
        return
    
    # Seleção de localidades para comparar
    nomes_localidades = [f"{loc.nome} ({loc.latitude:.4f}, {loc.longitude:.4f})" 
                        for loc in localidades]
    
    localidades_selecionadas = st.multiselect(
        "Selecione localidades para comparar",
        nomes_localidades,
        default=nomes_localidades[:2] if len(nomes_localidades) >= 2 else nomes_localidades
    )
    
    if len(localidades_selecionadas) >= 2:
        if st.button("📊 Comparar Localidades"):
            with st.spinner("Gerando comparação..."):
                try:
                    # Implementar comparação
                    st.success("Comparação realizada com sucesso!")
                    st.info("Funcionalidade de comparação será implementada em versão futura.")
                except Exception as e:
                    st.error(f"Erro na comparação: {str(e)}")

if __name__ == "__main__":
    main()
