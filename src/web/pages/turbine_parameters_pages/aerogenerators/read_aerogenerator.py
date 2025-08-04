import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import AerogeneratorRepository


def read_aerogenerator():
    """Interface para visualização de aerogeradores"""
    st.subheader("📋 Visualizar Aerogeradores")
    
    try:
        repo = AerogeneratorRepository()
        aerogenerators = repo.buscar_com_detalhes_completos()
        
        if not aerogenerators:
            st.info("ℹ️ Nenhum aerogerador cadastrado.")
            return
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", len(aerogenerators))
        with col2:
            potencia_total = sum([a['rated_power_kw'] for a in aerogenerators])
            st.metric("Potência Total (MW)", f"{potencia_total/1000:.1f}")
        with col3:
            fabricantes = len(set([a['manufacturer_name'] for a in aerogenerators]))
            st.metric("Fabricantes", fabricantes)
        
        # Tabela
        df = pd.DataFrame(aerogenerators)
        df_display = df[['id', 'model_code', 'model', 'manufacturer_name', 'rated_power_kw', 'rotor_diameter_m']].copy()
        df_display.columns = ['ID', 'Código', 'Modelo', 'Fabricante', 'Potência (kW)', 'Diâmetro (m)']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
