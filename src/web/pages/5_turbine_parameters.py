"""
Página 5: Parâmetros das Turbinas

Esta página apresenta todas as subpáginas dos parâmetros das turbinas eólicas:
- Manufacturers (Fabricantes)
- Turbine Types (Tipos de Turbina)
- Generator Types (Tipos de Gerador)
- Control Types (Tipos de Controle)

Cada parâmetro possui operações CRUD completas.
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar as subpáginas
from web.pages.turbine_parameters_pages.manufacturers.create_manufacturer import create_manufacturer
from web.pages.turbine_parameters_pages.manufacturers.read_manufacturer import read_manufacturer
from web.pages.turbine_parameters_pages.manufacturers.update_manufacturer import update_manufacturer
from web.pages.turbine_parameters_pages.manufacturers.delete_manufacturer import delete_manufacturer

from web.pages.turbine_parameters_pages.turbine_types.create_turbine_type import create_turbine_type
from web.pages.turbine_parameters_pages.turbine_types.read_turbine_type import read_turbine_type
from web.pages.turbine_parameters_pages.turbine_types.update_turbine_type import update_turbine_type
from web.pages.turbine_parameters_pages.turbine_types.delete_turbine_type import delete_turbine_type

from web.pages.turbine_parameters_pages.generator_types.create_generator_type import create_generator_type
from web.pages.turbine_parameters_pages.generator_types.read_generator_type import read_generator_type
from web.pages.turbine_parameters_pages.generator_types.update_generator_type import update_generator_type
from web.pages.turbine_parameters_pages.generator_types.delete_generator_type import delete_generator_type

from web.pages.turbine_parameters_pages.control_types.create_control_type import create_control_type
from web.pages.turbine_parameters_pages.control_types.read_control_type import read_control_type
from web.pages.turbine_parameters_pages.control_types.update_control_type import update_control_type
from web.pages.turbine_parameters_pages.control_types.delete_control_type import delete_control_type


# Título principal
st.markdown("""
            <div class="page-main-header">
            <h1>⚙️ Parâmetros das Turbinas</h1>
            <p>Gerencie fabricantes, tipos de turbina, geradores e controles</p>
            </div>
            """, unsafe_allow_html=True)

# Sidebar com informações
st.sidebar.header("ℹ️ Informações")
st.sidebar.info("""
**Ordem recomendada de cadastro:**

1. 🏭 **Fabricantes** - Empresas produtoras
2. ⚙️ **Tipos de Turbina** - Horizontal/Vertical
3. 🔌 **Tipos de Gerador** - PMSG, DFIG, etc.
4. 🎛️ **Tipos de Controle** - Pitch, Stall, etc.

Esta ordem garante que as dependências sejam respeitadas.
""")

# Inicializar estado da sessão se não existir
if 'selected_parameter' not in st.session_state:
    st.session_state.selected_parameter = 'manufacturers'
if 'selected_action' not in st.session_state:
    st.session_state.selected_action = 'create'

# Interface principal com seleção de parâmetro
st.markdown("---")
st.markdown("### 🔧 Selecionar Parâmetro")

# Criar quatro colunas para os botões de parâmetros
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏭 Fabricantes", use_container_width=True, 
                 type="primary" if st.session_state.selected_parameter == "manufacturers" else "secondary"):
        st.session_state.selected_parameter = "manufacturers"

with col2:
    if st.button("⚙️ Tipos de Turbina", use_container_width=True,
                 type="primary" if st.session_state.selected_parameter == "turbine_types" else "secondary"):
        st.session_state.selected_parameter = "turbine_types"

with col3:
    if st.button("🔌 Tipos de Gerador", use_container_width=True,
                 type="primary" if st.session_state.selected_parameter == "generator_types" else "secondary"):
        st.session_state.selected_parameter = "generator_types"

with col4:
    if st.button("🎛️ Tipos de Controle", use_container_width=True,
                 type="primary" if st.session_state.selected_parameter == "control_types" else "secondary"):
        st.session_state.selected_parameter = "control_types"

# Interface de seleção de ação
st.markdown("### 🎯 Selecionar Ação")

# Criar quatro colunas para os botões de ação
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Cadastrar", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "create" else "secondary"):
        st.session_state.selected_action = "create"

with col2:
    if st.button("📋 Visualizar", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "read" else "secondary"):
        st.session_state.selected_action = "read"

with col3:
    if st.button("✏️ Editar", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "update" else "secondary"):
        st.session_state.selected_action = "update"

with col4:
    if st.button("🗑️ Excluir", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "delete" else "secondary"):
        st.session_state.selected_action = "delete"

st.markdown("---")

# Renderizar a subpágina selecionada
try:
    # Mapeamento das funções
    functions_map = {
        "manufacturers": {
            "create": create_manufacturer,
            "read": read_manufacturer,
            "update": update_manufacturer,
            "delete": delete_manufacturer
        },
        "turbine_types": {
            "create": create_turbine_type,
            "read": read_turbine_type,
            "update": update_turbine_type,
            "delete": delete_turbine_type
        },
        "generator_types": {
            "create": create_generator_type,
            "read": read_generator_type,
            "update": update_generator_type,
            "delete": delete_generator_type
        },
        "control_types": {
            "create": create_control_type,
            "read": read_control_type,
            "update": update_control_type,
            "delete": delete_control_type
        }
    }
    
    # Executar a função selecionada
    selected_function = functions_map[st.session_state.selected_parameter][st.session_state.selected_action]
    selected_function()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar a página: {str(e)}")
    st.error("Verifique se todos os módulos estão instalados corretamente.")
    
    with st.expander("🔧 Detalhes do erro"):
        import traceback
        st.code(traceback.format_exc())

# Rodapé com informações adicionais
st.markdown("---")
st.markdown("### 📊 Sistema de Parâmetros de Turbinas")

# Mostrar resumo atual
try:
    from turbine_parameters import (
        ManufacturerRepository, TurbineTypeRepository,
        GeneratorTypeRepository, ControlTypeRepository
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        manufacturer_repo = ManufacturerRepository()
        manufacturers_count = manufacturer_repo.contar_total()
        with col1:
            st.metric("Fabricantes", manufacturers_count)
    except:
        with col1:
            st.metric("Fabricantes", "Erro")
    
    try:
        turbine_type_repo = TurbineTypeRepository()
        turbine_types_count = turbine_type_repo.contar_total()
        with col2:
            st.metric("Tipos de Turbina", turbine_types_count)
    except:
        with col2:
            st.metric("Tipos de Turbina", "Erro")
    
    try:
        generator_type_repo = GeneratorTypeRepository()
        generator_types_count = generator_type_repo.contar_total()
        with col3:
            st.metric("Tipos de Gerador", generator_types_count)
    except:
        with col3:
            st.metric("Tipos de Gerador", "Erro")
    
    try:
        control_type_repo = ControlTypeRepository()
        control_types_count = control_type_repo.contar_total()
        with col4:
            st.metric("Tipos de Controle", control_types_count)
    except:
        with col4:
            st.metric("Tipos de Controle", "Erro")
            
except Exception as e:
    st.warning("⚠️ Não foi possível carregar as estatísticas dos parâmetros.")

# Informações sobre os parâmetros
with st.expander("ℹ️ Sobre os Parâmetros das Turbinas"):
    st.markdown("""
    **Parâmetros Fundamentais:**
    
    🏭 **Fabricantes:**
    - Empresas que produzem turbinas eólicas
    - Essencial para identificação e rastreabilidade
    - Influencia características técnicas e disponibilidade
    
    ⚙️ **Tipos de Turbina:**
    - Classificação por orientação do eixo (Horizontal/Vertical)
    - Determina características aerodinâmicas fundamentais
    - Afeta eficiência e aplicação
    
    🔌 **Tipos de Gerador:**
    - Tecnologia de conversão eletromecânica
    - PMSG, DFIG, Síncrono, Assíncrono
    - Impacta na qualidade da energia e controle
    
    🎛️ **Tipos de Controle:**
    - Estratégia de regulação de potência
    - Pitch, Stall, Active Stall
    - Define comportamento em diferentes ventos
    
    **Importante:** Todos estes parâmetros são necessários antes de cadastrar aerogeradores.
    """)
