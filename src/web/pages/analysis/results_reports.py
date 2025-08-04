"""
Página de Resultados e Relatórios

Esta página consolida todos os resultados das análises:
- Resumo executivo
- Gráficos comparativos
- Relatórios técnicos
- Exportação de dados
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from analysis_tools.visualization import AnalysisVisualizer


def safe_get_attr(obj, attr, default='N/A'):
    """Acessa atributo de forma segura, lidando com objetos e dicionários."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)


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
    return 'N/A'


def render_results_reports_tab():
    """Renderiza a aba de resultados e relatórios."""
    
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📊 Resultados e Relatórios</h4>
        <p>Consolidação completa das análises e geração de relatórios técnicos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar se todas as análises foram executadas
    required_analyses = [
        'wind_profile_data',
        'wind_components_data', 
        'turbine_simulation_data'
    ]
    
    missing_analyses = []
    for analysis in required_analyses:
        if not st.session_state.analysis_state.get(analysis):
            missing_analyses.append(analysis)
    
    if missing_analyses:
        st.warning("⚠️ Execute todas as análises anteriores primeiro:")
        for analysis in missing_analyses:
            analysis_names = {
                'wind_profile_data': 'Análise do Perfil de Vento',
                'wind_components_data': 'Simulação dos Componentes do Vento',
                'turbine_simulation_data': 'Simulação da Turbina Eólica'
            }
            st.write(f"- {analysis_names[analysis]}")
        return
    
    # Obter todos os dados das análises
    wind_profile_data = st.session_state.analysis_state['wind_profile_data']
    wind_components_data = st.session_state.analysis_state['wind_components_data']
    turbine_simulation_data = st.session_state.analysis_state['turbine_simulation_data']
    
    # Dados gerais
    cidade_selected = st.session_state.analysis_state['cidade_selected']
    turbina_selected = st.session_state.analysis_state['turbina_selected']
    altura_turbina = st.session_state.analysis_state['altura_turbina']
    
    # Seção 1: Resumo Executivo
    st.markdown("## 📋 Resumo Executivo")
    
    # Cards principais de resultados
    col1, col2, col3, col4 = st.columns(4)
    
    operational_stats = turbine_simulation_data['operational_stats']
    
    with col1:
        st.metric(
            "Fator de Capacidade",
            f"{operational_stats.get('efficiency_stats', {}).get('capacity_factor', 0):.1f}%",
            delta="Meta: >25%"
        )
    
    with col2:
        st.metric(
            "Energia Anual",
            f"{operational_stats.get('operational_stats', {}).get('energy_production', 0):.0f} kWh",
            delta="Produção estimada"
        )
    
    with col3:
        velocidade_media = np.mean(wind_components_data['components'].air_flow)
        st.metric(
            "Velocidade Média",
            f"{velocidade_media:.2f} m/s",
            delta="Corrigida para altura"
        )
    
    with col4:
        potencia_nominal = float(safe_get_attr(turbina_selected, 'rated_power_kw', 1000))
        avg_power = operational_stats.get('operational_stats', {}).get('avg_power', 0)
        st.metric(
            "Potência Média",
            f"{avg_power:.1f} kW",
            delta=f"{(avg_power/potencia_nominal*100):.1f}% nominal"
        )
    
    # Classificação do recurso
    cf = operational_stats.get('efficiency_stats', {}).get('capacity_factor', 0)
    
    if cf > 0.35:
        recurso_class = "🟢 Excelente"
        recurso_color = "success"
    elif cf > 0.25:
        recurso_class = "🟡 Bom"
        recurso_color = "info"
    elif cf > 0.15:
        recurso_class = "🟠 Moderado"
        recurso_color = "warning"
    else:
        recurso_class = "🔴 Insuficiente"
        recurso_color = "error"
    
    modelo_turbina = safe_get_attr(turbina_selected, 'model', 'Turbina')
    cidade_nome = safe_get_city_name(cidade_selected)
    
    st.markdown(f"""
    <div style="padding: 1rem; border-left: 4px solid {'#28a745' if recurso_color == 'success' else '#17a2b8' if recurso_color == 'info' else '#ffc107' if recurso_color == 'warning' else '#dc3545'}; background-color: rgba(255,255,255,0.1); margin: 1rem 0;">
        <h4>🎯 Classificação do Recurso Eólico: {recurso_class}</h4>
        <p>Baseado no fator de capacidade de {cf*100:.1f}% para a turbina {modelo_turbina} em {cidade_nome}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Seção 2: Comparação de Métodos
    st.markdown("---")
    st.markdown("## 🔄 Comparação de Métodos de Correção")
    
    visualizer = AnalysisVisualizer()
    
    # Gráfico comparativo dos perfis de vento
    st.markdown("### Perfis de Vento")
    
    fig_comparison = visualizer.plot_wind_profile_comparison(
        profile_data=wind_profile_data,
        height=600
    )
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Tabela comparativa
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Velocidades Corrigidas**")
        
        corrected_speeds = wind_profile_data['corrected_speeds']
        original_speed = wind_profile_data['parameters']['v_ref']
        comparison_data = [
            {'Método': 'Velocidade Original', 'Velocidade': f"{original_speed:.2f} m/s"},
            {'Método': 'Lei da Potência', 'Velocidade': f"{corrected_speeds['power_law_speed']:.2f} m/s"},
            {'Método': 'Lei Logarítmica', 'Velocidade': f"{corrected_speeds['logarithmic_speed']:.2f} m/s"},
            {'Método': 'Diferença Relativa', 'Velocidade': f"{abs(corrected_speeds['power_law_speed'] - corrected_speeds['logarithmic_speed']):.2f} m/s"}
        ]
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
    
    with col2:
        st.markdown("**Impacto na Potência**")
        
        # Calcular impacto aproximado na potência (P ∝ V³)
        v_orig = wind_profile_data['parameters']['v_ref']
        v_power = corrected_speeds['power_law_speed']
        v_log = corrected_speeds['logarithmic_speed']
        
        power_impact_data = [
            {'Método': 'Velocidade Original', 'Impacto': f"{(v_orig**3/v_orig**3*100):.1f}%"},
            {'Método': 'Lei da Potência', 'Impacto': f"{(v_power**3/v_orig**3*100):.1f}%"},
            {'Método': 'Lei Logarítmica', 'Impacto': f"{(v_log**3/v_orig**3*100):.1f}%"},
            {'Método': 'Diferença Power/Log', 'Impacto': f"{abs(v_power**3/v_orig**3 - v_log**3/v_orig**3)*100:.1f}%"}
        ]
        
        df_power_impact = pd.DataFrame(power_impact_data)
        st.dataframe(df_power_impact, use_container_width=True)
    
    # Seção 3: Análise Temporal Completa
    st.markdown("---")
    st.markdown("## ⏱️ Análise Temporal Completa")
    
    # Gráfico temporal integrado
    fig_temporal = visualizer.plot_complete_temporal_analysis(
        wind_components=wind_components_data['components'],
        performance_data=turbine_simulation_data.get('performance_data'),
        height=800
    )
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Estatísticas temporais
    col1, col2, col3 = st.columns(3)
    
    components = wind_components_data['components']
    
    with col1:
        st.markdown("**Variabilidade do Vento**")
        
        air_flow_std = np.std(components.air_flow)
        air_flow_mean = np.mean(components.air_flow)
        coef_variacao = air_flow_std / air_flow_mean
        
        st.metric("Coeficiente de Variação", f"{coef_variacao:.3f}")
        st.metric("Desvio Padrão", f"{air_flow_std:.2f} m/s")
        st.metric("Amplitude", f"{np.ptp(components.air_flow):.2f} m/s")
    
    with col2:
        st.markdown("**Distribuição de Frequência**")
        
        # Calcular distribuição por faixas
        bins = np.arange(0, max(components.air_flow) + 2, 2)
        hist, _ = np.histogram(components.air_flow, bins=bins)
        freq_percentages = hist / len(components.air_flow) * 100
        
        faixa_max = np.argmax(freq_percentages)
        st.metric("Faixa Mais Frequente", f"{bins[faixa_max]:.0f}-{bins[faixa_max+1]:.0f} m/s")
        st.metric("Frequência Máxima", f"{freq_percentages[faixa_max]:.1f}%")
        
        # Percentil 90
        p90 = np.percentile(components.air_flow, 90)
        st.metric("Percentil 90", f"{p90:.2f} m/s")
    
    with col3:
        st.markdown("**Energia dos Componentes**")
        
        analysis = wind_components_data['analysis']
        energy = analysis['energy']
        total_energy = sum(energy.values())
        
        for component, energia in energy.items():
            if component == 'air_flow_energy':
                continue
            
            display_name = {
                'mean_wind_energy': 'Vento Médio',
                'waves_energy': 'Ondas',
                'turbulence_energy': 'Turbulência'
            }[component]
            
            percentual = (energia / total_energy) * 100
            st.metric(display_name, f"{percentual:.1f}%")
    
    # Seção 4: Relatório Técnico Detalhado
    st.markdown("---")
    st.markdown("## 📊 Relatório Técnico Detalhado")
    
    # Abas para diferentes seções do relatório
    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 Dados de Entrada",
        "🌪️ Análise do Vento", 
        "⚡ Performance da Turbina",
        "💰 Análise Econômica"
    ])
    try:
        with tab1:
            st.markdown("### Especificações do Projeto")

            col1, col2 = st.columns(2)

            with col1:
                # Obter dados da cidade de forma segura
                try:
                    nome_cidade = getattr(cidade_selected, 'nome', None) or cidade_selected.get('nome', 'N/A')
                    estado_cidade = getattr(cidade_selected, 'estado', None) or cidade_selected.get('estado', 'N/A')
                    regiao_cidade = getattr(cidade_selected, 'regiao', None) or cidade_selected.get('regiao', 'N/A')
                    pais_cidade = getattr(cidade_selected, 'pais', None) or cidade_selected.get('pais', 'N/A')
                    lat_cidade = getattr(cidade_selected, 'latitude', None) or cidade_selected.get('latitude', 0)
                    lon_cidade = getattr(cidade_selected, 'longitude', None) or cidade_selected.get('longitude', 0)
                except:
                    # Fallback para objeto sem método get
                    nome_cidade = getattr(cidade_selected, 'nome', 'N/A')
                    estado_cidade = getattr(cidade_selected, 'estado', 'N/A')
                    regiao_cidade = getattr(cidade_selected, 'regiao', 'N/A')
                    pais_cidade = getattr(cidade_selected, 'pais', 'N/A')
                    lat_cidade = getattr(cidade_selected, 'latitude', 0)
                    lon_cidade = getattr(cidade_selected, 'longitude', 0)

                st.markdown(f"""
                **Localização:**
                - Cidade: {nome_cidade}
                - Estado: {estado_cidade}
                - Região: {regiao_cidade}
                - País: {pais_cidade}

                **Coordenadas:**
                - Latitude: {lat_cidade}°
                - Longitude: {lon_cidade}°
                """)

            with col2:
                # Obter dados da turbina de forma segura
                try:
                    fabricante_turbina = getattr(turbina_selected, 'fabricante', None) or getattr(turbina_selected, 'marca_fabricante', 'N/A')
                    modelo_turbina = getattr(turbina_selected, 'modelo', 'N/A')
                    potencia_turbina = getattr(turbina_selected, 'potencia_nominal', 0)
                    diametro_turbina = getattr(turbina_selected, 'diametro_rotor', 0)
                except:
                    fabricante_turbina = 'N/A'
                    modelo_turbina = 'N/A'
                    potencia_turbina = 0
                    diametro_turbina = 0

                st.markdown(f"""
                **Turbina Selecionada:**
                - Fabricante: {fabricante_turbina}
                - Modelo: {modelo_turbina}
                - Potência Nominal: {potencia_turbina/1000:.1f} kW
                - Diâmetro do Rotor: {diametro_turbina:.1f} m
                - Altura da Torre: {altura_turbina:.0f} m
                - Área de Varredura: {np.pi * (diametro_turbina/2)**2:.0f} m²
                """)

            # Parâmetros das análises
            st.markdown("### Parâmetros Utilizados")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Perfil de Vento:**")
                profile_params = wind_profile_data['parameters']
                st.write(f"- Altura referência: {profile_params['altura_referencia']:.0f} m")
                st.write(f"- Altura turbina: {profile_params['altura_turbina']:.0f} m")
                st.write(f"- Tipo terreno: {profile_params['tipo_terreno']}")
                st.write(f"- Expoente α: {profile_params['expoente_alpha']:.3f}")
                st.write(f"- Rugosidade z₀: {profile_params['rugosidade_z0']:.4f}")

            with col2:
                st.markdown("**Componentes do Vento:**")
                comp_params = wind_components_data['parameters']
                st.write(f"- Duração: {comp_params['duracao']:.0f} h")
                st.write(f"- Pontos: {comp_params['pontos']}")
                st.write(f"- Velocidade base: {comp_params['velocidade_base']:.2f} m/s")
                st.write(f"- Método turbulência: {comp_params['metodo_turbulencia']}")
                st.write(f"- Método combinação: {comp_params['metodo_combinacao']}")

            with col3:
                st.markdown("**Simulação Turbina:**")
                turb_specs = turbine_simulation_data['turbine_specs']
                analysis_params = turbine_simulation_data['analysis_params']
                st.write(f"- Densidade ar: {analysis_params['air_density']:.3f} kg/m³")
                st.write(f"- Eficiência sistema: {turb_specs['system_efficiency']*100:.0f}%")
                st.write(f"- Perdas operacionais: {turb_specs['operational_losses']*100:.0f}%")
                st.write(f"- Método Cp: {analysis_params['cp_method']}")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados de entrada: {e}")

    try:
        with tab2:
            st.markdown("### Análise Detalhada do Recurso Eólico")

            # Distribuição de velocidades
            st.markdown("#### Distribuição de Velocidades")

            fig_dist = visualizer.plot_wind_speed_distribution(
                wind_speeds=components.air_flow,
                height=500
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            # Análise por faixas de vento
            st.markdown("#### Análise por Faixas de Vento")

            # Criar faixas de análise
            bins = np.arange(0, max(components.air_flow) + 2, 1)
            hist, bin_edges = np.histogram(components.air_flow, bins=bins)

            faixas_data = []
            for i in range(len(hist)):
                if hist[i] > 0:
                    faixa_inicio = bin_edges[i]
                    faixa_fim = bin_edges[i+1]
                    frequencia = hist[i] / len(components.air_flow) * 100

                    # Velocidades nesta faixa
                    mask = (components.air_flow >= faixa_inicio) & (components.air_flow < faixa_fim)
                    velocidades_faixa = components.air_flow[mask]

                    if len(velocidades_faixa) > 0:
                        vel_media = np.mean(velocidades_faixa)
                        # Potência média estimada (P ∝ V³)
                        potencia_relativa = (vel_media**3) / (np.mean(components.air_flow)**3)

                        faixas_data.append({
                            'Faixa (m/s)': f"{faixa_inicio:.0f}-{faixa_fim:.0f}",
                            'Frequência (%)': f"{frequencia:.1f}",
                            'Vel. Média (m/s)': f"{vel_media:.2f}",
                            'Potência Relativa': f"{potencia_relativa:.2f}x",
                            'Horas/Ano': f"{frequencia/100*8760:.0f}"
                        })

            df_faixas = pd.DataFrame(faixas_data)
            st.dataframe(df_faixas, use_container_width=True)

            # Rosa dos ventos simplificada
            st.markdown("#### Características do Vento")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Estatísticas Descritivas:**")

                stats_vento = {
                    'Velocidade Média': f"{np.mean(components.air_flow):.2f} m/s",
                    'Velocidade Mediana': f"{np.median(components.air_flow):.2f} m/s",
                    'Velocidade Moda': f"{bins[np.argmax(hist)]:.0f}-{bins[np.argmax(hist)+1]:.0f} m/s",
                    'Desvio Padrão': f"{np.std(components.air_flow):.2f} m/s",
                    'Velocidade Mínima': f"{np.min(components.air_flow):.2f} m/s",
                    'Velocidade Máxima': f"{np.max(components.air_flow):.2f} m/s",
                    'Coeficiente de Variação': f"{np.std(components.air_flow)/np.mean(components.air_flow):.3f}"
                }

                for stat, value in stats_vento.items():
                    st.write(f"**{stat}:** {value}")

            with col2:
                st.markdown("**Percentis:**")

                percentis = [10, 25, 50, 75, 90, 95, 99]
                for p in percentis:
                    valor = np.percentile(components.air_flow, p)
                    st.write(f"**P{p}:** {valor:.2f} m/s")
    except Exception as e:
        st.error(f"Erro ao carregar análise do vento: {e}")
    
    try:
        with tab3:
            st.markdown("### Performance Operacional da Turbina")

            # Curva de potência com dados reais
            st.markdown("#### Curva de Potência vs Dados Reais")

            power_curve = turbine_simulation_data['power_curve']
            fig_power_real = visualizer.plot_power_curve_with_real_data(
                power_curve=power_curve,
                real_wind_speeds=components.air_flow,
                height=600
            )
            st.plotly_chart(fig_power_real, use_container_width=True)

            # Indicadores de performance
            st.markdown("#### Indicadores de Performance")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                cf = operational_stats.get('efficiency_stats', {}).get('capacity_factor', 0)
                st.metric("Fator de Capacidade", f"{cf:.1f}%")

                # Benchmark
                if cf > 0.35:
                    st.success("Excelente")
                elif cf > 0.25:
                    st.info("Bom")
                elif cf > 0.15:
                    st.warning("Moderado")
                else:
                    st.error("Insuficiente")

            with col2:
                energy_production = operational_stats.get('operational_stats', {}).get('energy_production', 0)
                # Calcular rendimento por m² (aproximação)
                rotor_area = 3.14159 * (40)**2  # Assumindo diâmetro de 80m
                energy_yield = energy_production / rotor_area if rotor_area > 0 else 0
                st.metric("Rendimento Energético", f"{energy_yield:.0f} kWh/m²")

                if energy_yield > 2000:
                    st.success("Alto")
                elif energy_yield > 1500:
                    st.info("Médio")
                else:
                    st.warning("Baixo")

            with col3:
                availability = operational_stats.get('operational_stats', {}).get('availability', 0)
                st.metric("Disponibilidade", f"{availability:.1f}%")

                if availability > 95:
                    st.success("Excelente")
                elif availability > 90:
                    st.info("Boa")
                else:
                    st.warning("Melhorável")

            with col4:
                avg_efficiency = operational_stats.get('efficiency_stats', {}).get('avg_cp', 0)
                st.metric("Eficiência Média", f"{avg_efficiency*100:.1f}%")

                if avg_efficiency > 0.40:
                    st.success("Alta")
                elif avg_efficiency > 0.30:
                    st.info("Média")
                else:
                    st.warning("Baixa")

            # Análise temporal de potência
            if turbine_simulation_data.get('performance_data'):
                st.markdown("#### Análise Temporal de Potência")

                performance_data = turbine_simulation_data['performance_data']

                # Estatísticas da potência gerada
                potencias = performance_data['power_output']

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Distribuição de Potência:**")

                    # Faixas de potência
                    pot_max = max(potencias)
                    pot_bins = np.linspace(0, pot_max, 11)
                    pot_hist, _ = np.histogram(potencias, bins=pot_bins)

                    pot_data = []
                    for i in range(len(pot_hist)):
                        if pot_hist[i] > 0:
                            pot_inicio = pot_bins[i]
                            pot_fim = pot_bins[i+1]
                            freq = pot_hist[i] / len(potencias) * 100

                            pot_data.append({
                                'Faixa (kW)': f"{pot_inicio:.0f}-{pot_fim:.0f}",
                                'Frequência (%)': f"{freq:.1f}",
                                'Horas/Ano': f"{freq/100*8760:.0f}"
                            })

                    df_pot = pd.DataFrame(pot_data)
                    st.dataframe(df_pot, use_container_width=True)

                with col2:
                    st.markdown("**Tempo em Diferentes Modos:**")

                    # Classificar operação
                    cut_in = turbina_selected.velocidade_corte_inicial
                    cut_out = turbina_selected.velocidade_corte_final
                    rated_speed = 12  # Estimativa típica

                    parado = np.sum(components.air_flow < cut_in) / len(components.air_flow) * 100
                    operacao_parcial = np.sum((components.air_flow >= cut_in) & (components.air_flow < rated_speed)) / len(components.air_flow) * 100
                    operacao_nominal = np.sum((components.air_flow >= rated_speed) & (components.air_flow < cut_out)) / len(components.air_flow) * 100
                    desligado = np.sum(components.air_flow >= cut_out) / len(components.air_flow) * 100

                    modos_data = [
                        {'Modo': 'Parado (< cut-in)', 'Tempo (%)': f"{parado:.1f}", 'Horas/Ano': f"{parado/100*8760:.0f}"},
                        {'Modo': 'Operação Parcial', 'Tempo (%)': f"{operacao_parcial:.1f}", 'Horas/Ano': f"{operacao_parcial/100*8760:.0f}"},
                        {'Modo': 'Operação Nominal', 'Tempo (%)': f"{operacao_nominal:.1f}", 'Horas/Ano': f"{operacao_nominal/100*8760:.0f}"},
                        {'Modo': 'Desligado (> cut-out)', 'Tempo (%)': f"{desligado:.1f}", 'Horas/Ano': f"{desligado/100*8760:.0f}"}
                    ]

                    df_modos = pd.DataFrame(modos_data)
                    st.dataframe(df_modos, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar performance da turbina: {e}")
    
    try:
        with tab4:
            st.markdown("### Análise Econômica e Viabilidade")

            # Parâmetros econômicos
            col1, col2, col3 = st.columns(3)

            with col1:
                preco_energia = st.number_input(
                    "Preço da Energia (R$/MWh):",
                    min_value=100.0,
                    max_value=800.0,
                    value=300.0,
                    step=10.0,
                    key="preco_energia_rel"
                )

            with col2:
                custo_investimento = st.number_input(
                    "Custo de Investimento (R$/kW):",
                    min_value=3000.0,
                    max_value=8000.0,
                    value=5000.0,
                    step=100.0,
                    key="custo_investimento_rel"
                )

            with col3:
                taxa_desconto = st.slider(
                    "Taxa de Desconto (% a.a.):",
                    min_value=5.0,
                    max_value=15.0,
                    value=8.0,
                    step=0.5,
                    key="taxa_desconto_rel"
                ) / 100

            # Cálculos econômicos
            potencia_kw = turbina_selected.potencia_nominal / 1000
            investimento_total = potencia_kw * custo_investimento
            energia_anual_kwh = operational_stats.get('operational_stats', {}).get('energy_production', 0)
            energia_anual_mwh = energia_anual_kwh / 1000  # Converter para MWh
            receita_anual = energia_anual_mwh * preco_energia

            # Custos operacionais
            custo_om_percent = 0.03  # 3% do investimento
            custo_om_anual = investimento_total * custo_om_percent

            # Seguros e outros
            outros_custos = investimento_total * 0.01  # 1% do investimento

            receita_liquida_anual = receita_anual - custo_om_anual - outros_custos

            # VPL e TIR (simplificado)
            vida_util = 20
            fluxos = [-investimento_total] + [receita_liquida_anual] * vida_util

            # VPL
            vpls = []
            for i, fluxo in enumerate(fluxos):
                if i == 0:
                    vpls.append(fluxo)
                else:
                    vpls.append(fluxo / ((1 + taxa_desconto) ** i))

            vpl = sum(vpls)

            # Payback simples
            payback = investimento_total / receita_liquida_anual

            # Resultados econômicos
            st.markdown("#### Indicadores Econômicos")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Investimento Total", f"R$ {investimento_total:,.0f}")

            with col2:
                st.metric("Receita Anual", f"R$ {receita_anual:,.0f}")

            with col3:
                st.metric("VPL (20 anos)", f"R$ {vpl:,.0f}")

                if vpl > 0:
                    st.success("Viável")
                else:
                    st.error("Inviável")

            with col4:
                st.metric("Payback Simples", f"{payback:.1f} anos")

                if payback < 10:
                    st.success("Rápido")
                elif payback < 15:
                    st.info("Moderado")
                else:
                    st.warning("Lento")

            # Análise de sensibilidade
            st.markdown("#### Análise de Sensibilidade")

            # Variação do preço da energia
            precos_teste = np.arange(200, 501, 50)
            vpls_preco = []

            for preco in precos_teste:
                receita_teste = energia_anual_mwh * preco
                receita_liquida_teste = receita_teste - custo_om_anual - outros_custos
                fluxos_teste = [-investimento_total] + [receita_liquida_teste] * vida_util

                vpl_teste = sum([f / ((1 + taxa_desconto) ** i) if i > 0 else f for i, f in enumerate(fluxos_teste)])
                vpls_preco.append(vpl_teste)

            fig_sensibilidade = visualizer.plot_sensitivity_analysis(
                precos_teste, vpls_preco, 
                "Preço da Energia (R$/MWh)", "VPL (R$)",
                height=500
            )
            st.plotly_chart(fig_sensibilidade, use_container_width=True)

            # Resumo da viabilidade
            st.markdown("#### Resumo da Viabilidade")

            if vpl > 0 and payback < 12:
                viabilidade = "🟢 PROJETO VIÁVEL"
                cor_viabilidade = "success"
            elif vpl > 0 or payback < 15:
                viabilidade = "🟡 PROJETO MARGINAL"
                cor_viabilidade = "warning"
            else:
                viabilidade = "🔴 PROJETO INVIÁVEL"
                cor_viabilidade = "error"

            st.markdown(f"""
            <div style="padding: 1rem; border-left: 4px solid {'#28a745' if cor_viabilidade == 'success' else '#ffc107' if cor_viabilidade == 'warning' else    '#dc3545'}; background-color: rgba(255,255,255,0.1); margin: 1rem 0;">
                <h4>{viabilidade}</h4>
                <p><strong>VPL:</strong> R$ {vpl:,.0f} | <strong>Payback:</strong> {payback:.1f} anos | <strong>TIR Estimada:</strong> {(receita_liquida_anual/ investimento_total*100):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao carregar análise econômica: {e}")
    
    # Seção 5: Exportação de Relatórios
    st.markdown("---")
    st.markdown("## 📥 Exportação de Resultados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Relatório Executivo", use_container_width=True):
            # Gerar relatório executivo
            relatorio_executivo = gerar_relatorio_executivo(
                cidade_selected, turbina_selected, altura_turbina,
                operational_stats, velocidade_media, cf
            )
            
            st.download_button(
                label="💾 Download Relatório Executivo",
                data=relatorio_executivo,
                file_name=f"relatorio_executivo_{nome_cidade}_{modelo_turbina}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📈 Dados Técnicos", use_container_width=True):
            # Compilar todos os dados técnicos
            dados_tecnicos = compilar_dados_tecnicos(
                wind_profile_data, wind_components_data, turbine_simulation_data
            )
            
            st.download_button(
                label="💾 Download Dados Técnicos",
                data=dados_tecnicos.to_csv(index=False),
                file_name=f"dados_tecnicos_{nome_cidade}_{modelo_turbina}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🔧 Parâmetros de Configuração", use_container_width=True):
            # JSON com todos os parâmetros
            config_data = {
                'projeto': {
                    'cidade': nome_cidade,
                    'turbina': turbina_selected.modelo,
                    'altura_turbina': altura_turbina,
                    'data_analise': datetime.now().isoformat()
                },
                'parametros_perfil_vento': wind_profile_data['parameters'],
                'parametros_componentes': wind_components_data['parameters'],
                'parametros_turbina': turbine_simulation_data['analysis_params'],
                'resultados_resumo': {
                    'fator_capacidade': operational_stats.get('efficiency_stats', {}).get('capacity_factor', 0),
                    'energia_anual': operational_stats.get('operational_stats', {}).get('energy_production', 0),
                    'velocidade_media': float(velocidade_media),
                    'potencia_media': operational_stats.get('operational_stats', {}).get('avg_power', 0)
                }
            }
            
            config_json = json.dumps(config_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="💾 Download Configuração",
                data=config_json,
                file_name=f"configuracao_{nome_cidade}_{modelo_turbina}.json",
                mime="application/json"
            )
    
    # Seção final: Recomendações
    st.markdown("---")
    st.markdown("## 💡 Recomendações Finais")
    
    gerar_recomendacoes_finais(operational_stats, velocidade_media, cf, vpl, payback)


def gerar_relatorio_executivo(cidade, turbina, altura, stats, vel_media, cf):
    """Gera relatório executivo em texto."""
    
    relatorio = f"""
RELATÓRIO EXECUTIVO - ANÁLISE DE VIABILIDADE EÓLICA
================================================

DADOS DO PROJETO
----------------
Localização: {cidade.nome}, {cidade.estado}
Coordenadas: {cidade.latitude}°, {cidade.longitude}°
Turbina: {turbina.fabricante} {turbina.modelo}
Potência Nominal: {turbina.potencia_nominal/1000:.1f} kW
Altura da Torre: {altura:.0f} m
Data da Análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESULTADOS PRINCIPAIS
--------------------
Fator de Capacidade: {cf*100:.1f}%
Energia Anual: {stats['annual_energy']:.0f} MWh
Velocidade Média do Vento: {vel_media:.2f} m/s
Potência Média: {stats['average_power']:.1f} kW
Rendimento Energético: {stats['energy_yield']:.0f} kWh/m²

CLASSIFICAÇÃO DO RECURSO
-----------------------
"""
    
    if cf > 0.35:
        relatorio += "EXCELENTE - Recurso eólico de alta qualidade\n"
    elif cf > 0.25:
        relatorio += "BOM - Recurso eólico adequado para geração\n"
    elif cf > 0.15:
        relatorio += "MODERADO - Recurso eólico limitado\n"
    else:
        relatorio += "INSUFICIENTE - Recurso eólico inadequado\n"
    
    relatorio += f"""
INDICADORES OPERACIONAIS
-----------------------
Disponibilidade: {stats['availability']*100:.1f}%
Horas de Operação/Ano: {stats['operating_hours']:.0f} h
Eficiência Média: {stats['average_efficiency']*100:.1f}%
Coeficiente de Potência Médio: {stats['average_cp']:.3f}

CONCLUSÃO
---------
"""
    
    if cf > 0.25:
        relatorio += "O projeto apresenta viabilidade técnica para geração de energia eólica."
    else:
        relatorio += "O projeto requer análise econômica detalhada devido ao recurso limitado."
    
    return relatorio


def compilar_dados_tecnicos(wind_profile, wind_components, turbine_sim):
    """Compila todos os dados técnicos em um DataFrame."""
    
    # Dados temporais dos componentes de vento
    components = wind_components['components']
    
    # Performance da turbina (se disponível)
    performance_data = turbine_sim.get('performance_data')
    
    # Criar DataFrame principal
    data = {
        'tempo_h': np.arange(len(components.air_flow)) * (wind_components['parameters']['duracao'] / len(components.air_flow)),
        'vento_medio': components.mean_wind,
        'ondas': components.waves,
        'turbulencia': components.turbulence,
        'fluxo_ar': components.air_flow
    }
    
    if performance_data:
        data.update({
            'potencia_kw': performance_data['power_output'],
            'rpm': performance_data.get('rpm', [0] * len(components.air_flow)),
            'cp': performance_data.get('cp', [0] * len(components.air_flow)),
            'tsr': performance_data.get('tsr', [0] * len(components.air_flow))
        })
    
    return pd.DataFrame(data)


def gerar_recomendacoes_finais(stats, vel_media, cf, vpl, payback):
    """Gera recomendações finais baseadas nos resultados."""
    
    st.markdown("### 🎯 Recomendações Técnicas")
    
    # Recomendações baseadas no recurso eólico
    if vel_media < 5:
        st.warning("⚠️ **Velocidade baixa:** Considerar turbina de baixa velocidade de cut-in")
    elif vel_media > 10:
        st.success("✅ **Excelente recurso:** Considerar parque eólico de maior porte")
    
    if cf < 0.15:
        st.error("❌ **Fator de capacidade baixo:** Reavaliar localização ou tecnologia")
    elif cf > 0.35:
        st.success("✅ **Excelente performance:** Projeto altamente viável")
    
    # Recomendações operacionais
    if stats['availability'] < 0.90:
        st.warning("⚠️ **Baixa disponibilidade:** Revisar estratégias de manutenção")
    
    if stats['average_efficiency'] < 0.30:
        st.warning("⚠️ **Baixa eficiência:** Otimizar controle e operação")
    
    st.markdown("### 💰 Recomendações Econômicas")
    
    if vpl > 0:
        st.success("✅ **Viabilidade confirmada:** Prosseguir com desenvolvimento")
    else:
        st.error("❌ **Projeto inviável:** Reavaliar condições econômicas")
    
    if payback < 10:
        st.success("✅ **Retorno rápido:** Investimento atrativo")
    elif payback > 15:
        st.warning("⚠️ **Retorno lento:** Avaliar incentivos e financiamentos")
    
    st.markdown("### 📋 Próximos Passos Recomendados")
    
    if cf > 0.25 and vpl > 0:
        st.markdown("""
        1. **Desenvolvimento detalhado:** Elaborar projeto executivo
        2. **Estudos ambientais:** Avaliar impactos e licenciamento
        3. **Análise de micrositing:** Otimizar posicionamento das turbinas
        4. **Modelagem financeira:** Refinar análise econômica
        5. **Consulta aos stakeholders:** Engajar comunidade e investidores
        """)
    elif cf > 0.15:
        st.markdown("""
        1. **Campanhas de medição:** Confirmar recurso com dados locais
        2. **Análise de sensibilidade:** Testar diferentes cenários
        3. **Estudo de alternativas:** Avaliar outras tecnologias
        4. **Busca por incentivos:** Investigar subsídios disponíveis
        """)
    else:
        st.markdown("""
        1. **Reavaliação do local:** Considerar localizações alternativas
        2. **Tecnologias alternativas:** Avaliar solar ou híbrido
        3. **Análise de dados históricos:** Verificar variabilidade anual
        4. **Consultoria especializada:** Buscar segunda opinião técnica
        """)
