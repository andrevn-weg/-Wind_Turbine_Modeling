import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from geographic import Pais, Regiao, PaisRepository, RegiaoRepository


def create_estado():
    """
    Interface para cadastro de estados/regiões
    """
    st.subheader("🗺️ Cadastro de Estado/Região")
    
    # Carregar países disponíveis
    try:
        pais_repo = PaisRepository()
        pais_repo.criar_tabela()
        paises = pais_repo.listar_todos()
        
        if not paises:
            st.error("❌ Nenhum país cadastrado. Cadastre um país primeiro!")
            if st.button("➕ Ir para Cadastro de País"):
                st.session_state.selected_tab = "pais"
                st.rerun()
            return
            
    except Exception as e:
        st.error(f"Erro ao carregar países: {str(e)}")
        return
    
    with st.form("form_estado", clear_on_submit=False):
        st.markdown("### Dados do Estado/Região")
        
        # Seleção do país
        pais_opcoes = {f"{p.nome} ({p.codigo})": p for p in paises}
        pais_selecionado = st.selectbox(
            "País *",
            options=list(pais_opcoes.keys()),
            help="Selecione o país ao qual este estado/região pertence"
        )
        
        pais_obj = pais_opcoes[pais_selecionado] if pais_selecionado else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome do Estado/Região *", 
                placeholder="Ex: Santa Catarina, São Paulo, California",
                help="Nome completo do estado ou região"
            )
        
        with col2:
            sigla = st.text_input(
                "Sigla", 
                placeholder="Ex: SC, SP, CA",
                max_chars=5,
                help="Sigla ou abreviação do estado (opcional)"
            ).upper()
        
        # Validações visuais
        if nome and len(nome.strip()) > 0:
            st.success(f"✅ Nome válido: {nome}")
        elif nome:
            st.error("❌ Nome não pode estar vazio")
            
        if sigla and len(sigla.strip()) > 0:
            if len(sigla) <= 5:
                st.success(f"✅ Sigla válida: {sigla}")
            else:
                st.error("❌ Sigla deve ter no máximo 5 caracteres")
        
        st.markdown("---")
        
        # Botões
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                "💾 Salvar Estado", 
                type="primary", 
                use_container_width=True
            )
        
        if submitted and pais_obj:
            # Criar e validar região
            regiao = Regiao(
                nome=nome.strip(), 
                pais_id=pais_obj.id, 
                sigla=sigla.strip() if sigla.strip() else None
            )
            
            if not regiao.validar():
                st.error("❌ Dados do estado são inválidos. Verifique os campos obrigatórios.")
                return
            
            try:
                repo = RegiaoRepository()
                repo.criar_tabela()
                
                # Verificar se já existe estado com mesma sigla no país (se sigla foi informada)
                if sigla and sigla.strip():
                    if repo.existe_sigla_no_pais(sigla, pais_obj.id):
                        st.error(f"❌ Já existe um estado com a sigla '{sigla}' no país {pais_obj.nome}")
                        return
                
                # Verificar se já existe estado com mesmo nome no país
                estados_existentes = repo.buscar_por_nome(nome)
                estado_mesmo_pais = next((e for e in estados_existentes if e.pais_id == pais_obj.id), None)
                if estado_mesmo_pais:
                    st.error(f"❌ Já existe um estado com o nome '{nome}' no país {pais_obj.nome}")
                    return
                
                # Salvar novo estado
                estado_id = repo.salvar(regiao)
                st.success(f"✅ Estado '{regiao.nome_completo()}' salvo com sucesso! (ID: {estado_id})")
                
                # Mostrar detalhes
                with st.expander("📋 Detalhes do estado salvo", expanded=True):
                    st.json({
                        "id": estado_id,
                        "nome": regiao.nome,
                        "sigla": regiao.sigla,
                        "pais": pais_obj.nome,
                        "nome_completo": regiao.nome_completo()
                    })
                
                st.info("💡 Recarregue a página ou use o menu lateral para cadastrar outro estado.")
                
            except Exception as e:
                st.error(f"❌ Erro ao salvar estado: {str(e)}")
    
    # Seção de ajuda
    with st.expander("ℹ️ Ajuda - Estados e Regiões"):
        st.markdown("""
        **Exemplos de estados/regiões:**
        
        **Brasil:**
        - Santa Catarina (SC)
        - São Paulo (SP)
        - Rio de Janeiro (RJ)
        - Minas Gerais (MG)
        
        **Estados Unidos:**
        - California (CA)
        - New York (NY)
        - Texas (TX)
        - Florida (FL)
        
        **Dicas:**
        - O nome deve ser único dentro do país
        - A sigla é opcional, mas se informada, deve ser única no país
        - Use nomes oficiais sempre que possível
        """)
    
    # Mostrar estados do país selecionado
    if st.checkbox("📋 Ver estados do país selecionado") and pais_obj:
        try:
            repo = RegiaoRepository()
            estados = repo.buscar_por_pais(pais_obj.id)
            
            if estados:
                st.markdown(f"### Estados de {pais_obj.nome}")
                for estado in estados:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{estado.nome_completo()}**")
                    with col2:
                        if estado.sigla:
                            st.code(estado.sigla)
                        else:
                            st.caption("Sem sigla")
                    with col3:
                        st.caption(f"ID: {estado.id}")
            else:
                st.info(f"Nenhum estado cadastrado para {pais_obj.nome}.")
                
        except Exception as e:
            st.error(f"Erro ao carregar estados: {str(e)}")


if __name__ == "__main__":
    # Para teste individual da página
    # st.set_page_config(page_title="Cadastro de Estado", page_icon="🗺️")
    create_estado()
