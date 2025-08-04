import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import Manufacturer, ManufacturerRepository


def update_manufacturer():
    """
    Interface para edição de fabricantes existentes
    """
    st.subheader("✏️ Editar Fabricante")
    
    try:
        repo = ManufacturerRepository()
        manufacturers = repo.listar_todos()
        
        if not manufacturers:
            st.info("ℹ️ Nenhum fabricante cadastrado para editar.")
            st.markdown("👆 Use a aba **Cadastrar** para adicionar fabricantes primeiro.")
            return
        
        # Seleção do fabricante para editar
        st.markdown("### 🔍 Selecionar Fabricante para Editar")
        
        # Criar opções para o selectbox
        opcoes_fabricantes = {
            f"{m.name} - {m.country} (ID: {m.id})": m.id 
            for m in manufacturers
        }
        
        fabricante_selecionado = st.selectbox(
            "Escolha o fabricante:",
            options=list(opcoes_fabricantes.keys()),
            help="Selecione o fabricante que deseja editar"
        )
        
        if fabricante_selecionado:
            manufacturer_id = opcoes_fabricantes[fabricante_selecionado]
            manufacturer = repo.buscar_por_id(manufacturer_id)
            
            if not manufacturer:
                st.error("❌ Fabricante não encontrado!")
                return
            
            st.markdown("---")
            st.markdown("### 📝 Dados Atuais")
            
            # Mostrar dados atuais
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Nome Atual:** {manufacturer.name}")
            with col2:
                st.info(f"**País Atual:** {manufacturer.country}")
            with col3:
                website_atual = manufacturer.official_website or "Não informado"
                st.info(f"**Website Atual:** {website_atual}")
            
            st.markdown("### ✏️ Novos Dados")
            
            # Formulário de edição
            with st.form("form_edit_manufacturer", clear_on_submit=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input(
                        "Nome do Fabricante *", 
                        value=manufacturer.name,
                        placeholder="Ex: Vestas Wind Systems, General Electric",
                        help="Nome completo do fabricante"
                    )
                
                with col2:
                    new_country = st.text_input(
                        "País *", 
                        value=manufacturer.country,
                        placeholder="Ex: Denmark, United States, Germany",
                        help="País de origem do fabricante"
                    )
                
                new_website = st.text_input(
                    "Website Oficial",
                    value=manufacturer.official_website or "",
                    placeholder="Ex: https://www.vestas.com",
                    help="URL do website oficial (opcional)"
                )
                
                # Validações visuais
                valid_name = new_name and len(new_name.strip()) > 0
                valid_country = new_country and len(new_country.strip()) > 0
                
                # Mostrar mudanças
                if new_name != manufacturer.name:
                    st.warning(f"🔄 Nome será alterado: **{manufacturer.name}** → **{new_name}**")
                
                if new_country != manufacturer.country:
                    st.warning(f"🔄 País será alterado: **{manufacturer.country}** → **{new_country}**")
                
                website_original = manufacturer.official_website or ""
                if new_website.strip() != website_original:
                    st.warning(f"🔄 Website será alterado: **{website_original or 'Vazio'}** → **{new_website or 'Vazio'}**")
                
                if new_name:
                    if valid_name:
                        st.success(f"✅ Nome válido: {new_name}")
                    else:
                        st.error("❌ Nome não pode estar vazio")
                        
                if new_country:
                    if valid_country:
                        st.success(f"✅ País válido: {new_country}")
                    else:
                        st.error("❌ País não pode estar vazio")
                
                if new_website and new_website.strip():
                    if new_website.startswith(('http://', 'https://')):
                        st.success(f"✅ Website válido: {new_website}")
                    else:
                        st.warning("⚠️ Website deve começar com http:// ou https://")
                
                # Botões de ação
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    submitted = st.form_submit_button(
                        "💾 Salvar Alterações", 
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
                
                # Verificar se houve alterações
                alteracoes = []
                if new_name.strip() != manufacturer.name:
                    alteracoes.append("Nome")
                if new_country.strip() != manufacturer.country:
                    alteracoes.append("País")
                if new_website.strip() != (manufacturer.official_website or ""):
                    alteracoes.append("Website")
                
                if not alteracoes:
                    st.info("ℹ️ Nenhuma alteração foi feita.")
                    return
                
                try:
                    # Atualizar dados do fabricante
                    manufacturer.name = new_name.strip()
                    manufacturer.country = new_country.strip()
                    manufacturer.official_website = new_website.strip() if new_website and new_website.strip() else None
                    
                    # Salvar no banco
                    sucesso = repo.atualizar(manufacturer)
                    
                    if sucesso:
                        st.success(f"✅ Fabricante atualizado com sucesso!")
                        st.success(f"🔄 Campos alterados: {', '.join(alteracoes)}")
                        st.balloons()
                        
                        # Mostrar dados atualizados
                        with st.expander("📋 Dados Atualizados", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("ID", manufacturer.id)
                            with col2:
                                st.metric("Nome", manufacturer.name)
                            with col3:
                                st.metric("País", manufacturer.country)
                            
                            if manufacturer.official_website:
                                st.write(f"**Website:** [{manufacturer.official_website}]({manufacturer.official_website})")
                    else:
                        st.error("❌ Erro ao atualizar fabricante. Nenhuma linha foi afetada.")
                        
                except ValueError as e:
                    st.error(f"❌ Erro de validação: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar fabricante: {str(e)}")
                    st.error("Verifique se o banco de dados está acessível.")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar fabricantes: {str(e)}")
        st.error("Verifique se o banco de dados está acessível.")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())
    
    # Informações sobre edição
    with st.expander("ℹ️ Informações sobre Edição"):
        st.markdown("""
        **Como editar um fabricante:**
        
        1. **Selecione** o fabricante que deseja editar na lista
        2. **Visualize** os dados atuais destacados em azul
        3. **Modifique** os campos necessários no formulário
        4. **Observe** as mudanças destacadas em amarelo
        5. **Salve** as alterações clicando no botão
        
        **Campos obrigatórios:** Nome e País
        **Campo opcional:** Website oficial
        
        **Dica:** As alterações são destacadas automaticamente para facilitar a revisão.
        """)
