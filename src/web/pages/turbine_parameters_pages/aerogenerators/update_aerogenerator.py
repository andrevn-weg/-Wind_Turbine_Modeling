import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import AerogeneratorRepository


def update_aerogenerator():
    """Interface para edição de aerogeradores"""
    st.subheader("✏️ Editar Aerogerador")
    st.info("ℹ️ Funcionalidade de edição em desenvolvimento. Use a exclusão e criação de novo registro.")
