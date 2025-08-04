"""
Página de Análise de Perfil Vertical do Vento

Esta página implementa a análise do perfil vertical de vento usando:
- Lei de Potência
- Lei Logarítmica  
- Análise comparativa entre os modelos
- Correção de velocidade para altura da turbina
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from analysis_tools.wind_profile import WindProfileCalculator
from analysis_tools.visualization import AnalysisVisualizer
from meteorological.meteorological_data.repository import MeteorologicalDataRepository


def render_wind_profile_tab():
    """Renderiza a aba de análise de perfil de vento."""
    
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">📏 Análise do Perfil Vertical do Vento</h4>
        <p>Análise das leis de extrapolação vertical: Lei de Potência e Lei Logarítmica</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar se parâmetros iniciais foram configurados
    if not st.session_state.analysis_state.get('cidade_selected'):
        st.warning("⚠️ Configure os parâmetros iniciais primeiro.")
        return
    
    cidade_selected = st.session_state.analysis_state['cidade_selected']
    altura_turbina = st.session_state.analysis_state['altura_turbina']
    
    # Obter dados meteorológicos da cidade
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
        
        if not dados_meteorologicos:
            st.error("❌ Nenhum dado meteorológico encontrado para esta cidade.")
            return
        
    except Exception as e:
        st.error(f"Erro ao carregar dados meteorológicos: {str(e)}")
        return
    
    # Calcular estatísticas dos dados de vento
    velocidades_vento = [d.velocidade_vento for d in dados_meteorologicos if d.velocidade_vento]
    alturas_medicao = list(set([d.altura_captura for d in dados_meteorologicos if d.altura_captura]))
    
    if not velocidades_vento:
        st.error("❌ Nenhum dado de velocidade de vento encontrado.")
        return
    
    velocidade_media = np.mean(velocidades_vento)
    velocidade_mediana = np.median(velocidades_vento)
    velocidade_max = np.max(velocidades_vento)
    
    # Seção 1: Resumo dos Dados Meteorológicos
    st.markdown("### 📊 Dados Meteorológicos Disponíveis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Registros", f"{len(velocidades_vento)}")
    
    with col2:
        st.metric("Velocidade Média", f"{velocidade_media:.2f} m/s")
    
    with col3:
        st.metric("Velocidade Máxima", f"{velocidade_max:.2f} m/s")
    
    with col4:
        st.metric("Alturas Medição", f"{len(alturas_medicao)}")
    
    # Seção 2: Configuração dos Parâmetros de Análise
    st.markdown("---")
    st.markdown("### ⚙️ Configuração dos Parâmetros de Análise")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Velocidade de referência
        opcoes_velocidade = {
            f"Velocidade Média ({velocidade_media:.2f} m/s)": velocidade_media,
            f"Velocidade Mediana ({velocidade_mediana:.2f} m/s)": velocidade_mediana,
            "Velocidade Personalizada": None
        }
        
        velocidade_opcao = st.selectbox(
            "Velocidade de Referência:",
            list(opcoes_velocidade.keys()),
            help="Velocidade de vento na altura de referência"
        )
        
        if opcoes_velocidade[velocidade_opcao] is None:
            v_ref = st.number_input(
                "Velocidade Personalizada (m/s):",
                min_value=0.1,
                max_value=50.0,
                value=velocidade_media,
                step=0.1
            )
        else:
            v_ref = opcoes_velocidade[velocidade_opcao]
    
    with col2:
        # Altura de referência
        if alturas_medicao:
            altura_ref_sugerida = min(alturas_medicao)
            h_ref = st.selectbox(
                "Altura de Referência (m):",
                sorted(alturas_medicao),
                index=sorted(alturas_medicao).index(altura_ref_sugerida),
                help="Altura onde a velocidade foi medida"
            )
        else:
            h_ref = st.number_input(
                "Altura de Referência (m):",
                min_value=1.0,
                max_value=200.0,
                value=10.0,
                step=1.0
            )
    
    with col3:
        # Altura máxima de análise
        altura_max_sugerida = max(altura_turbina + 50, 100)
        h_max = st.number_input(
            "Altura Máxima Análise (m):",
            min_value=h_ref + 10,
            max_value=300.0,
            value=altura_max_sugerida,
            step=10.0,
            help="Altura máxima para extrapolação"
        )
    
    # Seção 3: Parâmetros dos Modelos
    st.markdown("---")
    st.markdown("### 🔧 Parâmetros dos Modelos de Extrapolação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Lei de Potência**")
        
        # Seletor de tipo de terreno para Lei de Potência
        try:
            calculator = WindProfileCalculator()
            tipos_terreno_info = calculator.get_terrain_types_info()
            
            if tipos_terreno_info.empty:
                st.error("❌ Nenhum tipo de terreno encontrado.")
                return
            
            terreno_opcoes = {}
            for _, row in tipos_terreno_info.iterrows():
                label = f"{row['Tipo de Terreno']} (n = {row['Coeficiente n']})"
                terreno_opcoes[label] = {
                    'key': row['Chave'],
                    'n': row['Coeficiente n'],
                    'z0': row['Rugosidade z0 (m)']
                }
            
            if not terreno_opcoes:
                st.error("❌ Erro ao processar tipos de terreno.")
                st.info(f"Debug: tipos_terreno_info = {tipos_terreno_info}")
                return
            
            opcoes_lista = list(terreno_opcoes.keys())
            indice_padrao = 4 if len(opcoes_lista) > 4 else 0
            
            terreno_selecionado = st.selectbox(
                "Tipo de Terreno:",
                opcoes_lista,
                index=indice_padrao,
                help="Tipo de terreno que melhor descreve a região",
                key="terrain_selector"
            )
            
            if not terreno_selecionado or terreno_selecionado not in terreno_opcoes:
                st.error("❌ Erro na seleção do tipo de terreno.")
                st.info(f"Debug: terreno_selecionado = {terreno_selecionado}")
                st.info(f"Debug: opcoes_lista = {opcoes_lista}")
                return
                
            n_coeff = terreno_opcoes[terreno_selecionado]['n']
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar tipos de terreno: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return
        
        # Permitir ajuste manual
        n_manual = st.checkbox("Ajustar coeficiente manualmente")
        if n_manual:
            n_coeff = st.number_input(
                "Coeficiente n:",
                min_value=0.05,
                max_value=0.50,
                value=n_coeff,
                step=0.01
            )
    
    with col2:
        st.markdown("**Lei Logarítmica**")
        
        if terreno_selecionado and terreno_selecionado in terreno_opcoes:
            z0 = terreno_opcoes[terreno_selecionado]['z0']
        else:
            z0 = 0.1  # valor padrão
        
        # Permitir ajuste manual
        z0_manual = st.checkbox("Ajustar rugosidade manualmente")
        if z0_manual:
            z0 = st.number_input(
                "Comprimento de Rugosidade z₀ (m):",
                min_value=0.00001,
                max_value=5.0,
                value=z0,
                step=0.001,
                format="%.5f"
            )
        
        st.write(f"**z₀ = {z0:.5f} m**")
    
    # Botão para executar análise
    st.markdown("---")
    
    if st.button("🔬 Executar Análise do Perfil de Vento", type="primary", use_container_width=True):
        
        with st.spinner("Calculando perfil de vento..."):
            try:
                # Executar cálculos
                profile = calculator.calculate_profile(
                    v_ref=v_ref,
                    h_ref=h_ref,
                    h_max=h_max,
                    n=n_coeff,
                    z0=z0,
                    step=0.5
                )
                
                # Pontos destacados
                highlighted = calculator.get_highlighted_points(profile, interval=10.0)
                
                # Correção para altura da turbina
                corrected_speeds = calculator.correct_wind_speed_to_turbine_height(
                    measured_speed=v_ref,
                    measured_height=h_ref,
                    turbine_height=altura_turbina,
                    terrain_type=terreno_opcoes[terreno_selecionado]['key']
                )
                
                # Salvar resultados no session state
                st.session_state.analysis_state['wind_profile_data'] = {
                    'profile': profile,
                    'highlighted': highlighted,
                    'corrected_speeds': corrected_speeds,
                    'parameters': {
                        'v_ref': v_ref,
                        'h_ref': h_ref,
                        'h_max': h_max,
                        'n_coeff': n_coeff,
                        'z0': z0,
                        'terrain_type': terreno_selecionado
                    }
                }
                
                st.success("✅ Análise do perfil de vento concluída!")
                
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")
                return
    
    # Exibir resultados se disponíveis
    wind_profile_data = st.session_state.analysis_state.get('wind_profile_data')
    
    if wind_profile_data:
        profile = wind_profile_data['profile']
        highlighted = wind_profile_data['highlighted']
        corrected_speeds = wind_profile_data['corrected_speeds']
        parameters = wind_profile_data['parameters']
        
        st.markdown("---")
        st.markdown("### 📈 Resultados da Análise")
        
        # Gráfico principal
        visualizer = AnalysisVisualizer()
        fig_profile = visualizer.plot_wind_profile(
            profile=profile,
            highlighted_points=highlighted,
            show_intersection=True,
            height=600
        )
        
        st.plotly_chart(fig_profile, use_container_width=True)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Intersecção",
                f"{profile.intersection_height:.1f} m",
                f"{profile.intersection_speed:.2f} m/s"
            )
        
        with col2:
            velocidade_turbina_lp = corrected_speeds['power_law_speed']
            st.metric(
                "Vento no Hub (LP)",
                f"{velocidade_turbina_lp:.2f} m/s",
                f"+{((velocidade_turbina_lp/v_ref - 1) * 100):.1f}%"
            )
        
        with col3:
            velocidade_turbina_ll = corrected_speeds['logarithmic_speed']
            st.metric(
                "Vento no Hub (LL)",
                f"{velocidade_turbina_ll:.2f} m/s",
                f"+{((velocidade_turbina_ll/v_ref - 1) * 100):.1f}%"
            )
        
        with col4:
            diferenca = corrected_speeds['difference']
            st.metric(
                "Diferença",
                f"{diferenca:.3f} m/s",
                f"{(diferenca/velocidade_turbina_lp * 100):.1f}%"
            )
        
        # Tabela de análise
        st.markdown("### 📊 Tabela de Análise")
        
        df_analysis = calculator.generate_analysis_table(profile, interval=10.0)
        
        # Destacar linha correspondente à altura da turbina
        turbine_height_row = df_analysis[
            np.abs(df_analysis['Altura (m)'] - altura_turbina) == 
            np.abs(df_analysis['Altura (m)'] - altura_turbina).min()
        ]
        
        if not turbine_height_row.empty:
            st.markdown(f"**🎯 Valores na altura da turbina ({altura_turbina} m):**")
            st.dataframe(turbine_height_row, use_container_width=True)
            st.markdown("---")
        
        st.dataframe(df_analysis, use_container_width=True)
        
        # Informações técnicas
        with st.expander("🔧 Detalhes Técnicos da Análise"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Parâmetros Utilizados:**
                - Velocidade de referência: {parameters['v_ref']:.2f} m/s
                - Altura de referência: {parameters['h_ref']:.0f} m
                - Coeficiente de potência (n): {parameters['n_coeff']:.3f}
                - Comprimento de rugosidade (z₀): {parameters['z0']:.5f} m
                """)
            
            with col2:
                st.markdown(f"""
                **Resultados na Altura da Turbina ({altura_turbina} m):**
                - Lei de Potência: {velocidade_turbina_lp:.2f} m/s
                - Lei Logarítmica: {velocidade_turbina_ll:.2f} m/s
                - Ganho médio: {((velocidade_turbina_lp + velocidade_turbina_ll)/(2*v_ref) - 1)*100:.1f}%
                """)
        
        # Recomendações
        st.markdown("### 💡 Recomendações")
        
        if diferenca < 0.5:
            st.success("✅ **Excelente concordância** entre os modelos. Ambos podem ser usados com confiança.")
        elif diferenca < 1.0:
            st.info("ℹ️ **Boa concordância** entre os modelos. Pequenas diferenças são esperadas.")
        else:
            st.warning("⚠️ **Diferença significativa** entre os modelos. Considere validar com dados locais.")
        
        # Análise do ganho de velocidade
        ganho_medio = ((velocidade_turbina_lp + velocidade_turbina_ll)/(2*v_ref) - 1) * 100
        
        if ganho_medio > 30:
            st.success(f"✅ **Excelente ganho** de velocidade ({ganho_medio:.1f}%) com a altura.")
        elif ganho_medio > 15:
            st.info(f"ℹ️ **Bom ganho** de velocidade ({ganho_medio:.1f}%) com a altura.")
        else:
            st.warning(f"⚠️ **Ganho moderado** de velocidade ({ganho_medio:.1f}%) com a altura.")
