import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import ControlType, ControlTypeRepository


def read_control_type():
    """Interface para visualização de tipos de controle"""
    st.subheader("📋 Visualizar Tipos de Controle")
    
    try:
        repo = ControlTypeRepository()
        control_types = repo.listar_todos()
        
        if not control_types:
            st.info("ℹ️ Nenhum tipo cadastrado.")
            return
        
        for control_type in control_types:
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px;">
                <h4>🎛️ {control_type.type}</h4>
                <p><strong>ID:</strong> {control_type.id}</p>
                <p><strong>Descrição:</strong> {control_type.description or 'Não informada'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
