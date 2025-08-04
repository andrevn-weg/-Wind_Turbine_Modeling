import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import TurbineType, TurbineTypeRepository


def read_turbine_type():
    """
    Interface para visualização de tipos de turbina cadastrados
    """
    st.subheader("📋 Visualizar Tipos de Turbina")
    
    try:
        repo = TurbineTypeRepository()
        turbine_types = repo.listar_todos()
        
        if not turbine_types:
            st.info("ℹ️ Nenhum tipo de turbina cadastrado ainda.")
            st.markdown("👆 Use a aba **Cadastrar** para adicionar tipos de turbina.")
            return
        
        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Tipos", len(turbine_types))
        with col2:
            com_descricao = len([t for t in turbine_types if t.description])
            st.metric("Com Descrição", com_descricao)
        with col3:
            st.metric("Sem Descrição", len(turbine_types) - com_descricao)
        
        st.markdown("---")
        
        # Filtro de busca
        st.markdown("### 🔍 Filtros")
        busca_tipo = st.text_input(
            "Buscar tipo:",
            placeholder="Digite parte do nome do tipo"
        )
        
        # Aplicar filtro
        turbine_types_filtrados = turbine_types
        if busca_tipo:
            turbine_types_filtrados = [
                t for t in turbine_types_filtrados 
                if busca_tipo.lower() in t.type.lower()
            ]
        
        st.markdown(f"### 📊 Resultados ({len(turbine_types_filtrados)} tipos)")
        
        if not turbine_types_filtrados:
            st.warning("⚠️ Nenhum tipo encontrado com o filtro aplicado.")
            return
        
        # Visualização em cards
        for turbine_type in turbine_types_filtrados:
            with st.container():
                st.markdown(f"""
                <div style="
                    border: 1px solid #ddd; 
                    border-radius: 10px; 
                    padding: 15px; 
                    margin: 10px 0;
                    background-color: #f9f9f9;
                ">
                    <h4 style="margin: 0 0 10px 0; color: #0066cc;">⚙️ {turbine_type.type}</h4>
                    <p style="margin: 5px 0;"><strong>ID:</strong> {turbine_type.id}</p>
                    <p style="margin: 5px 0;"><strong>Descrição:</strong> {turbine_type.description or 'Não informada'}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Tabela resumo
        st.markdown("---")
        st.markdown("### 📋 Tabela Resumo")
        
        df_types = pd.DataFrame([
            {
                "ID": t.id,
                "Tipo": t.type,
                "Descrição": t.description or "Não informada",
                "Tem Descrição": "Sim" if t.description else "Não"
            }
            for t in turbine_types_filtrados
        ])
        
        st.dataframe(
            df_types,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Tipo": st.column_config.TextColumn("Tipo", width="medium"), 
                "Descrição": st.column_config.TextColumn("Descrição", width="large"),
                "Tem Descrição": st.column_config.TextColumn("Tem Descrição", width="small")
            }
        )
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar tipos de turbina: {str(e)}")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())
