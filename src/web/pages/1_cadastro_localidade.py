"""
Página principal de Cadastro de Localidades

Esta página serve como interface principal para cadastro de dados geográficos:
- Países
- Estados/Regiões
- Cidades

Cada tipo de cadastro é implementado em uma subpágina separada.
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar as subpáginas de cadastro
from web.pages.cadastro_geographic import create_pais, create_estado, create_cidade


# Título principal
# st.title("📍 Cadastro de Localidades")
st.markdown("""
            <div class="page-main-header">
            <h1>📍 Cadastro de Localidades </h1>
            <p>Gerencie países, estados e cidades de forma simples e eficiente</p>
            </div>
            """, unsafe_allow_html=True)
# st.markdown("Sistema para cadastro de dados geográficos: países, estados e cidades")

# Sidebar com informações
st.sidebar.header("ℹ️ Informações")
st.sidebar.info("""
**Ordem recomendada de cadastro:**

1. 🏳️ **País** - Cadastre primeiro o país
2. 🗺️ **Estado** - Depois os estados/regiões  
3. 🏙️ **Cidade** - Por último as cidades

Esta ordem garante que as relações entre as entidades sejam respeitadas.
""")

# Inicializar estado da sessão se não existir
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = 'pais'

# Interface principal com abas
st.markdown("---")

# Criar três colunas para os botões principais
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏳️ Cadastrar País", use_container_width=True, 
                 type="primary" if st.session_state.selected_tab == "pais" else "secondary"):
        st.session_state.selected_tab = "pais"

with col2:
    if st.button("🗺️ Cadastrar Estado", use_container_width=True,
                 type="primary" if st.session_state.selected_tab == "estado" else "secondary"):
        st.session_state.selected_tab = "estado"

with col3:
    if st.button("🏙️ Cadastrar Cidade", use_container_width=True,
                 type="primary" if st.session_state.selected_tab == "cidade" else "secondary"):
        st.session_state.selected_tab = "cidade"

st.markdown("---")

# Renderizar a subpágina selecionada
try:
    if st.session_state.selected_tab == "pais":
        create_pais()
        
    elif st.session_state.selected_tab == "estado":
        create_estado()
        
    elif st.session_state.selected_tab == "cidade":
        create_cidade()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar a página: {str(e)}")
    st.error("Verifique se todos os módulos estão instalados corretamente.")
    
    with st.expander("🔧 Detalhes do erro"):
        import traceback
        st.code(traceback.format_exc())

# Rodapé com informações adicionais
st.markdown("---")
st.markdown("### 📊 Sistema de Dados Geográficos")

# Estatísticas rápidas (se possível carregar)
try:
    from geographic import PaisRepository, RegiaoRepository, CidadeRepository
    
    col1, col2, col3 = st.columns(3)
    
    # Contar países
    try:
        pais_repo = PaisRepository()
        pais_repo.criar_tabela()
        paises = pais_repo.listar_todos()
        with col1:
            st.metric("🏳️ Países", len(paises))
    except:
        with col1:
            st.metric("🏳️ Países", "—")
    
    # Contar regiões
    try:
        regiao_repo = RegiaoRepository()
        regiao_repo.criar_tabela()
        regioes = regiao_repo.listar_todos()
        with col2:
            st.metric("🗺️ Estados/Regiões", len(regioes))
    except:
        with col2:
            st.metric("🗺️ Estados/Regiões", "—")
    
    # Contar cidades
    try:
        cidade_repo = CidadeRepository()
        cidade_repo.criar_tabela()
        cidades = cidade_repo.listar_todos()
        with col3:
            st.metric("🏙️ Cidades", len(cidades))
    except:
        with col3:
            st.metric("🏙️ Cidades", "—")
            
except ImportError:
    st.warning("⚠️ Módulos geográficos não carregados. Verifique a instalação.")

# Informações de uso no sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Como usar")
st.sidebar.markdown("""
1. **Selecione o tipo** de localidade que deseja cadastrar
2. **Preencha os dados** obrigatórios marcados com *
3. **Clique em Salvar** para armazenar no banco de dados
4. **Verifique** os dados salvos usando as opções de visualização

**Dicas:**
- Use coordenadas precisas para cidades
- Códigos ISO são obrigatórios para países
- Siglas de estados são opcionais mas recomendadas
""")

st.sidebar.markdown("---")
st.sidebar.success("✅ Sistema de cadastro de localidades ativo!")
