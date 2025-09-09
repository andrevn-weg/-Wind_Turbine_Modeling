"""
Página de Simulação de Turbina Eólica

Esta página implementa a simulação completa de turbinas eólicas:
- Configuração de parâmetros da turbina
- Simulação de performance e potência
- Análise temporal e estatística
- Relatórios de eficiência
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from analysis_tools.turbine_performance import TurbinePerformanceCalculator
from analysis_tools.visualization import AnalysisVisualizer
from analysis_tools.wind_components import WindComponentsSimulator
from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from turbine_parameters.aerogenerators.repository import AerogeneratorRepository
from turbine_parameters.manufacturers.repository import ManufacturerRepository


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


def render_turbine_simulation_tab():
    """Renderiza a aba de simulação de turbina."""
    
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">⚡ Simulação de Turbina Eólica</h4>
        <p>Simulação completa de performance e eficiência da turbina</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar se dados anteriores estão disponíveis
    if not st.session_state.analysis_state.get('cidade_selected'):
        st.warning("⚠️ Configure os parâmetros iniciais primeiro.")
        return
    
    if not st.session_state.analysis_state.get('wind_components_data'):
        st.warning("⚠️ Execute a análise de componentes do vento primeiro.")
        return
        
    cidade_selected = st.session_state.analysis_state['cidade_selected']
    cidade_nome = safe_get_city_name(cidade_selected)
    wind_components_data = st.session_state.analysis_state['wind_components_data']
    components = wind_components_data['components']
    
    # Seção 1: Configuração da Turbina
    st.markdown("### ⚙️ Configuração da Turbina")
    
    try:
        # Conectar ao banco de dados para obter turbinas reais
        aerogenerator_repo = AerogeneratorRepository()
        manufacturer_repo = ManufacturerRepository()
        
        # Obter todos os aerogeradores
        aerogeneradores = aerogenerator_repo.listar_todos()
        fabricantes = manufacturer_repo.listar_todos()
        
        if not aerogeneradores:
            st.error("❌ Nenhuma turbina encontrada no banco de dados.")
            return
        
        # Criar mapeamento de fabricantes
        fabricante_map = {fab.id: fab.name for fab in fabricantes}
        
        # Criar opções de seleção
        opcoes_turbinas = []
        turbina_map = {}
        
        for aerog in aerogeneradores:
            fabricante_nome = fabricante_map.get(aerog.manufacturer_id, "Desconhecido")
            nome_completo = f"{fabricante_nome} - {aerog.model} ({aerog.rated_power_kw}kW)"
            opcoes_turbinas.append(nome_completo)
            turbina_map[nome_completo] = aerog
            
        col1, col2, col3 = st.columns(3)
        
        with col1:
            turbine_selected = st.selectbox(
                "Modelo da Turbina:",
                opcoes_turbinas,
                help="Selecione uma turbina do banco de dados"
            )
            
            # Obter turbina selecionada
            turbina_obj = turbina_map[turbine_selected]
            
            # Validar e ajustar o valor do diâmetro do rotor
            rotor_value = float(turbina_obj.rotor_diameter_m)
            if rotor_value < 30.0:
                # Se o valor do banco for muito pequeno, usar um valor padrão
                rotor_value = max(rotor_value, 50.0)  # Mínimo seguro para turbinas comerciais
                st.warning(f"⚠️ Diâmetro do rotor da turbina ({turbina_obj.rotor_diameter_m}m) ajustado para {rotor_value}m")
            
            rotor_diameter = st.number_input(
                "Diâmetro do Rotor (m):",
                min_value=15.0,  # Reduzido para acomodar turbinas menores
                max_value=200.0,
                value=rotor_value,
                step=5.0,
                help="Diâmetro do rotor da turbina selecionada"
            )
        
        with col2:
            # Validar e ajustar o valor da potência nominal
            power_value = int(turbina_obj.rated_power_kw)
            if power_value < 500:
                power_value = 500
                st.warning(f"⚠️ Potência da turbina ({turbina_obj.rated_power_kw}kW) ajustada para {power_value}kW")
            
            rated_power = st.number_input(
                "Potência Nominal (kW):",
                min_value=100,  # Reduzido para acomodar turbinas menores
                max_value=10000,
                value=power_value,
                step=100,
                help="Potência nominal da turbina selecionada"
            )
            
            # Validar e ajustar o valor da altura do hub
            hub_value = float(turbina_obj.hub_height_m)
            if hub_value < 40.0:
                hub_value = max(hub_value, 30.0)  # Mínimo para turbinas menores
                st.warning(f"⚠️ Altura do hub da turbina ({turbina_obj.hub_height_m}m) ajustada para {hub_value}m")
            
            hub_height = st.number_input(
                "Altura do Hub (m):",
                min_value=20.0,  # Reduzido para acomodar turbinas menores
                max_value=150.0,
                value=hub_value,
                step=5.0,
                help="Altura do hub da turbina selecionada"
            )
        
        with col3:
            # Validar e ajustar velocidade de partida
            cut_in_value = float(turbina_obj.cut_in_speed)
            if cut_in_value < 2.0 or cut_in_value > 5.0:
                cut_in_value = max(min(cut_in_value, 5.0), 2.0)
                st.warning(f"⚠️ Velocidade de partida ({turbina_obj.cut_in_speed}m/s) ajustada para {cut_in_value}m/s")
            
            cut_in_speed = st.number_input(
                "Velocidade de Partida (m/s):",
                min_value=1.0,  # Mais flexível
                max_value=8.0,   # Mais flexível
                value=cut_in_value,
                step=0.1,
                help="Velocidade mínima para operação"
            )
            
            # Validar e ajustar velocidade de parada
            cut_out_value = float(turbina_obj.cut_out_speed)
            if cut_out_value < 20.0:
                cut_out_value = max(cut_out_value, 15.0)
                st.warning(f"⚠️ Velocidade de parada ({turbina_obj.cut_out_speed}m/s) ajustada para {cut_out_value}m/s")
            
            cut_out_speed = st.number_input(
                "Velocidade de Parada (m/s):",
                min_value=15.0,  # Mais flexível
                max_value=35.0,  # Mais flexível
                value=cut_out_value,
                step=0.5,
                help="Velocidade máxima para operação"
            )
            
            # Validar e ajustar velocidade nominal
            rated_wind_value = float(turbina_obj.rated_wind_speed) if turbina_obj.rated_wind_speed else 12.0
            if rated_wind_value < 10.0 or rated_wind_value > 16.0:
                rated_wind_value = max(min(rated_wind_value, 16.0), 10.0)
                if turbina_obj.rated_wind_speed:
                    st.warning(f"⚠️ Velocidade nominal ({turbina_obj.rated_wind_speed}m/s) ajustada para {rated_wind_value}m/s")
            
            rated_speed = st.number_input(
                "Velocidade Nominal (m/s):",
                min_value=8.0,   # Mais flexível
                max_value=18.0,  # Mais flexível
                value=rated_wind_value,
                step=0.5,
                help="Velocidade para potência nominal"
            )
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados de turbinas: {str(e)}")
        st.warning("⚠️ Usando configuração manual como fallback")
        
        # Fallback para configuração manual com limites flexíveis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            turbine_selected = "Manual"
            rotor_diameter = st.number_input(
                "Diâmetro do Rotor (m):", 
                min_value=15.0, 
                max_value=200.0, 
                value=80.0, 
                step=5.0
            )
        
        with col2:
            rated_power = st.number_input(
                "Potência Nominal (kW):", 
                min_value=100, 
                max_value=10000, 
                value=2000, 
                step=100
            )
            hub_height = st.number_input(
                "Altura do Hub (m):", 
                min_value=20.0, 
                max_value=150.0, 
                value=80.0, 
                step=5.0
            )
        
        with col3:
            cut_in_speed = st.number_input(
                "Velocidade de Partida (m/s):", 
                min_value=1.0, 
                max_value=8.0, 
                value=3.0, 
                step=0.1
            )
            cut_out_speed = st.number_input(
                "Velocidade de Parada (m/s):", 
                min_value=15.0, 
                max_value=35.0, 
                value=25.0, 
                step=0.5
            )
            rated_speed = st.number_input(
                "Velocidade Nominal (m/s):", 
                min_value=8.0, 
                max_value=18.0, 
                value=12.0, 
                step=0.5
            )
    
    # Seção 2: Parâmetros de Análise
    st.markdown("---")
    st.markdown("### 🔧 Parâmetros de Análise")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_analise = st.selectbox(
            "Tipo de Análise:",
            ["estatistica", "temporal", "completa"],
            index=2,
            help="Estatística: apenas curva de potência\nTemporal: simulação temporal\nCompleta: ambos"
        )
        
    with col2:
        cp_model = st.selectbox(
            "Modelo de Cp:",
            ["heier", "default"],
            help="Modelo matemático para coeficiente de potência"
        )
        
    with col3:
        beta_angle = st.slider(
            "Ângulo de Pitch β (°):",
            min_value=0.0,
            max_value=15.0,
            value=0.0,
            step=0.5,
            help="Ângulo de controle das pás"
        )
    
    # Botão de simulação
    st.markdown("---")
    
    if st.button("🚀 Executar Simulação da Turbina", type="primary", use_container_width=True):
        
        with st.spinner("Executando simulação da turbina..."):
            try:
                calculator = TurbinePerformanceCalculator()
                
                # Especificações da turbina
                turbine_specs = {
                    'model': turbine_selected,
                    'rotor_diameter': rotor_diameter,
                    'rated_power': rated_power,
                    'hub_height': hub_height,
                    'cut_in_speed': cut_in_speed,
                    'cut_out_speed': cut_out_speed,
                    'rated_speed': rated_speed
                }
                
                # Parâmetros de análise
                analysis_params = {
                    'cp_model': cp_model,
                    'beta': beta_angle,
                    'analysis_type': tipo_analise
                }
                
                # Executar simulação temporal
                if tipo_analise in ['temporal', 'completa']:
                    performance_data = calculator.simulate_temporal_performance(
                        turbine_specs=turbine_specs,
                        wind_data=components.air_flow,
                        time_vector=components.time,
                        beta=analysis_params.get('beta', 0.0),
                        model=analysis_params.get('cp_model', 'heier')
                    )
                else:
                    performance_data = None
                
                # Calcular curva de potência
                power_curve_performance = calculator.generate_power_curve(
                    turbine_specs=turbine_specs,
                    beta=analysis_params.get('beta', 0.0)
                )
                
                # Análise de coeficiente de potência
                if tipo_analise in ['estatistica', 'completa']:
                    cp_analysis = calculator.analyze_performance(power_curve_performance)
                else:
                    cp_analysis = None
                
                # Calcular estatísticas operacionais
                operational_stats = calculator.calculate_operational_statistics(
                    performance_data if tipo_analise in ['temporal', 'completa'] else None,
                    power_curve_performance,
                    components.air_flow
                )
                
                # Salvar resultados
                st.session_state.analysis_state['turbine_simulation_data'] = {
                    'performance_data': performance_data if tipo_analise in ['temporal', 'completa'] else None,
                    'power_curve': power_curve_performance,
                    'cp_analysis': cp_analysis if tipo_analise in ['estatistica', 'completa'] else None,
                    'operational_stats': operational_stats,
                    'turbine_specs': turbine_specs,
                    'analysis_params': analysis_params,
                    'tipo_analise': tipo_analise
                }
                
                st.success("✅ Simulação da turbina concluída!")
                
            except Exception as e:
                st.error(f"❌ Erro na simulação: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                return
    
    # Exibir resultados se disponíveis
    simulation_data = st.session_state.analysis_state.get('turbine_simulation_data')
    
    if simulation_data:
        performance_data = simulation_data['performance_data']
        power_curve = simulation_data['power_curve']
        cp_analysis = simulation_data['cp_analysis']
        operational_stats = simulation_data['operational_stats']
        turbine_specs = simulation_data['turbine_specs']
        
        st.markdown("---")
        st.markdown("### 📊 Resultados da Simulação")
        
        # Visualizações principais
        visualizer = AnalysisVisualizer()
        
        # 1. Curva de Potência
        st.markdown("#### ⚡ Curva de Potência da Turbina")
        
        fig_power = visualizer.plot_turbine_power_curve(
            performance=power_curve,
            height=600
        )
        st.plotly_chart(fig_power, use_container_width=True)
        
        # 2. Análise do Coeficiente de Potência (se disponível)
        if cp_analysis:
            st.markdown("#### 🔄 Análise do Coeficiente de Potência (Cp)")
            
            fig_cp = visualizer.plot_cp_curve(
                performance=power_curve,
                height=600
            )
            st.plotly_chart(fig_cp, use_container_width=True)
        
        # 3. Performance Temporal (se disponível)
        if performance_data:
            st.markdown("#### ⏱️ Performance Temporal")
            
            fig_temporal = visualizer.plot_temporal_performance(
                performance_data=performance_data,
                wind_data=components.air_flow,
                height=800
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Métricas principais
        st.markdown("### 📈 Métricas de Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Potência Média",
                f"{operational_stats.get('operational_stats', {}).get('avg_power', 0):.1f} kW",
                delta=f"{operational_stats.get('efficiency_stats', {}).get('capacity_factor', 0):.1f}% CF"
            )
        
        with col2:
            st.metric(
                "Energia Produzida",
                f"{operational_stats.get('operational_stats', {}).get('energy_production', 0):.0f} kWh",
                delta="Produção contínua"
            )
        
        with col3:
            st.metric(
                "Horas Operação",
                f"{operational_stats.get('operational_stats', {}).get('operating_hours', 0):.0f} h",
                delta=f"{operational_stats.get('operational_stats', {}).get('availability', 0):.1f}% disponível"
            )
        
        with col4:
            st.metric(
                "Eficiência Média",
                f"{operational_stats.get('efficiency_stats', {}).get('avg_cp', 0)*100:.1f}%",
                delta=f"Cp médio: {operational_stats.get('efficiency_stats', {}).get('avg_cp', 0):.3f}"
            )
        
        # Análise detalhada
        st.markdown("### 📋 Análise Detalhada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Estatísticas de Performance**")
            
            # Estatísticas básicas
            stats_data = []
            
            # Dados de potência
            if 'power_stats' in operational_stats:
                power_stats = operational_stats['power_stats']
                for key, value in power_stats.items():
                    stats_data.append({
                        'Métrica': key.replace('_', ' ').title(),
                        'Valor': f"{value:.2f}" if isinstance(value, float) else str(value),
                        'Unidade': 'kW' if 'power' in key else 'm/s' if 'speed' in key else '-'
                    })
            
            # Dados operacionais
            if 'operational_stats' in operational_stats:
                op_stats = operational_stats['operational_stats']
                for key, value in op_stats.items():
                    stats_data.append({
                        'Métrica': key.replace('_', ' ').title(),
                        'Valor': f"{value:.2f}" if isinstance(value, float) else str(value),
                        'Unidade': 'h' if 'hours' in key else '%' if 'availability' in key else 'kW' if 'power' in key else 'kWh' if 'energy' in key else '-'
                    })
            
            if stats_data:
                df_stats = pd.DataFrame(stats_data)
                st.dataframe(df_stats, use_container_width=True)
        
        with col2:
            st.markdown("**Especificações da Turbina**")
            
            specs_data = []
            for key, value in turbine_specs.items():
                specs_data.append({
                    'Parâmetro': key.replace('_', ' ').title(),
                    'Valor': f"{value:.1f}" if isinstance(value, float) else str(value),
                    'Unidade': get_unit_for_param(key)
                })
            
            df_specs = pd.DataFrame(specs_data)
            st.dataframe(df_specs, use_container_width=True)
        
        # Tabelas de dados
        st.markdown("### 📄 Dados Tabulares")
        
        tab1, tab2, tab3 = st.tabs(["💫 Curva de Potência", "⏱️ Performance Temporal", "📊 Estatísticas"])
        
        with tab1:
            if hasattr(power_curve, 'wind_speeds') and hasattr(power_curve, 'power_output'):
                df_power = pd.DataFrame({
                    'Velocidade do Vento (m/s)': power_curve.wind_speeds,
                    'Potência (kW)': power_curve.power_output,
                    'Cp': power_curve.cp_values if hasattr(power_curve, 'cp_values') else np.zeros_like(power_curve.wind_speeds),
                    'Lambda': power_curve.lambda_values if hasattr(power_curve, 'lambda_values') else np.zeros_like(power_curve.wind_speeds)
                })
                st.dataframe(df_power, use_container_width=True)
        
        with tab2:
            if performance_data:
                df_temporal = pd.DataFrame({
                    'Tempo (h)': performance_data['time'],
                    'Velocidade Vento (m/s)': performance_data['wind_speeds'],
                    'Potência (kW)': performance_data['power_output'],
                    'Cp': performance_data['cp_values'],
                    'Status': performance_data['operational_status']
                })
                st.dataframe(df_temporal, use_container_width=True)
        
        with tab3:
            # Resumo geral das estatísticas
            summary_data = []
            
            if performance_data and 'metrics' in performance_data:
                metrics = performance_data['metrics']
                for key, value in metrics.items():
                    summary_data.append({
                        'Métrica': key.replace('_', ' ').title(),
                        'Valor': f"{value:.2f}" if isinstance(value, float) else str(value),
                        'Descrição': get_metric_description(key)
                    })
            
            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary, use_container_width=True)
        
        # Recomendações
        st.markdown("### 💡 Recomendações")
        
        if performance_data and 'metrics' in performance_data:
            capacity_factor = performance_data['metrics'].get('capacity_factor', 0)
            avg_cp = performance_data['metrics'].get('avg_cp', 0)
            
            if capacity_factor > 40:
                st.success(f"✅ **Excelente fator de capacidade** ({capacity_factor:.1f}%). Local muito favorável para geração eólica.")
            elif capacity_factor > 25:
                st.info(f"ℹ️ **Bom fator de capacidade** ({capacity_factor:.1f}%). Local adequado para geração eólica.")
            else:
                st.warning(f"⚠️ **Fator de capacidade baixo** ({capacity_factor:.1f}%). Considere outros locais ou turbinas maiores.")
            
            if avg_cp > 0.4:
                st.success(f"✅ **Excelente eficiência aerodinâmica** (Cp = {avg_cp:.3f}). Turbina bem otimizada.")
            elif avg_cp > 0.3:
                st.info(f"ℹ️ **Boa eficiência aerodinâmica** (Cp = {avg_cp:.3f}). Performance adequada.")
            else:
                st.warning(f"⚠️ **Baixa eficiência aerodinâmica** (Cp = {avg_cp:.3f}). Considere ajustar parâmetros.")


def get_unit_for_param(param_key):
    """Retorna a unidade apropriada para cada parâmetro."""
    units = {
        'rotor_diameter': 'm',
        'rated_power': 'kW',
        'hub_height': 'm',
        'cut_in_speed': 'm/s',
        'cut_out_speed': 'm/s',
        'rated_speed': 'm/s',
        'beta': '°'
    }
    return units.get(param_key, '-')


def get_metric_description(metric_key):
    """Retorna descrição para cada métrica."""
    descriptions = {
        'total_energy': 'Energia total produzida no período',
        'capacity_factor': 'Percentual da potência nominal utilizada',
        'avg_wind_speed': 'Velocidade média do vento',
        'avg_cp': 'Coeficiente de potência médio',
        'max_power': 'Potência máxima atingida',
        'operating_hours': 'Percentual de tempo em operação'
    }
    return descriptions.get(metric_key, 'Métrica de performance')
