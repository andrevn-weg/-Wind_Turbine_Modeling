import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import ControlType, ControlTypeRepository


def create_control_type():
    """Interface para cadastro de tipos de controle"""
    st.subheader("🎛️ Cadastro de Tipo de Controle")
    
    with st.form("form_control_type"):
        type_name = st.text_input("Tipo *", placeholder="Ex: Pitch, Stall, Active Stall")
        description = st.text_area("Descrição", placeholder="Descrição do tipo de controle")
        
        if st.form_submit_button("💾 Cadastrar", type="primary") and type_name.strip():
            try:
                control_type = ControlType(
                    type=type_name.strip(),
                    description=description.strip() if description.strip() else None
                )
                
                repo = ControlTypeRepository()
                repo.criar_tabela()
                type_id = repo.salvar(control_type)
                st.success(f"✅ Tipo cadastrado! ID: {type_id}")
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
