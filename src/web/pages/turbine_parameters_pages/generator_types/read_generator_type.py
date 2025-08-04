import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import GeneratorType, GeneratorTypeRepository


def read_generator_type():
    """
    Interface para visualização de tipos de gerador
    """
    st.subheader("📋 Visualizar Tipos de Gerador")
    
    try:
        repo = GeneratorTypeRepository()
        generator_types = repo.listar_todos()
        
        if not generator_types:
            st.info("ℹ️ Nenhum tipo de gerador cadastrado.")
            return
        
        for generator_type in generator_types:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px;">
                    <h4>🔌 {generator_type.type}</h4>
                    <p><strong>ID:</strong> {generator_type.id}</p>
                    <p><strong>Descrição:</strong> {generator_type.description or 'Não informada'}</p>
                </div>
                """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
