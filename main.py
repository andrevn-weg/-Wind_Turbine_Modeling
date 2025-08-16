"""
Sistema de Simulação de Turbinas Eólicas
Aplicação principal usando Streamlit
"""

from pathlib import Path
import streamlit as st
import os
import sys

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
# Configuração do Streamlit
st.logo(image="src/images/UFSM-CS_horizontal_cor.png",icon_image="src/images/UFSM-CS_horizontal_cor.png", size="large",link="https://www.ufsm.br/cursos/graduacao/cachoeira-do-sul/engenharia-eletrica")
        
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",

)

# Import CSS loader
from utils.css_loader import load_css

# Load centralized CSS
css_path = Path(__file__).parent / "src" / "web" / "static" / "styles.css"
load_css(str(css_path))

# Configuração das páginas
pages = {
    "": [
        st.Page(page="src/web/pages/0_home.py", title="Home", icon="🍃"),
    ],
    "📊 Localidades": [
        st.Page(page="src/web/pages/1_cadastro_localidade.py", title="Cadastro de Localidade", icon="📍"),
        st.Page(page="src/web/pages/2_listar_localidades.py", title="Listar Localidades", icon="📋"),
    ],
    "🌤️ Dados Climáticos": [
        st.Page(page="src/web/pages/3_meteorological_registration.py", title="Cadastro de Dados Climáticos", icon="🌦️"),
        st.Page(page="src/web/pages/4_meteorological_analysis.py", title="Análises Meteorológicas", icon="📊"),
        # st.Page(page="src/web/pages/6_comparacao_fontes.py", title="Comparação de Fontes", icon="🔍"),
    ],
    "⚙️ Turbinas": [
        st.Page(page="src/web/pages/5_turbine_parameters.py", title="Parâmetros das Turbinas", icon="⚙️"),
        st.Page(page="src/web/pages/6_aerogenerators.py", title="Aerogeradores", icon="🏭"),
    ],
    "🔬 Análise": [
        st.Page(page="src/web/pages/7_analysis.py", title="Análise de Turbinas Eólicas", icon="🔬"),
    ],
    
}

# Navegação
pg = st.navigation(pages=pages, expanded=True)

pg.run()
