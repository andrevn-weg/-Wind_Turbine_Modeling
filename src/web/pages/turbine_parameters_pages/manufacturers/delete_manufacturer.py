import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import Manufacturer, ManufacturerRepository


def delete_manufacturer():
    """
    Interface para exclusão de fabricantes
    """
    st.subheader("🗑️ Excluir Fabricante")
    
    # Aviso importante
    st.warning("""
    ⚠️ **ATENÇÃO: Esta operação é irreversível!**
    
    A exclusão de um fabricante pode afetar outros dados do sistema que dependem desta informação.
    """)
    
    try:
        repo = ManufacturerRepository()
        manufacturers = repo.listar_todos()
        
        if not manufacturers:
            st.info("ℹ️ Nenhum fabricante cadastrado para excluir.")
            st.markdown("👆 Use a aba **Cadastrar** para adicionar fabricantes primeiro.")
            return
        
        # Seleção do fabricante para excluir
        st.markdown("### 🔍 Selecionar Fabricante para Excluir")
        
        # Criar opções para o selectbox
        opcoes_fabricantes = {
            f"{m.name} - {m.country} (ID: {m.id})": m.id 
            for m in manufacturers
        }
        
        fabricante_selecionado = st.selectbox(
            "Escolha o fabricante:",
            options=list(opcoes_fabricantes.keys()),
            help="Selecione o fabricante que deseja excluir"
        )
        
        if fabricante_selecionado:
            manufacturer_id = opcoes_fabricantes[fabricante_selecionado]
            manufacturer = repo.buscar_por_id(manufacturer_id)
            
            if not manufacturer:
                st.error("❌ Fabricante não encontrado!")
                return
            
            st.markdown("---")
            st.markdown("### 📋 Dados do Fabricante Selecionado")
            
            # Mostrar dados do fabricante em destaque
            with st.container():
                st.markdown(f"""
                <div style="
                    border: 2px solid #ff4444; 
                    border-radius: 10px; 
                    padding: 20px; 
                    margin: 10px 0;
                    background-color: #ffe6e6;
                ">
                    <h4 style="margin: 0 0 15px 0; color: #cc0000;">🏭 {manufacturer.name}</h4>
                    <p style="margin: 5px 0;"><strong>ID:</strong> {manufacturer.id}</p>
                    <p style="margin: 5px 0;"><strong>País:</strong> {manufacturer.country}</p>
                    <p style="margin: 5px 0;"><strong>Criado em:</strong> {manufacturer.created_at.strftime('%d/%m/%Y %H:%M') if manufacturer.created_at else 'N/A'}</p>
                    {"<p style='margin: 5px 0;'><strong>Website:</strong> <a href='" + manufacturer.official_website + "' target='_blank'>" + manufacturer.official_website + "</a></p>" if manufacturer.official_website else "<p style='margin: 5px 0;'><strong>Website:</strong> Não informado</p>"}
                </div>
                """, unsafe_allow_html=True)
            
            # Verificar dependências (aerogeradores que usam este fabricante)
            st.markdown("### 🔗 Verificação de Dependências")
            
            # Aqui você pode adicionar verificação de aerogeradores que dependem deste fabricante
            # Por enquanto, vamos apenas mostrar um aviso
            st.info("""
            ℹ️ **Verificação de Dependências:**
            
            Antes de excluir este fabricante, verifique se não existem aerogeradores cadastrados que dependem dele.
            A exclusão de um fabricante que possui aerogeradores associados pode causar inconsistências no banco de dados.
            """)
            
            st.markdown("---")
            st.markdown("### ⚠️ Confirmação de Exclusão")
            
            # Checkbox de confirmação
            confirmar_exclusao = st.checkbox(
                f"Confirmo que desejo excluir o fabricante **{manufacturer.name}** permanentemente",
                help="Esta ação não pode ser desfeita!"
            )
            
            # Botão de exclusão (só aparece se confirmado)
            if confirmar_exclusao:
                st.markdown("---")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button(
                        "🗑️ EXCLUIR DEFINITIVAMENTE", 
                        use_container_width=True,
                        type="primary",
                        help="Clique para excluir o fabricante permanentemente"
                    ):
                        try:
                            # Tentar excluir
                            sucesso = repo.excluir(manufacturer.id)
                            
                            if sucesso:
                                st.success(f"✅ Fabricante **{manufacturer.name}** excluído com sucesso!")
                                st.balloons()
                                
                                # Limpar cache do Streamlit para atualizar a lista
                                st.cache_data.clear()
                                
                                # Mostrar confirmação
                                st.info(f"🗑️ Fabricante ID {manufacturer.id} foi removido permanentemente do banco de dados.")
                                
                                # Sugerir recarregar a página
                                st.markdown("🔄 **Recarregue a página** para atualizar a lista de fabricantes.")
                                
                            else:
                                st.error("❌ Erro ao excluir fabricante. Nenhuma linha foi afetada.")
                                st.error("Possível causa: O fabricante pode não existir mais ou estar sendo usado por outros registros.")
                                
                        except Exception as e:
                            st.error(f"❌ Erro ao excluir fabricante: {str(e)}")
                            
                            # Verificar se é erro de constraint (chave estrangeira)
                            if "FOREIGN KEY constraint failed" in str(e) or "foreign key constraint" in str(e).lower():
                                st.error("""
                                🔗 **Erro de Dependência:**
                                
                                Este fabricante não pode ser excluído pois existem aerogeradores cadastrados que dependem dele.
                                Para excluir este fabricante, primeiro remova ou altere todos os aerogeradores associados.
                                """)
                            else:
                                st.error("Verifique se o banco de dados está acessível.")
            
            else:
                st.info("☑️ Marque a caixa de confirmação acima para habilitar o botão de exclusão.")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar fabricantes: {str(e)}")
        st.error("Verifique se o banco de dados está acessível.")
        
        with st.expander("🔧 Detalhes do erro"):
            import traceback
            st.code(traceback.format_exc())
    
    # Informações sobre exclusão
    with st.expander("ℹ️ Informações sobre Exclusão"):
        st.markdown("""
        **Sobre a exclusão de fabricantes:**
        
        ⚠️ **Cuidados importantes:**
        - A exclusão é **permanente** e **irreversível**
        - Verifique dependências antes de excluir
        - Fabricantes com aerogeradores associados não podem ser excluídos
        
        🔗 **Verificação de dependências:**
        - Aerogeradores cadastrados
        - Histórico de dados meteorológicos
        - Análises e relatórios salvos
        
        📋 **Processo de exclusão:**
        1. Selecione o fabricante na lista
        2. Revise os dados exibidos
        3. Verifique as dependências
        4. Confirme a exclusão marcando a caixa
        5. Clique no botão vermelho para excluir
        
        💡 **Dica:** Se você não tem certeza, considere primeiro editar os dados ao invés de excluir.
        """)
