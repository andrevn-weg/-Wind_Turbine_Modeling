import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import GeneratorType, GeneratorTypeRepository


def create_generator_type():
    """
    Interface para cadastro de tipos de gerador
    """
    st.subheader("🔌 Cadastro de Tipo de Gerador")
    
    with st.form("form_generator_type"):
        st.markdown("### Dados do Tipo de Gerador")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            type_name = st.text_input("Tipo *", placeholder="Ex: PMSG, DFIG, Synchronous")
        
        with col2:
            description = st.text_area("Descrição", placeholder="Descrição do tipo de gerador")
        
        submitted = st.form_submit_button("💾 Cadastrar Tipo", type="primary")
        
        if submitted and type_name.strip():
            try:
                generator_type = GeneratorType(
                    type=type_name.strip(),
                    description=description.strip() if description.strip() else None
                )
                
                repo = GeneratorTypeRepository()
                repo.criar_tabela()
                type_id = repo.salvar(generator_type)
                
                st.success(f"✅ Tipo de gerador cadastrado! ID: {type_id}")
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
