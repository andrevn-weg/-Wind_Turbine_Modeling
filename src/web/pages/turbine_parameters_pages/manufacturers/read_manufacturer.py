import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import Manufacturer, ManufacturerRepository


def read_manufacturer():
    """
    Interface para visualização de fabricantes cadastrados
    """
    st.subheader("📋 Visualizar Fabricantes")
    
    try:
        repo = ManufacturerRepository()
        manufacturers = repo.listar_todos()
        
        if not manufacturers:
            st.info("ℹ️ Nenhum fabricante cadastrado ainda.")
            st.markdown("👆 Use a aba **Cadastrar** para adicionar o primeiro fabricante.")
            return
        
        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Fabricantes", len(manufacturers))
        with col2:
            paises_unicos = len(set([m.country for m in manufacturers]))
            st.metric("Países Únicos", paises_unicos)
        with col3:
            com_website = len([m for m in manufacturers if m.official_website])
            st.metric("Com Website", com_website)
        
        st.markdown("---")
        
        # Filtros
        st.markdown("### 🔍 Filtros")
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por país
            todos_paises = sorted(list(set([m.country for m in manufacturers])))
            pais_selecionado = st.selectbox(
                "Filtrar por País:",
                options=["Todos"] + todos_paises,
                index=0
            )
        
        with col2:
            # Filtro por busca de nome
            busca_nome = st.text_input(
                "Buscar por Nome:",
                placeholder="Digite parte do nome do fabricante"
            )
        
        # Aplicar filtros
        manufacturers_filtrados = manufacturers
        
        if pais_selecionado != "Todos":
            manufacturers_filtrados = [m for m in manufacturers_filtrados if m.country == pais_selecionado]
        
        if busca_nome:
            manufacturers_filtrados = [
                m for m in manufacturers_filtrados 
                if busca_nome.lower() in m.name.lower()
            ]
        
        st.markdown(f"### 📊 Resultados ({len(manufacturers_filtrados)} fabricantes)")
        
        if not manufacturers_filtrados:
            st.warning("⚠️ Nenhum fabricante encontrado com os filtros aplicados.")
            return
        
        # Escolha do formato de visualização
        formato = st.radio(
            "Formato de Visualização:",
            options=["Cards", "Tabela"],
            horizontal=True
        )
        
        if formato == "Cards":
            # Visualização em cards
            for i in range(0, len(manufacturers_filtrados), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(manufacturers_filtrados):
                        manufacturer = manufacturers_filtrados[i + j]
                        with col:
                            with st.container():
                                st.markdown(f"""
                                <div style="
                                    border: 1px solid #ddd; 
                                    border-radius: 10px; 
                                    padding: 15px; 
                                    margin: 10px 0;
                                    background-color: #f9f9f9;
                                ">
                                    <h4 style="margin: 0 0 10px 0; color: #0066cc;">🏭 {manufacturer.name}</h4>
                                    <p style="margin: 5px 0;"><strong>ID:</strong> {manufacturer.id}</p>
                                    <p style="margin: 5px 0;"><strong>País:</strong> {manufacturer.country}</p>
                                    <p style="margin: 5px 0;"><strong>Criado em:</strong> {manufacturer.created_at.strftime('%d/%m/%Y %H:%M') if manufacturer.created_at else 'N/A'}</p>
                                    {"<p style='margin: 5px 0;'><strong>Website:</strong> <a href='" + manufacturer.official_website + "' target='_blank'>" + manufacturer.official_website + "</a></p>" if manufacturer.official_website else ""}
                                </div>
                                """, unsafe_allow_html=True)
        
        else:
            # Visualização em tabela
            df_manufacturers = pd.DataFrame([
                {
                    "ID": m.id,
                    "Nome": m.name,
                    "País": m.country,
                    "Website": m.official_website or "Não informado",
                    "Criado em": m.created_at.strftime('%d/%m/%Y %H:%M') if m.created_at else 'N/A'
                }
                for m in manufacturers_filtrados
            ])
            
            st.dataframe(
                df_manufacturers,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Nome": st.column_config.TextColumn("Nome", width="medium"), 
                    "País": st.column_config.TextColumn("País", width="medium"),
                    "Website": st.column_config.LinkColumn("Website", width="large"),
                    "Criado em": st.column_config.TextColumn("Criado em", width="medium")
                }
            )
        
        # Análise por país
        if len(manufacturers_filtrados) > 1:
            st.markdown("---")
            st.markdown("### 🌍 Análise por País")
            
            # Contar fabricantes por país
            paises_count = {}
            for manufacturer in manufacturers_filtrados:
                pais = manufacturer.country
                paises_count[pais] = paises_count.get(pais, 0) + 1
            
            # Criar DataFrame para o gráfico
            df_paises = pd.DataFrame(
                list(paises_count.items()),
                columns=['País', 'Quantidade']
            ).sort_values('Quantidade', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.bar_chart(df_paises.set_index('País'))
            
            with col2:
                st.markdown("**Ranking por País:**")
                for i, (pais, qtd) in enumerate(df_paises.values, 1):
                    st.write(f"{i}. **{pais}**: {qtd} fabricante{'s' if qtd > 1 else ''}")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar fabricantes: {str(e)}")
        st.error("Verifique se o banco de dados está acessível.")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())
    
    # Informações sobre os dados
    with st.expander("ℹ️ Sobre os Dados"):
        st.markdown("""
        **Campos dos Fabricantes:**
        
        - **ID**: Identificador único no banco de dados
        - **Nome**: Nome completo do fabricante
        - **País**: País de origem da empresa
        - **Website**: Site oficial (opcional)
        - **Criado em**: Data e hora do cadastro
        
        **Funcionalidades:**
        - Filtros por país e nome
        - Visualização em cards ou tabela
        - Análise estatística por país
        - Links clicáveis para websites
        """)
