import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import GeneratorType, GeneratorTypeRepository


def update_generator_type():
    """
    Interface para edição de tipos de gerador
    """
    st.subheader("✏️ Editar Tipo de Gerador")
    
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
            
            with st.form("form_edit"):
                new_type = st.text_input("Tipo *", value=generator_type.type)
                new_description = st.text_area("Descrição", value=generator_type.description or "")
                
                if st.form_submit_button("💾 Salvar", type="primary"):
                    generator_type.type = new_type.strip()
                    generator_type.description = new_description.strip() if new_description.strip() else None
                    
                    if repo.atualizar(generator_type):
                        st.success("✅ Atualizado!")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
