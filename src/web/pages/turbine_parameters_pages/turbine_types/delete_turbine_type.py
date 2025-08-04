import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import TurbineType, TurbineTypeRepository


def delete_turbine_type():
    """
    Interface para exclusão de tipos de turbina
    """
    st.subheader("🗑️ Excluir Tipo de Turbina")
    
    st.warning("⚠️ **ATENÇÃO: Esta operação é irreversível!**")
    
    try:
        repo = TurbineTypeRepository()
        turbine_types = repo.listar_todos()
        
        if not turbine_types:
            st.info("ℹ️ Nenhum tipo cadastrado para excluir.")
            return
        
        # Seleção do tipo para excluir
        opcoes_tipos = {
            f"{t.type} (ID: {t.id})": t.id 
            for t in turbine_types
        }
        
        tipo_selecionado = st.selectbox(
            "Escolha o tipo:",
            options=list(opcoes_tipos.keys())
        )
        
        if tipo_selecionado:
            type_id = opcoes_tipos[tipo_selecionado]
            turbine_type = repo.buscar_por_id(type_id)
            
            st.error(f"Tipo selecionado: **{turbine_type.type}**")
            
            confirmar = st.checkbox(f"Confirmo que desejo excluir o tipo **{turbine_type.type}**")
            
            if confirmar:
                if st.button("🗑️ EXCLUIR DEFINITIVAMENTE", type="primary"):
                    if repo.excluir(type_id):
                        st.success(f"✅ Tipo **{turbine_type.type}** excluído!")
                    else:
                        st.error("❌ Erro ao excluir.")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
