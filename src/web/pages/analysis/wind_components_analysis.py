"""
Página de Análise de Componentes do Vento

Esta página implementa a simulação dos componentes do vento:
- Vento médio (Mean Wind)
- Ondas (Waves) 
- Turbulência (Turbulence)
- Fluxo de ar resultante
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from analysis_tools.wind_components import WindComponentsSimulator
from analysis_tools.visualization import AnalysisVisualizer
from meteorological.meteorological_data.repository import MeteorologicalDataRepository


def safe_get_city_name(cidade_obj):
    """Extrai nome da cidade de forma segura."""
    if isinstance(cidade_obj, dict):
        if 'cidade' in cidade_obj and hasattr(cidade_obj['cidade'], 'nome'):
            return cidade_obj['cidade'].nome
        elif 'cidade' in cidade_obj and isinstance(cidade_obj['cidade'], dict):
            return cidade_obj['cidade'].get('nome', 'N/A')
        elif 'nome' in cidade_obj:
            return cidade_obj['nome']
    elif hasattr(cidade_obj, 'nome'):
        return cidade_obj.nome
    return 'cidade'


def render_wind_components_tab():
    """Renderiza a aba de análise de componentes do vento."""
    
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">🌊 Simulação dos Componentes do Vento</h4>
        <p>Análise dos componentes que formam o vento real: vento médio, ondas e turbulência</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar se parâmetros anteriores foram configurados
    if not st.session_state.analysis_state.get('wind_profile_data'):
        st.warning("⚠️ Execute a análise do perfil de vento primeiro.")
        return
    
    wind_profile_data = st.session_state.analysis_state['wind_profile_data']
    cidade_selected = st.session_state.analysis_state['cidade_selected']
    altura_turbina = st.session_state.analysis_state['altura_turbina']
    
    # Obter velocidade corrigida do perfil de vento
    corrected_speeds = wind_profile_data['corrected_speeds']
    velocidade_corrigida = (corrected_speeds['power_law_speed'] + corrected_speeds['logarithmic_speed']) / 2
    
    # Obter dados meteorológicos para condições reais
    try:
        met_repo = MeteorologicalDataRepository()
        
        # Extrair cidade_id de forma segura
        cidade_id = None
        if isinstance(cidade_selected, dict):
            if 'cidade' in cidade_selected and hasattr(cidade_selected['cidade'], 'id'):
                cidade_id = cidade_selected['cidade'].id
            elif 'cidade' in cidade_selected and isinstance(cidade_selected['cidade'], dict):
                cidade_id = cidade_selected['cidade'].get('id')
            elif 'id' in cidade_selected:
                cidade_id = cidade_selected['id']
        elif hasattr(cidade_selected, 'id'):
            cidade_id = cidade_selected.id
        
        if not cidade_id:
            st.error("❌ Erro ao obter ID da cidade selecionada.")
            st.info(f"Debug: cidade_selected = {cidade_selected}")
            return
            
        dados_meteorologicos = met_repo.buscar_por_cidade(cidade_id)
        
        # Calcular condições médias
        temperaturas = [d.temperatura for d in dados_meteorologicos if d.temperatura]
        umidades = [d.umidade for d in dados_meteorologicos if d.umidade]
        
        temperatura_media = np.mean(temperaturas) if temperaturas else 20.0
        umidade_media = np.mean(umidades) if umidades else 60.0
        
    except Exception as e:
        st.warning(f"Erro ao carregar condições meteorológicas: {str(e)}")
        temperatura_media = 20.0
        umidade_media = 60.0
    
    # Seção 1: Condições de Entrada
    st.markdown("### 📊 Condições de Entrada")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Altura da Turbina", f"{altura_turbina:.0f} m")
    
    with col2:
        st.metric("Velocidade Corrigida", f"{velocidade_corrigida:.2f} m/s")
    
    with col3:
        st.metric("Temperatura Média", f"{temperatura_media:.1f} °C")
    
    with col4:
        st.metric("Umidade Média", f"{umidade_media:.0f} %")
    
    # Seção 2: Configuração da Simulação
    st.markdown("---")
    st.markdown("### ⚙️ Configuração da Simulação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Parâmetros Temporais**")
        
        duracao = st.slider(
            "Duração da Simulação (horas):",
            min_value=1.0,
            max_value=168.0,  # 1 semana
            value=24.0,
            step=1.0,
            help="Período de tempo para simulação"
        )
        
        pontos = st.slider(
            "Número de Pontos:",
            min_value=100,
            max_value=2000,
            value=500,
            step=50,
            help="Resolução temporal da simulação"
        )
        
        resolucao_temporal = duracao / pontos * 60  # em minutos
        st.info(f"Resolução: {resolucao_temporal:.1f} min/ponto")
    
    with col2:
        st.markdown("**Parâmetros dos Componentes**")
        
        # Velocidade base (baseada na corrigida)
        velocidade_base = st.number_input(
            "Velocidade Base (m/s):",
            min_value=0.1,
            max_value=30.0,
            value=velocidade_corrigida,
            step=0.1,
            help="Velocidade média do vento"
        )
        
        # Amplitude das ondas
        amplitude_ondas = st.slider(
            "Amplitude das Ondas:",
            min_value=0.1,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Intensidade das flutuações de média frequência"
        )
        
        # Intensidade da turbulência
        intensidade_turbulencia = st.slider(
            "Intensidade da Turbulência:",
            min_value=0.1,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Intensidade das flutuações de alta frequência"
        )
    
    # Seção 3: Método de Turbulência
    st.markdown("---")
    st.markdown("### 🌪️ Configuração da Turbulência")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        metodo_turbulencia = st.selectbox(
            "Método de Geração:",
            ['rayleigh', 'normal', 'uniform'],
            index=0,
            help="Distribuição estatística para gerar turbulência"
        )
        
        metodo_combinacao = st.selectbox(
            "Método de Combinação:",
            ['weighted', 'additive', 'multiplicative'],
            index=0,
            help="Como combinar os componentes do vento"
        )
    
    with col2:
        # Informações sobre o método selecionado
        simulator = WindComponentsSimulator()
        methods_info = simulator.get_turbulence_methods_info()
        
        if metodo_turbulencia in methods_info:
            info = methods_info[metodo_turbulencia]
            st.markdown(f"""
            **{info['description']}**
            
            **Características:** {info['characteristics']}
            
            **Uso:** {info['use_case']}
            """)
    
    # Opções avançadas
    with st.expander("🔧 Configurações Avançadas"):
        col1, col2 = st.columns(2)
        
        with col1:
            usar_condicoes_reais = st.checkbox(
                "Usar Condições Meteorológicas Reais",
                value=True,
                help="Ajustar turbulência baseada em temperatura e umidade"
            )
            
            if usar_condicoes_reais:
                st.info(f"Ajuste automático baseado em T={temperatura_media:.1f}°C e RH={umidade_media:.0f}%")
        
        with col2:
            seed_personalizada = st.checkbox("Seed Personalizada para Reprodutibilidade")
            
            if seed_personalizada:
                seed_value = st.number_input(
                    "Seed:",
                    min_value=1,
                    max_value=9999,
                    value=42,
                    step=1
                )
            else:
                seed_value = None
    
    # Botão para executar simulação
    st.markdown("---")
    
    if st.button("🌊 Executar Simulação dos Componentes", type="primary", use_container_width=True):
        
        with st.spinner("Simulando componentes do vento..."):
            try:
                # Configurar seed se especificada
                if seed_value:
                    np.random.seed(seed_value)
                
                # Executar simulação
                if usar_condicoes_reais:
                    weather_data = {
                        'mean_speed': velocidade_base,
                        'temperature': temperatura_media,
                        'humidity': umidade_media
                    }
                    
                    components = simulator.simulate_real_wind_conditions(
                        weather_data=weather_data,
                        duration=duracao,
                        points=pontos
                    )
                else:
                    components = simulator.simulate_wind_components(
                        duration=duracao,
                        points=pontos,
                        base_speed=velocidade_base,
                        wave_amplitude=amplitude_ondas,
                        turbulence_intensity=intensidade_turbulencia,
                        combination_method=metodo_combinacao
                    )
                
                # Análise estatística
                analysis = simulator.analyze_components(components)
                
                # Salvar resultados no session state
                st.session_state.analysis_state['wind_components_data'] = {
                    'components': components,
                    'analysis': analysis,
                    'parameters': {
                        'duracao': duracao,
                        'pontos': pontos,
                        'velocidade_base': velocidade_base,
                        'amplitude_ondas': amplitude_ondas,
                        'intensidade_turbulencia': intensidade_turbulencia,
                        'metodo_turbulencia': metodo_turbulencia,
                        'metodo_combinacao': metodo_combinacao,
                        'usar_condicoes_reais': usar_condicoes_reais
                    }
                }
                
                st.success("✅ Simulação dos componentes concluída!")
                
            except Exception as e:
                st.error(f"Erro na simulação: {str(e)}")
                return
    
    # Exibir resultados se disponíveis
    wind_components_data = st.session_state.analysis_state.get('wind_components_data')
    
    if wind_components_data:
        components = wind_components_data['components']
        analysis = wind_components_data['analysis']
        parameters = wind_components_data['parameters']
        
        st.markdown("---")
        st.markdown("### 📈 Resultados da Simulação")
        
        # Gráfico principal dos componentes
        visualizer = AnalysisVisualizer()
        fig_components = visualizer.plot_wind_components(
            components=components,
            height=800
        )
        
        st.plotly_chart(fig_components, use_container_width=True)
        
        # Cards de resumo estatístico
        st.markdown("### 📊 Análise Estatística")
        
        visualizer.create_analysis_summary_cards(analysis)
        
        # Tabela de estatísticas detalhadas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Estatísticas dos Componentes**")
            
            stats_data = []
            for component in ['mean_wind', 'waves', 'turbulence', 'air_flow']:
                stats = analysis[component]
                display_name = {
                    'mean_wind': 'Vento Médio',
                    'waves': 'Ondas',
                    'turbulence': 'Turbulência',
                    'air_flow': 'Fluxo de Ar'
                }[component]
                
                stats_data.append({
                    'Componente': display_name,
                    'Média': f"{stats['mean']:.2f}",
                    'Desvio': f"{stats['std']:.2f}",
                    'Mín': f"{stats['min']:.2f}",
                    'Máx': f"{stats['max']:.2f}"
                })
            
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True)
        
        with col2:
            st.markdown("**Correlações com Fluxo de Ar**")
            
            correlations = analysis['correlations']
            corr_data = [
                {'Componente': 'Vento Médio', 'Correlação': f"{correlations['mean_wind_vs_air_flow']:.3f}"},
                {'Componente': 'Ondas', 'Correlação': f"{correlations['waves_vs_air_flow']:.3f}"},
                {'Componente': 'Turbulência', 'Correlação': f"{correlations['turbulence_vs_air_flow']:.3f}"}
            ]
            
            df_corr = pd.DataFrame(corr_data)
            st.dataframe(df_corr, use_container_width=True)
            
            # Energia dos componentes
            st.markdown("**Energia dos Componentes**")
            energy = analysis['energy']
            total_energy = sum(energy.values())
            
            for component, energia in energy.items():
                display_name = {
                    'mean_wind_energy': 'Vento Médio',
                    'waves_energy': 'Ondas', 
                    'turbulence_energy': 'Turbulência',
                    'air_flow_energy': 'Fluxo de Ar'
                }[component]
                
                percentual = (energia / total_energy) * 100
                st.write(f"**{display_name}:** {percentual:.1f}%")
        
        # DataFrame completo para análise
        st.markdown("### 📋 Dados Completos da Simulação")
        
        df_components = simulator.generate_analysis_dataframe(components)
        
        # Estatísticas do fluxo de ar resultante
        fluxo_medio = np.mean(components.air_flow)
        fluxo_std = np.std(components.air_flow)
        fluxo_min = np.min(components.air_flow)
        fluxo_max = np.max(components.air_flow)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Velocidade Média", f"{fluxo_medio:.2f} m/s")
        
        with col2:
            st.metric("Desvio Padrão", f"{fluxo_std:.2f} m/s")
        
        with col3:
            st.metric("Velocidade Mínima", f"{fluxo_min:.2f} m/s")
        
        with col4:
            st.metric("Velocidade Máxima", f"{fluxo_max:.2f} m/s")
        
        # Mostrar amostra dos dados
        st.dataframe(df_components.head(20), use_container_width=True)
        
        if st.button("📥 Download Dados Completos"):
            csv = df_components.to_csv(index=False)
            cidade_nome = safe_get_city_name(cidade_selected)
            st.download_button(
                label="💾 Baixar CSV",
                data=csv,
                file_name=f"componentes_vento_{cidade_nome}.csv",
                mime="text/csv"
            )
        
        # Informações técnicas
        with st.expander("🔧 Detalhes Técnicos da Simulação"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Parâmetros da Simulação:**
                - Duração: {parameters['duracao']:.0f} horas
                - Pontos: {parameters['pontos']} 
                - Resolução: {(parameters['duracao']/parameters['pontos']*60):.1f} min/ponto
                - Velocidade base: {parameters['velocidade_base']:.2f} m/s
                - Método turbulência: {parameters['metodo_turbulencia']}
                - Método combinação: {parameters['metodo_combinacao']}
                """)
            
            with col2:
                st.markdown(f"""
                **Resultados do Fluxo de Ar:**
                - Velocidade média: {fluxo_medio:.2f} m/s
                - Variabilidade: {(fluxo_std/fluxo_medio*100):.1f}%
                - Faixa operacional: {fluxo_min:.2f} - {fluxo_max:.2f} m/s
                - Condições reais: {'Sim' if parameters['usar_condicoes_reais'] else 'Não'}
                """)
        
        # Recomendações
        st.markdown("### 💡 Recomendações")
        
        # Análise da variabilidade
        variabilidade = fluxo_std / fluxo_medio
        
        if variabilidade < 0.1:
            st.success("✅ **Vento estável** - Condições excelentes para geração contínua.")
        elif variabilidade < 0.2:
            st.info("ℹ️ **Vento moderadamente variável** - Boas condições para operação.")
        else:
            st.warning("⚠️ **Vento muito variável** - Considerar sistemas de controle avançado.")
        
        # Análise da velocidade média
        if fluxo_medio > 8:
            st.success("✅ **Excelente recurso eólico** - Alta velocidade média.")
        elif fluxo_medio > 5:
            st.info("ℹ️ **Bom recurso eólico** - Velocidade adequada para geração.")
        else:
            st.warning("⚠️ **Recurso eólico limitado** - Avaliar viabilidade econômica.")
