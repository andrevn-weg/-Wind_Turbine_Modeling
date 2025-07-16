import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from geographic import Pais, PaisRepository


def create_pais():
    """
    Interface para cadastro de países
    """
    st.subheader("🏳️ Cadastro de País")
    
    with st.form("form_pais", clear_on_submit=False):
        st.markdown("### Dados do País")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome do País *", 
                placeholder="Ex: Brasil, Estados Unidos, Argentina",
                help="Nome completo do país"
            )
        
        with col2:
            codigo = st.text_input(
                "Código ISO *", 
                placeholder="Ex: BR, US, AR",
                max_chars=2,
                help="Código ISO de 2 caracteres (maiúsculas)"
            ).upper()
        
        # Validações visuais
        if nome and len(nome.strip()) > 0:
            st.success(f"✅ Nome válido: {nome}")
        elif nome:
            st.error("❌ Nome não pode estar vazio")
            
        if codigo and len(codigo) == 2 and codigo.isalpha():
            st.success(f"✅ Código válido: {codigo}")
        elif codigo:
            if len(codigo) != 2:
                st.error("❌ Código deve ter exatamente 2 caracteres")
            elif not codigo.isalpha():
                st.error("❌ Código deve conter apenas letras")
        
        st.markdown("---")
        
        # Botões
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                "💾 Salvar País", 
                type="primary", 
                use_container_width=True
            )
        
        if submitted:
            # Criar e validar país
            pais = Pais(nome=nome.strip(), codigo=codigo.strip())
            
            if not pais.validar():
                st.error("❌ Dados do país são inválidos. Verifique os campos obrigatórios.")
                return
            
            try:
                # Verificar se já existe
                repo = PaisRepository()
                repo.criar_tabela()
                
                pais_existente = repo.buscar_por_codigo(codigo)
                if pais_existente:
                    st.error(f"❌ Já existe um país com o código '{codigo}': {pais_existente.nome}")
                    return
                
                # Salvar novo país
                pais_id = repo.salvar(pais)
                st.success(f"✅ País '{nome}' salvo com sucesso! (ID: {pais_id})")
                
                # Mostrar detalhes
                with st.expander("📋 Detalhes do país salvo", expanded=True):
                    st.json({
                        "id": pais_id,
                        "nome": pais.nome,
                        "codigo": pais.codigo
                    })
                
                # Limpar o formulário seria ideal, mas o Streamlit não suporta diretamente
                st.info("💡 Recarregue a página ou use o menu lateral para cadastrar outro país.")
                
            except Exception as e:
                st.error(f"❌ Erro ao salvar país: {str(e)}")
    
    # Seção de ajuda
    with st.expander("ℹ️ Ajuda - Códigos ISO de Países"):
        st.markdown("""
        **Exemplos de códigos ISO válidos:**
        - 🇧🇷 **BR** - Brasil
        - 🇺🇸 **US** - Estados Unidos  
        - 🇦🇷 **AR** - Argentina
        - 🇨🇱 **CL** - Chile
        - 🇺🇾 **UY** - Uruguai
        - 🇵🇾 **PY** - Paraguai
        - 🇨🇦 **CA** - Canadá
        - 🇲🇽 **MX** - México
        
        **Regras:**
        - Deve ter exatamente 2 caracteres
        - Apenas letras (A-Z)
        - Automaticamente convertido para maiúsculas
        """)
    
    # Mostrar países existentes
    if st.checkbox("📋 Ver países cadastrados"):
        try:
            repo = PaisRepository()
            paises = repo.listar_todos()
            
            if paises:
                st.markdown("### Países Cadastrados")
                for pais in paises:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{pais.nome}**")
                    with col2:
                        st.code(pais.codigo)
                    with col3:
                        st.caption(f"ID: {pais.id}")
            else:
                st.info("Nenhum país cadastrado ainda.")
                
        except Exception as e:
            st.error(f"Erro ao carregar países: {str(e)}")


if __name__ == "__main__":
    # Para teste individual da página
    # st.set_page_config(page_title="Cadastro de País", page_icon="🏳️")
    create_pais()
