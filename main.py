from pathlib import Path
import streamlit as st
import os
import sys
import pandas as pd
from PIL import Image
import importlib

st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Import CSS loader
from utils.css_loader import load_css

# Load centralized CSS
project_root = Path(__file__).parent.parent
css_path = os.path.join(project_root, "static", "styles.css")
load_css(css_path)

pages = {
    "Home" : [
        st.Page(page="pages/0_home.py", title="Home", icon="🍃",)
    ],
    "Pages Lixo" : [
        st.Page(page="pages/cadastro_localidade.py", title="Cadastro de Localidade", icon="📍")
        ]
}

pg = st.navigation(pages=pages, expanded=True)
pg.run()