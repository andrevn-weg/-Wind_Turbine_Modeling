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

st.set_page_config(
    page_title="Simulador de Turbina Eólica",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌪️"
)

# Import CSS loader
from utils.css_loader import load_css

# Load centralized CSS
css_path = Path(__file__).parent / "src" / "web" / "static" / "styles.css"
load_css(str(css_path))

# Configuração das páginas
pages = {
    "🏠 Principal": [
        st.Page(page="src/web/pages/0_home.py", title="Home", icon="🍃"),
    ],
    "📊 Localidades": [
        st.Page(page="src/web/pages/1_cadastro_localidade.py", title="Cadastro de Localidade", icon="📍"),
        st.Page(page="src/web/pages/2_listar_localidades.py", title="Listar Localidades", icon="📋"),
    ],
    "🌤️ Dados Climáticos": [
        st.Page(page="src/web/pages/3_cadastro_dados_climaticos.py", title="Cadastro de Dados Climáticos", icon="🌦️"),
        st.Page(page="src/web/pages/6_comparacao_fontes.py", title="Comparação de Fontes", icon="🔍"),
    ],
    
}

# Navegação
pg = st.navigation(pages=pages, expanded=True)
pg.run()
