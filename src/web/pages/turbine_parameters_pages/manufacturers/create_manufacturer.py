import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import Manufacturer, ManufacturerRepository


def create_manufacturer():
    """
    Interface para cadastro de fabricantes de turbinas eólicas
    """
    st.subheader("🏭 Cadastro de Fabricante")
    
    with st.form("form_manufacturer", clear_on_submit=False):
        st.markdown("### Dados do Fabricante")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nome do Fabricante *", 
                placeholder="Ex: Vestas Wind Systems, General Electric",
                help="Nome completo do fabricante"
            )
        
        with col2:
            country = st.text_input(
                "País *", 
                placeholder="Ex: Denmark, United States, Germany",
                help="País de origem do fabricante"
            )
        
        official_website = st.text_input(
            "Website Oficial",
            placeholder="Ex: https://www.vestas.com",
            help="URL do website oficial (opcional)"
        )
        
        # Validações visuais
        valid_name = name and len(name.strip()) > 0
        valid_country = country and len(country.strip()) > 0
        
        if name:
            if valid_name:
                st.success(f"✅ Nome válido: {name}")
            else:
                st.error("❌ Nome não pode estar vazio")
                
        if country:
            if valid_country:
                st.success(f"✅ País válido: {country}")
            else:
                st.error("❌ País não pode estar vazio")
        
        if official_website and official_website.strip():
            if official_website.startswith(('http://', 'https://')):
                st.success(f"✅ Website válido: {official_website}")
            else:
                st.warning("⚠️ Website deve começar com http:// ou https://")
        
        # Botão Submit
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button(
                "💾 Cadastrar Fabricante", 
                use_container_width=True,
                type="primary"
            )
    
    # Processar submissão
    if submitted:
        if not valid_name:
            st.error("❌ Nome do fabricante é obrigatório!")
            return
            
        if not valid_country:
            st.error("❌ País é obrigatório!")
            return
        
        try:
            # Criar instância do fabricante
            manufacturer = Manufacturer(
                name=name.strip(),
                country=country.strip(),
                official_website=official_website.strip() if official_website and official_website.strip() else None
            )
            
            # Salvar no banco
            repo = ManufacturerRepository()
            repo.criar_tabela()  # Garante que a tabela existe
            manufacturer_id = repo.salvar(manufacturer)
            
            st.success(f"✅ Fabricante cadastrado com sucesso! ID: {manufacturer_id}")
            st.balloons()
            
            # Mostrar dados cadastrados
            with st.expander("📋 Dados Cadastrados", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ID", manufacturer_id)
                with col2:
                    st.metric("Nome", manufacturer.name)
                with col3:
                    st.metric("País", manufacturer.country)
                
                if manufacturer.official_website:
                    st.write(f"**Website:** [{manufacturer.official_website}]({manufacturer.official_website})")
            
        except ValueError as e:
            st.error(f"❌ Erro de validação: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro ao cadastrar fabricante: {str(e)}")
            st.error("Verifique se o banco de dados está acessível.")
    
    # Informações adicionais
    with st.expander("ℹ️ Informações sobre Fabricantes"):
        st.markdown("""
        **Fabricantes de Turbinas Eólicas:**
        
        Os fabricantes são empresas especializadas na produção de turbinas eólicas.
        Alguns dos principais fabricantes mundiais incluem:
        
        - **Vestas** (Dinamarca) - Líder mundial em turbinas eólicas
        - **General Electric** (EUA) - Grande diversificado com divisão eólica
        - **Siemens Gamesa** (Espanha/Alemanha) - Resultado da fusão Siemens/Gamesa
        - **Goldwind** (China) - Maior fabricante chinês
        - **Enercon** (Alemanha) - Especialista em turbinas sem caixa de engrenagens
        
        **Campos obrigatórios:** Nome e País
        **Campo opcional:** Website oficial
        """)
