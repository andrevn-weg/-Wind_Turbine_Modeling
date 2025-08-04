import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import AerogeneratorRepository


def delete_aerogenerator():
    """Interface para exclusão de aerogeradores"""
    st.subheader("🗑️ Excluir Aerogerador")
    st.warning("⚠️ **ATENÇÃO: Operação irreversível!**")
    
    try:
        repo = AerogeneratorRepository()
        aerogenerators = repo.listar_todos()
        
        if not aerogenerators:
            st.info("ℹ️ Nenhum aerogerador cadastrado.")
            return
        
        opcoes = {f"{a.model_code} - {a.model}": a.id for a in aerogenerators}
        selecionado = st.selectbox("Escolha o aerogerador:", list(opcoes.keys()))
        
        if selecionado:
            aerogenerator_id = opcoes[selecionado]
            aerogenerator = repo.buscar_por_id(aerogenerator_id)
            
            st.error(f"Aerogerador: **{aerogenerator.model_code}** - {aerogenerator.model}")
            
            if st.checkbox(f"Confirmo excluir **{aerogenerator.model_code}**"):
                if st.button("🗑️ EXCLUIR", type="primary"):
                    if repo.excluir(aerogenerator_id):
                        st.success("✅ Excluído!")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
