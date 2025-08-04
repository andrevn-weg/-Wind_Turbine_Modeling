import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import TurbineType, TurbineTypeRepository


def update_turbine_type():
    """
    Interface para edição de tipos de turbina existentes
    """
    st.subheader("✏️ Editar Tipo de Turbina")
    
    try:
        repo = TurbineTypeRepository()
        turbine_types = repo.listar_todos()
        
        if not turbine_types:
            st.info("ℹ️ Nenhum tipo cadastrado para editar.")
            return
        
        # Seleção do tipo para editar
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
            
            with st.form("form_edit_turbine_type"):
                new_type = st.text_input("Tipo *", value=turbine_type.type)
                new_description = st.text_area("Descrição", value=turbine_type.description or "")
                
                submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
                
                if submitted and new_type.strip():
                    turbine_type.type = new_type.strip()
                    turbine_type.description = new_description.strip() if new_description.strip() else None
                    
                    if repo.atualizar(turbine_type):
                        st.success("✅ Tipo atualizado com sucesso!")
                    else:
                        st.error("❌ Erro ao atualizar.")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
