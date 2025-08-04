import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import ControlType, ControlTypeRepository


def delete_control_type():
    """Interface para exclusão de tipos de controle"""
    st.subheader("🗑️ Excluir Tipo de Controle")
    st.warning("⚠️ **ATENÇÃO: Operação irreversível!**")
    
    try:
        repo = ControlTypeRepository()
        control_types = repo.listar_todos()
        
        if not control_types:
            st.info("ℹ️ Nenhum tipo cadastrado.")
            return
        
        opcoes = {f"{t.type} (ID: {t.id})": t.id for t in control_types}
        selecionado = st.selectbox("Escolha o tipo:", list(opcoes.keys()))
        
        if selecionado:
            type_id = opcoes[selecionado]
            control_type = repo.buscar_por_id(type_id)
            
            st.error(f"Tipo: **{control_type.type}**")
            
            if st.checkbox(f"Confirmo excluir **{control_type.type}**"):
                if st.button("🗑️ EXCLUIR", type="primary"):
                    if repo.excluir(type_id):
                        st.success("✅ Excluído!")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
