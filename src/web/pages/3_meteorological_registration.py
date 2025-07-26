"""
Página principal de Cadastro de Dados Meteorológicos

Esta página serve como interface principal para cadastro de dados climáticos:
- Fontes de dados meteorológicos (NASA Power, Open-Meteo, etc.)
- Dados meteorológicos coletados das APIs

Cada tipo de cadastro é implementado em uma subpágina separada.
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar as subpáginas de cadastro meteorológico
try:
    from web.pages.meteorological_registration import (
        create_meteorological_data_source, 
        create_meteorological_data,
        view_meteorological_data,
        delete_meteorological_data
    )
except ImportError as e:
    st.error(f"Erro ao importar subpáginas de cadastro meteorológico: {e}")

# try:
#     from pages.meteorological_registration.create_meteorological_data_source import create_meteorological_data_source
#     from pages.meteorological_registration.create_meteorological_data import create_meteorological_data
# except ImportError as e:
#     st.error(f"Erro ao importar subpáginas de cadastro meteorológico: {e}")



# """Função principal da página"""

# Título principal
st.markdown("""
<div class="page-main-header">
    <h1>🌤️ Cadastro de Dados Meteorológicos</h1>
    <p>Gerencie fontes de dados e colete informações climáticas para análise de vento</p>
</div>
""", unsafe_allow_html=True)
# Sidebar com informações
st.sidebar.header("ℹ️ Informações")
st.sidebar.info("""
**Funcionalidades disponíveis:**
1. 🌪️ **Cadastrar Dados** - Colete dados das APIs
2. 🆕 **Cadastrar Fonte** - Registre origens dos dados  
3. 📊 **Visualizar Dados** - Consulte dados coletados
4. 🗑️ **Excluir Dados** - Remova dados específicos

**Fontes Disponíveis:**
• **NASA POWER** - Alturas: 10m, 50m
• **Open-Meteo** - Alturas: 10m
""")
# Avisos importantes
st.sidebar.warning("""
⚠️ **Prevenção de Duplicatas**

O sistema automaticamente verifica e impede o cadastro de dados duplicados com base em:
- Cidade
- Período/Data
- Fonte de dados  
- Altura de captura
""")

st.sidebar.success("""
💡 **Dicas de Uso**

• **Visualização:** Use filtros para explorar os dados
• **Exclusão:** Sempre confira os dados antes de excluir
• **Backup:** Considere exportar antes de excluir
""")
# Inicializar estado da sessão se não existir
if 'selected_meteorological_tab' not in st.session_state:
    st.session_state.selected_meteorological_tab = 'dados'
# Interface principal com abas
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌪️ Cadastrar Dados", use_container_width=True):
        st.session_state.selected_meteorological_tab = 'dados'

with col2:
    if st.button("🆕 Cadastrar Fonte", use_container_width=True):
        st.session_state.selected_meteorological_tab = 'fonte'

with col3:
    if st.button("📊 Visualizar Dados", use_container_width=True):
        st.session_state.selected_meteorological_tab = 'visualizar'

with col4:
    if st.button("🗑️ Excluir Dados", use_container_width=True):
        st.session_state.selected_meteorological_tab = 'excluir'
st.markdown("---")
# Renderizar a aba selecionada
try:
    if st.session_state.selected_meteorological_tab == 'fonte':
        create_meteorological_data_source()
    
    elif st.session_state.selected_meteorological_tab == 'dados':
        create_meteorological_data()
        
    elif st.session_state.selected_meteorological_tab == 'visualizar':
        view_meteorological_data()
        
    elif st.session_state.selected_meteorological_tab == 'excluir':
        delete_meteorological_data()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar interface: {str(e)}")
    
    with st.expander("🔧 Detalhes do erro"):
        import traceback
        st.code(traceback.format_exc())
# Rodapé com links úteis
st.sidebar.markdown("---")
st.sidebar.success("✅ Sistema meteorológico completo ativo!")
st.sidebar.markdown("🌤️ **Cadastro** • 📊 **Visualização** • 🗑️ **Exclusão**")




