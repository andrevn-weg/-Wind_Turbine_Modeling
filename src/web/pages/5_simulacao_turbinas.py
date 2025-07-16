"""
Página de Simulação de Turbinas - Sistema de Modelagem e Simulação.

Esta página permite simular o comportamento de turbinas eólicas
com base em dados climáticos e parâmetros técnicos.

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
    LocalizacaoClimaticaRepository,
    DadosClimaticosRepository
)

# Carregar CSS
css_path = os.path.join(project_root, "web", "static", "styles.css")
load_css(css_path)

def main():
    """Função principal da página de simulação de turbinas."""
    
    # Título da página
    st.markdown("""
    <div class="page-main-header">
        <h1>⚡ Simulação de <span style="color: rgb(155, 89, 182);">Turbinas</span></h1>
        <p>Modelagem e Simulação de Turbinas Eólicas</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inicializar serviços
    coleta_service = ColetaDadosService()
    analise_service = AnaliseEolicaService()
    localizacao_repo = LocalizacaoClimaticaRepository()
    dados_repo = DadosClimaticosRepository()
    
    # Tabs para diferentes tipos de simulação
    tabs = st.tabs([
        "🎯 Simulação Rápida", 
        "🔧 Configuração Avançada", 
        "📊 Análise de Performance",
        "💡 Otimização"
    ])
    
    with tabs[0]:
        simulacao_rapida_tab(coleta_service, analise_service)
    
    with tabs[1]:
        configuracao_avancada_tab(localizacao_repo, dados_repo)
    
    with tabs[2]:
        analise_performance_tab(dados_repo, localizacao_repo)
    
    with tabs[3]:
        otimizacao_tab()

def simulacao_rapida_tab(coleta_service, analise_service):
    """Tab para simulação rápida de turbina."""
    
    st.markdown("### 🎯 Simulação Rápida")
    st.markdown("Configure uma simulação básica de turbina eólica rapidamente.")
    
    # Parâmetros da turbina
    st.markdown("#### ⚙️ Parâmetros da Turbina")
    
    col1, col2 = st.columns(2)
    
    with col1:
        potencia_nominal = st.number_input(
            "Potência Nominal (kW)",
            min_value=0.1,
            max_value=10000.0,
            value=2000.0,
            step=100.0,
            help="Potência nominal da turbina em kilowatts"
        )
        
        diametro_rotor = st.number_input(
            "Diâmetro do Rotor (m)",
            min_value=1.0,
            max_value=200.0,
            value=80.0,
            step=1.0,
            help="Diâmetro do rotor da turbina em metros"
        )
        
        altura_hub = st.number_input(
            "Altura do Hub (m)",
            min_value=10.0,
            max_value=200.0,
            value=80.0,
            step=5.0,
            help="Altura do centro do rotor em metros"
        )
    
    with col2:
        vel_corte_inicial = st.number_input(
            "Velocidade de Corte Inicial (m/s)",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
            help="Velocidade mínima do vento para gerar energia"
        )
        
        vel_nominal = st.number_input(
            "Velocidade Nominal (m/s)",
            min_value=5.0,
            max_value=20.0,
            value=12.0,
            step=0.5,
            help="Velocidade do vento para potência nominal"
        )
        
        vel_corte_final = st.number_input(
            "Velocidade de Corte Final (m/s)",
            min_value=15.0,
            max_value=40.0,
            value=25.0,
            step=1.0,
            help="Velocidade máxima de operação segura"
        )
    
    # Dados de vento
    st.markdown("#### 🌪️ Dados de Vento")
    
    tipo_dados = st.radio(
        "Fonte dos Dados de Vento",
        ["Coletar dados online", "Usar dados simulados", "Dados personalizados"],
        help="Escolha a fonte dos dados de vento para simulação"
    )
    
    dados_vento = None
    
    if tipo_dados == "Coletar dados online":
        with st.expander("🌍 Configurar Coleta de Dados"):
            col1, col2 = st.columns(2)
            
            with col1:
                latitude = st.number_input("Latitude", value=-26.52, format="%.6f")
                longitude = st.number_input("Longitude", value=-49.06, format="%.6f")
            
            with col2:
                nome_local = st.text_input("Nome do Local", value="Local da Simulação")
                periodo_dias = st.selectbox("Período (dias)", [7, 15, 30, 60, 90], index=2)
            
            if st.button("📥 Coletar Dados"):
                with st.spinner("Coletando dados de vento..."):
                    try:
                        dados_vento = coleta_service.coletar_dados_historicos(
                            latitude, longitude, nome_local, periodo_dias
                        )
                        
                        if dados_vento:
                            st.success(f"✅ Coletados {len(dados_vento)} registros de vento!")
                            st.session_state['dados_vento_simulacao'] = dados_vento
                        else:
                            st.error("Não foi possível coletar dados de vento.")
                    
                    except Exception as e:
                        st.error(f"Erro ao coletar dados: {str(e)}")
    
    elif tipo_dados == "Usar dados simulados":
        with st.expander("🎲 Configurar Dados Simulados"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                vel_media = st.number_input("Velocidade Média (m/s)", value=8.0, min_value=1.0, max_value=20.0)
                desvio_padrao = st.number_input("Desvio Padrão (m/s)", value=2.0, min_value=0.1, max_value=5.0)
            
            with col2:
                num_pontos = st.number_input("Número de Pontos", value=1000, min_value=100, max_value=10000)
                semente = st.number_input("Semente Aleatória", value=42, min_value=1, max_value=1000)
            
            with col3:
                distribuicao = st.selectbox("Distribuição", ["Normal", "Weibull", "Exponencial"])
                incluir_sazonalidade = st.checkbox("Incluir Sazonalidade", value=True)
            
            if st.button("🎲 Gerar Dados Simulados"):
                dados_vento = gerar_dados_vento_simulados(
                    vel_media, desvio_padrao, num_pontos, semente, 
                    distribuicao, incluir_sazonalidade
                )
                
                if dados_vento:
                    st.success(f"✅ Gerados {len(dados_vento)} pontos de dados simulados!")
                    st.session_state['dados_vento_simulacao'] = dados_vento
    
    else:  # Dados personalizados
        st.info("🔜 Funcionalidade de upload de dados personalizados será implementada em versão futura.")
    
    # Verificar se há dados de vento na sessão
    if 'dados_vento_simulacao' in st.session_state:
        dados_vento = st.session_state['dados_vento_simulacao']
    
    # Executar simulação
    st.markdown("---")
    
    if st.button("⚡ Executar Simulação", type="primary"):
        if dados_vento:
            with st.spinner("Executando simulação da turbina..."):
                try:
                    resultados = executar_simulacao_turbina(
                        dados_vento, potencia_nominal, diametro_rotor, altura_hub,
                        vel_corte_inicial, vel_nominal, vel_corte_final
                    )
                    
                    if resultados:
                        mostrar_resultados_simulacao(resultados, dados_vento)
                    
                except Exception as e:
                    st.error(f"Erro na simulação: {str(e)}")
        else:
            st.warning("⚠️ Por favor, configure os dados de vento antes de executar a simulação.")

def configuracao_avancada_tab(localizacao_repo, dados_repo):
    """Tab para configuração avançada de simulação."""
    
    st.markdown("### 🔧 Configuração Avançada")
    st.markdown("Configure simulações detalhadas com parâmetros avançados.")
    
    # Seleção de localidade com dados existentes
    localidades = localizacao_repo.listar_todas()
    
    if localidades:
        st.markdown("#### 📍 Selecionar Localidade")
        
        nomes_localidades = [f"{loc.nome} ({loc.latitude:.4f}, {loc.longitude:.4f})" 
                           for loc in localidades]
        
        localidade_idx = st.selectbox(
            "Localidade com Dados",
            range(len(nomes_localidades)),
            format_func=lambda x: nomes_localidades[x],
            help="Selecione uma localidade com dados históricos"
        )
        
        localidade_selecionada = localidades[localidade_idx]
        
        # Verificar dados disponíveis
        dados_disponiveis = dados_repo.obter_por_localizacao(localidade_selecionada.id)
        
        if dados_disponiveis:
            st.success(f"✅ {len(dados_disponiveis)} registros de dados disponíveis")
            
            # Mostrar período dos dados
            datas = [d.data_medicao for d in dados_disponiveis]
            data_inicio = min(datas)
            data_fim = max(datas)
            
            st.info(f"📅 Período dos dados: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        else:
            st.warning("⚠️ Nenhum dado encontrado para esta localidade.")
    
    else:
        st.info("📍 Cadastre localidades na página 'Coleta de Dados' para usar dados históricos.")
    
    # Configurações avançadas da turbina
    st.markdown("#### ⚙️ Configurações Avançadas da Turbina")
    
    with st.expander("🔧 Parâmetros Técnicos Detalhados"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Características Aerodinâmicas:**")
            coef_potencia_max = st.number_input("Coeficiente de Potência Máximo", value=0.45, min_value=0.1, max_value=0.6, step=0.01)
            tip_speed_ratio = st.number_input("Tip Speed Ratio Ótimo", value=7.0, min_value=3.0, max_value=12.0, step=0.1)
            eficiencia_gearbox = st.number_input("Eficiência da Caixa de Engrenagens (%)", value=95.0, min_value=80.0, max_value=99.0, step=1.0)
            eficiencia_gerador = st.number_input("Eficiência do Gerador (%)", value=93.0, min_value=80.0, max_value=98.0, step=1.0)
        
        with col2:
            st.markdown("**Características Ambientais:**")
            densidade_ar = st.number_input("Densidade do Ar (kg/m³)", value=1.225, min_value=1.0, max_value=1.4, step=0.01)
            rugosidade_terreno = st.selectbox("Rugosidade do Terreno", 
                                            ["0.0002 - Mar aberto", "0.03 - Campo aberto", "0.1 - Subúrbio", "0.4 - Cidade"])
            correcao_altura = st.checkbox("Aplicar Correção de Altura", value=True)
            fator_disponibilidade = st.number_input("Fator de Disponibilidade (%)", value=95.0, min_value=80.0, max_value=100.0, step=1.0)
    
    st.info("🔜 Simulação avançada será implementada em versão futura com todos os parâmetros técnicos.")

def analise_performance_tab(dados_repo, localizacao_repo):
    """Tab para análise de performance."""
    
    st.markdown("### 📊 Análise de Performance")
    st.markdown("Analise a performance esperada de turbinas em diferentes condições.")
    
    # Localidades para análise
    localidades = localizacao_repo.listar_todas()
    
    if not localidades:
        st.info("📍 Cadastre localidades com dados para realizar análises de performance.")
        return
    
    # Seleção múltipla de localidades
    nomes_localidades = [f"{loc.nome} ({loc.latitude:.4f}, {loc.longitude:.4f})" 
                        for loc in localidades]
    
    localidades_selecionadas = st.multiselect(
        "Localidades para Análise",
        nomes_localidades,
        default=nomes_localidades[:1] if nomes_localidades else [],
        help="Selecione uma ou mais localidades para comparar"
    )
    
    if localidades_selecionadas:
        # Análise de viabilidade
        st.markdown("#### 📈 Análise de Viabilidade")
        
        for nome_local in localidades_selecionadas:
            # Encontrar localidade correspondente
            idx = nomes_localidades.index(nome_local)
            localidade = localidades[idx]
            
            # Obter dados
            dados = dados_repo.obter_por_localizacao(localidade.id)
            
            if dados:
                with st.expander(f"📊 {localidade.nome}"):
                    analisar_viabilidade_localidade(dados, localidade.nome)
            else:
                st.warning(f"⚠️ Sem dados para {localidade.nome}")

def otimizacao_tab():
    """Tab para otimização de turbinas."""
    
    st.markdown("### 💡 Otimização")
    st.markdown("Encontre a configuração ótima de turbina para suas condições.")
    
    st.info("🔜 Funcionalidade de otimização será implementada em versão futura.")
    
    # Preview do que será implementado
    with st.expander("🔮 Preview - Funcionalidades Futuras"):
        st.markdown("""
        **Funcionalidades de Otimização Planejadas:**
        
        1. **Otimização de Altura do Hub**
           - Análise de perfil de vento vertical
           - Custo-benefício por altura
           - Recomendação de altura ótima
        
        2. **Seleção de Turbina**
           - Comparação de diferentes modelos
           - Análise de ROI por turbina
           - Recomendação baseada em condições locais
        
        3. **Layout do Parque Eólico**
           - Otimização de espaçamento
           - Minimização de efeitos de esteira
           - Maximização de produção total
        
        4. **Análise Financeira**
           - Cálculo de LCOE
           - Análise de viabilidade econômica
           - Projeção de retorno de investimento
        """)

def gerar_dados_vento_simulados(vel_media, desvio_padrao, num_pontos, semente, 
                               distribuicao, incluir_sazonalidade):
    """Gera dados de vento simulados."""
    
    np.random.seed(semente)
    
    # Gerar timestamps
    inicio = datetime.now() - timedelta(days=num_pontos//24)
    timestamps = [inicio + timedelta(hours=i) for i in range(num_pontos)]
    
    # Gerar velocidades base
    if distribuicao == "Normal":
        velocidades = np.random.normal(vel_media, desvio_padrao, num_pontos)
    elif distribuicao == "Weibull":
        # Parâmetros aproximados para Weibull
        k = 2.0  # Parâmetro de forma
        scale = vel_media / (np.exp(1/k) * np.sqrt(np.pi/k))
        velocidades = np.random.weibull(k, num_pontos) * scale
    else:  # Exponencial
        velocidades = np.random.exponential(vel_media, num_pontos)
    
    # Garantir valores positivos
    velocidades = np.maximum(velocidades, 0.1)
    
    # Adicionar sazonalidade se solicitado
    if incluir_sazonalidade:
        for i, timestamp in enumerate(timestamps):
            # Variação sazonal (ciclo anual)
            dia_ano = timestamp.timetuple().tm_yday
            fator_sazonal = 1 + 0.2 * np.sin(2 * np.pi * dia_ano / 365)
            
            # Variação diária
            hora = timestamp.hour
            fator_diario = 1 + 0.1 * np.sin(2 * np.pi * hora / 24)
            
            velocidades[i] *= fator_sazonal * fator_diario
    
    # Criar objetos de dados climáticos simulados
    from climate.models.entity import DadosClimaticos
    
    dados_simulados = []
    for i, timestamp in enumerate(timestamps):
        dado = DadosClimaticos(
            data_medicao=timestamp,
            velocidade_vento=velocidades[i],
            temperatura=20.0 + 5 * np.sin(2 * np.pi * timestamp.timetuple().tm_yday / 365),
            umidade=60.0 + 20 * np.random.random(),
            pressao=1013.25 + 10 * np.random.random()
        )
        dados_simulados.append(dado)
    
    return dados_simulados

def executar_simulacao_turbina(dados_vento, potencia_nominal, diametro_rotor, altura_hub,
                              vel_corte_inicial, vel_nominal, vel_corte_final):
    """Executa simulação básica de turbina eólica."""
    
    try:
        # Área do rotor
        area_rotor = np.pi * (diametro_rotor / 2) ** 2
        
        # Densidade do ar (padrão ao nível do mar)
        densidade_ar = 1.225
        
        resultados = []
        
        for dado in dados_vento:
            velocidade = dado.velocidade_vento
            
            # Aplicar curva de potência simplificada
            if velocidade < vel_corte_inicial:
                potencia = 0.0
            elif velocidade < vel_nominal:
                # Curva cúbica entre corte inicial e nominal
                fator = (velocidade - vel_corte_inicial) / (vel_nominal - vel_corte_inicial)
                potencia = potencia_nominal * (fator ** 3)
            elif velocidade < vel_corte_final:
                # Potência nominal entre velocidade nominal e corte final
                potencia = potencia_nominal
            else:
                # Turbina desligada por segurança
                potencia = 0.0
            
            # Calcular energia (assumindo 1 hora por ponto)
            energia = potencia  # kWh para 1 hora
            
            # Potência disponível no vento
            potencia_vento = 0.5 * densidade_ar * area_rotor * (velocidade ** 3) / 1000  # kW
            
            # Coeficiente de potência
            cp = potencia / potencia_vento if potencia_vento > 0 else 0
            cp = min(cp, 0.59)  # Limite de Betz
            
            resultado = {
                'timestamp': dado.data_medicao,
                'velocidade_vento': velocidade,
                'potencia_gerada': potencia,
                'energia_gerada': energia,
                'potencia_vento': potencia_vento,
                'coeficiente_potencia': cp,
                'temperatura': dado.temperatura
            }
            
            resultados.append(resultado)
        
        return resultados
        
    except Exception as e:
        st.error(f"Erro na simulação: {str(e)}")
        return None

def mostrar_resultados_simulacao(resultados, dados_vento):
    """Mostra os resultados da simulação."""
    
    st.markdown("### 📊 Resultados da Simulação")
    
    # Converter para DataFrame
    df = pd.DataFrame(resultados)
    
    # Métricas principais
    energia_total = df['energia_gerada'].sum()
    potencia_media = df['potencia_gerada'].mean()
    fator_capacidade = (potencia_media / df['potencia_gerada'].max()) * 100 if df['potencia_gerada'].max() > 0 else 0
    horas_operacao = len(df[df['potencia_gerada'] > 0])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Energia Total", f"{energia_total:.1f} kWh")
    
    with col2:
        st.metric("Potência Média", f"{potencia_media:.1f} kW")
    
    with col3:
        st.metric("Fator de Capacidade", f"{fator_capacidade:.1f}%")
    
    with col4:
        st.metric("Horas de Operação", f"{horas_operacao}/{len(df)}")
    
    # Gráficos
    st.markdown("#### 📈 Gráficos de Performance")
    
    # Gráfico de potência vs velocidade
    fig_potencia = px.scatter(
        df,
        x='velocidade_vento',
        y='potencia_gerada',
        title='Curva de Potência',
        labels={'velocidade_vento': 'Velocidade do Vento (m/s)', 'potencia_gerada': 'Potência (kW)'},
        color='coeficiente_potencia',
        color_continuous_scale='viridis'
    )
    fig_potencia.update_layout(height=400)
    st.plotly_chart(fig_potencia, use_container_width=True)
    
    # Série temporal de potência
    fig_serie = px.line(
        df,
        x='timestamp',
        y='potencia_gerada',
        title='Produção de Energia ao Longo do Tempo',
        labels={'potencia_gerada': 'Potência (kW)', 'timestamp': 'Data/Hora'}
    )
    fig_serie.update_layout(height=400)
    st.plotly_chart(fig_serie, use_container_width=True)
    
    # Distribuição de velocidades e potência
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist_vento = px.histogram(
            df,
            x='velocidade_vento',
            title='Distribuição de Velocidades do Vento',
            labels={'velocidade_vento': 'Velocidade (m/s)', 'count': 'Frequência'}
        )
        fig_hist_vento.update_layout(height=300)
        st.plotly_chart(fig_hist_vento, use_container_width=True)
    
    with col2:
        fig_hist_potencia = px.histogram(
            df,
            x='potencia_gerada',
            title='Distribuição de Potência Gerada',
            labels={'potencia_gerada': 'Potência (kW)', 'count': 'Frequência'}
        )
        fig_hist_potencia.update_layout(height=300)
        st.plotly_chart(fig_hist_potencia, use_container_width=True)
    
    # Tabela de estatísticas
    st.markdown("#### 📋 Estatísticas Detalhadas")
    
    estatisticas = {
        'Métrica': [
            'Energia Total (kWh)',
            'Energia Média Diária (kWh)',
            'Potência Máxima (kW)',
            'Potência Média (kW)',
            'Fator de Capacidade (%)',
            'Horas de Operação',
            'Velocidade Média do Vento (m/s)',
            'Velocidade Máxima do Vento (m/s)',
            'Coeficiente de Potência Médio'
        ],
        'Valor': [
            f"{energia_total:.1f}",
            f"{energia_total / (len(df) / 24):.1f}",
            f"{df['potencia_gerada'].max():.1f}",
            f"{potencia_media:.1f}",
            f"{fator_capacidade:.1f}",
            f"{horas_operacao}",
            f"{df['velocidade_vento'].mean():.2f}",
            f"{df['velocidade_vento'].max():.2f}",
            f"{df['coeficiente_potencia'].mean():.3f}"
        ]
    }
    
    df_stats = pd.DataFrame(estatisticas)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

def analisar_viabilidade_localidade(dados, nome_localidade):
    """Analisa a viabilidade eólica de uma localidade."""
    
    # Calcular estatísticas básicas
    velocidades = [d.velocidade_vento for d in dados]
    vel_media = np.mean(velocidades)
    vel_max = np.max(velocidades)
    vel_min = np.min(velocidades)
    
    # Classificação do potencial eólico
    if vel_media >= 7.0:
        classificacao = "🟢 Excelente"
        cor = "green"
    elif vel_media >= 5.5:
        classificacao = "🟡 Bom"
        cor = "orange"
    elif vel_media >= 4.0:
        classificacao = "🟠 Moderado"
        cor = "orange"
    else:
        classificacao = "🔴 Baixo"
        cor = "red"
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Velocidade Média", f"{vel_media:.2f} m/s")
        st.metric("Velocidade Máxima", f"{vel_max:.2f} m/s")
    
    with col2:
        st.markdown(f"**Potencial Eólico:** {classificacao}")
        
        # Estimar fator de capacidade
        if vel_media >= 7.0:
            fator_capacidade_est = 35
        elif vel_media >= 5.5:
            fator_capacidade_est = 25
        elif vel_media >= 4.0:
            fator_capacidade_est = 15
        else:
            fator_capacidade_est = 5
        
        st.metric("Fator de Capacidade Estimado", f"{fator_capacidade_est}%")
    
    with col3:
        # Horas com vento útil (>3 m/s)
        horas_uteis = len([v for v in velocidades if v >= 3.0])
        percent_uteis = (horas_uteis / len(velocidades)) * 100
        
        st.metric("Horas com Vento Útil", f"{percent_uteis:.1f}%")
        st.metric("Dados Analisados", f"{len(dados)} registros")
    
    # Gráfico de distribuição
    df_local = pd.DataFrame({'velocidade': velocidades})
    
    fig_hist = px.histogram(
        df_local,
        x='velocidade',
        title=f'Distribuição de Velocidades - {nome_localidade}',
        labels={'velocidade': 'Velocidade do Vento (m/s)', 'count': 'Frequência'}
    )
    fig_hist.update_layout(height=300)
    st.plotly_chart(fig_hist, use_container_width=True)

if __name__ == "__main__":
    main()
