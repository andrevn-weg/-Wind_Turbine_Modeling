"""
Página 7: Análise de Turbinas Eólicas

Esta página apresenta o sistema completo de análise de turbinas eólicas, incluindo:
- Parâmetros Iniciais: Seleção de localidade, turbina, altura, período
- Perfil Vertical do Vento: Lei de Potência e Lei Logarítmica
- Componentes do Vento: Vento médio, ondas e turbulência
- Simulação de Turbina: Cálculos de Cp e estimativa de geração
- Resultados e Relatórios: Visualizações e recomendações

Baseado nas diretrizes do guia de desenvolvimento das páginas de análise.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import traceback

def handle_analysis_error(error, context=""):
    """Função para tratar erros específicos da análise."""
    st.error(f"""
    🚨 **Erro na Análise**
    
    **Contexto:** {context}
    **Erro:** {str(error)}
    
    💡 **Soluções:**
    - Verifique se todos os dados necessários estão disponíveis
    - Recarregue a página e tente novamente
    - Verifique as configurações dos parâmetros
    """)
    
    with st.expander("🔧 Detalhes do Erro"):
        st.code(traceback.format_exc(), language="python")

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar páginas de análise com tratamento de erro
try:
    from web.pages.analysis.initial_parameters import render_initial_parameters_tab
    from web.pages.analysis.wind_profile_analysis import render_wind_profile_tab
    from web.pages.analysis.wind_components_analysis import render_wind_components_tab
    from web.pages.analysis.turbine_simulation import render_turbine_simulation_tab
    from web.pages.analysis.results_reports import render_results_reports_tab
except ImportError as e:
    st.error(f"""
    ❌ **Erro de Importação dos Módulos de Análise**
    
    Não foi possível carregar os módulos necessários para análise.
    
    **Erro:** {str(e)}
    
    **Soluções:**
    1. Verifique se todos os arquivos de análise estão presentes
    2. Reinstale as dependências do projeto
    3. Contate o suporte técnico
    """)
    
    # Criar funções vazias como fallback
    def render_initial_parameters_tab():
        st.error("Módulo de parâmetros iniciais não disponível")
    
    def render_wind_profile_tab():
        st.error("Módulo de análise de perfil de vento não disponível")
    
    def render_wind_components_tab():
        st.error("Módulo de componentes do vento não disponível")
    
    def render_turbine_simulation_tab():
        st.error("Módulo de simulação de turbina não disponível")
    
    def render_results_reports_tab():
        st.error("Módulo de resultados e relatórios não disponível")


def main():
    """Função principal da página de análise."""
    
    try:
        # Configurar tema dos gráficos
        try:
            from analysis_tools.visualization import AnalysisVisualizer
            AnalysisVisualizer.configure_plotly_theme()
        except Exception as e:
            st.warning("⚠️ Não foi possível configurar o tema dos gráficos. Usando tema padrão.")
        
        # Header principal
        st.markdown("""
        <div class="page-main-header">
            <h1>🔬 Análise de Turbinas Eólicas</h1>
            <p>Sistema completo de simulação e análise de viabilidade eólica</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar com informações
        st.sidebar.header("📊 Sistema de Análise")
        st.sidebar.info("""
        **Fluxo de Análise:**
        
        1. 📋 **Parâmetros Iniciais** - Definir localidade e turbina
        2. 📏 **Perfil de Vento** - Análise vertical do vento
        3. 🌊 **Componentes** - Simulação de vento real
        4. ⚙️ **Simulação** - Performance da turbina
        5. 📈 **Resultados** - Relatórios e recomendações
        
        **💡 Dica:** Complete cada etapa sequencialmente para melhor análise.
        """)
        
        # Inicializar session state para análise
        if 'analysis_state' not in st.session_state:
            st.session_state.analysis_state = {
                'cidade_selected': None,
                'turbina_selected': None,
                'altura_turbina': 80.0,
                'periodo_analise': None,
                'wind_profile_data': None,
                'wind_components_data': None,
                'turbine_performance_data': None,
                'analysis_complete': False
            }
        
        # Verificar disponibilidade de dados
        try:
            verificar_prerequisites()
        except Exception as e:
            st.sidebar.error(f"Erro ao verificar pré-requisitos: {str(e)}")
        
    except Exception as e:
        handle_analysis_error(e, "Inicialização da Página")
    
    # Interface principal com tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Parâmetros Iniciais",
        "📏 Perfil de Vento", 
        "🌊 Componentes do Vento",
        "⚙️ Simulação de Turbina",
        "📈 Resultados e Relatórios"
    ])
    
    with tab1:
        try:
            render_initial_parameters_tab()
        except Exception as e:
            handle_analysis_error(e, "Parâmetros Iniciais")
    
    with tab2:
        try:
            render_wind_profile_tab()
        except Exception as e:
            handle_analysis_error(e, "Análise do Perfil de Vento")
    
    with tab3:
        try:
            render_wind_components_tab()
        except Exception as e:
            handle_analysis_error(e, "Componentes do Vento")
    
    with tab4:
        try:
            render_turbine_simulation_tab()
        except Exception as e:
            handle_analysis_error(e, "Simulação da Turbina")
    
    with tab5:
        try:
            render_results_reports_tab()
        except Exception as e:
            handle_analysis_error(e, "Resultados e Relatórios")
    
    # Footer com status da análise
    try:
        render_analysis_status_footer()
    except Exception as e:
        st.warning(f"Erro ao carregar status da análise: {str(e)}")


def verificar_prerequisites():
    """Verifica se os pré-requisitos para análise estão atendidos."""
    
    try:
        # Verificar dados meteorológicos
        from meteorological.meteorological_data.repository import MeteorologicalDataRepository
        met_repo = MeteorologicalDataRepository()
        total_dados = len(met_repo.listar_todos())
        
        # Verificar turbinas cadastradas
        from turbine_parameters.aerogenerators.repository import AerogeneratorRepository
        turb_repo = AerogeneratorRepository()
        total_turbinas = turb_repo.contar_total()
        
        # Verificar cidades
        from geographic.cidade.repository import CidadeRepository
        cidade_repo = CidadeRepository()
        total_cidades = cidade_repo.contar_total()
        
        # Mostrar alertas se necessário
        warnings = []
        
        if total_cidades == 0:
            warnings.append("❌ Nenhuma cidade cadastrada")
        
        if total_dados == 0:
            warnings.append("❌ Nenhum dado meteorológico disponível")
        
        if total_turbinas == 0:
            warnings.append("❌ Nenhuma turbina cadastrada")
        
        if warnings:
            st.sidebar.markdown("### ⚠️ Pré-requisitos")
            for warning in warnings:
                st.sidebar.warning(warning)
            
            st.sidebar.markdown("""
            **Para usar o sistema de análise:**
            1. Cadastre pelo menos uma cidade
            2. Colete dados meteorológicos
            3. Cadastre parâmetros de turbinas
            """)
        else:
            st.sidebar.success(f"""
            ✅ **Sistema Pronto**
            - {total_cidades} cidades
            - {total_dados} dados meteorológicos  
            - {total_turbinas} turbinas
            """)
    
    except Exception as e:
        st.sidebar.error(f"Erro ao verificar pré-requisitos: {str(e)}")


def render_analysis_status_footer():
    """Renderiza o footer com status da análise atual."""
    
    st.markdown("---")
    st.markdown("### 📊 Status da Análise Atual")
    
    state = st.session_state.analysis_state
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status = "✅" if state.get('cidade_selected') and state.get('turbina_selected') else "⏸️"
        st.metric("Parâmetros", status)
    
    with col2:
        status = "✅" if state.get('wind_profile_data') else "⏸️"
        st.metric("Perfil Vento", status)
    
    with col3:
        status = "✅" if state.get('wind_components_data') else "⏸️"
        st.metric("Componentes", status)
    
    with col4:
        status = "✅" if state.get('turbine_performance_data') else "⏸️"
        st.metric("Simulação", status)
    
    with col5:
        status = "✅" if state.get('analysis_complete') else "⏸️"
        st.metric("Análise", status)
    
    # Progresso geral
    progress_items = [
        bool(state.get('cidade_selected') and state.get('turbina_selected')),
        bool(state.get('wind_profile_data')),
        bool(state.get('wind_components_data')),
        bool(state.get('turbine_performance_data')),
        bool(state.get('analysis_complete'))
    ]
    
    progress = sum(progress_items) / len(progress_items) if progress_items else 0
    st.progress(progress)
    st.caption(f"Progresso da análise: {progress:.0%}")
    
    # Informações técnicas
    if state.get('cidade_selected') or state.get('turbina_selected'):
        with st.expander("🔧 Detalhes Técnicos da Análise"):
            if state.get('cidade_selected'):
                cidade_info = state['cidade_selected']
                if isinstance(cidade_info, dict) and 'cidade' in cidade_info:
                    cidade_nome = cidade_info['cidade'].nome
                    st.write(f"**🏙️ Cidade:** {cidade_nome}")
                else:
                    st.write(f"**🏙️ Cidade:** {cidade_info}")
            
            if state.get('turbina_selected'):
                turbina_info = state['turbina_selected']
                if hasattr(turbina_info, 'modelo'):
                    st.write(f"**⚙️ Turbina:** {turbina_info.modelo}")
                else:
                    st.write(f"**⚙️ Turbina:** {turbina_info}")
            
            if state.get('altura_turbina'):
                st.write(f"**📏 Altura:** {state['altura_turbina']} m")
            
            if state.get('periodo_analise'):
                periodo = state['periodo_analise']
                if isinstance(periodo, dict):
                    data_inicio = periodo.get('data_inicio', 'N/A')
                    data_fim = periodo.get('data_fim', 'N/A')
                    dias_total = periodo.get('dias_total', 'N/A')
                    st.write(f"**📅 Período:** {data_inicio} a {data_fim} ({dias_total} dias)")
                else:
                    st.write(f"**📅 Período:** {periodo}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"""
        # 🚨 Erro Crítico na Página de Análise
        
        A página de análise encontrou um erro inesperado.
        
        **Erro:** {str(e)}
        
        **Soluções:**
        1. Recarregue a página (F5)
        2. Verifique se todos os dados necessários estão cadastrados
        3. Contate o suporte técnico se o problema persistir
        """)
        
        with st.expander("🔧 Detalhes Técnicos"):
            st.code(traceback.format_exc(), language="python")
        
        # Botões de recuperação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Recarregar Página", type="primary"):
                st.rerun()
        
        with col2:
            if st.button("🏠 Voltar ao Home"):
                st.switch_page("src/web/pages/0_home.py")
