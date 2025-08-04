import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import GeneratorType, GeneratorTypeRepository


def delete_generator_type():
    """
    Interface para exclusão de tipos de gerador
    """
    st.subheader("🗑️ Excluir Tipo de Gerador")
    st.warning("⚠️ **ATENÇÃO: Operação irreversível!**")
    
    try:
        repo = GeneratorTypeRepository()
        generator_types = repo.listar_todos()
        
        if not generator_types:
            st.info("ℹ️ Nenhum tipo cadastrado.")
            return
        
        opcoes = {f"{t.type} (ID: {t.id})": t.id for t in generator_types}
        selecionado = st.selectbox("Escolha o tipo:", list(opcoes.keys()))
        
        if selecionado:
            type_id = opcoes[selecionado]
            generator_type = repo.buscar_por_id(type_id)
            
            st.error(f"Tipo: **{generator_type.type}**")
            
            if st.checkbox(f"Confirmo excluir **{generator_type.type}**"):
                if st.button("🗑️ EXCLUIR", type="primary"):
                    if repo.excluir(type_id):
                        st.success("✅ Excluído!")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
