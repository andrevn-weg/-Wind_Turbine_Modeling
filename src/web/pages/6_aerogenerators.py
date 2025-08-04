"""
Página 6: Aerogeradores

Esta página gerencia o cadastro e manutenção dos aerogeradores completos.
Depende dos parâmetros cadastrados nas páginas anteriores.
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar as subpáginas
from web.pages.turbine_parameters_pages.aerogenerators.create_aerogenerator import create_aerogenerator
from web.pages.turbine_parameters_pages.aerogenerators.read_aerogenerator import read_aerogenerator
from web.pages.turbine_parameters_pages.aerogenerators.update_aerogenerator import update_aerogenerator
from web.pages.turbine_parameters_pages.aerogenerators.delete_aerogenerator import delete_aerogenerator


# Título principal
st.markdown("""
            <div class="page-main-header">
            <h1>🏭 Aerogeradores</h1>
            <p>Cadastro e gerenciamento de turbinas eólicas completas</p>
            </div>
            """, unsafe_allow_html=True)

# Sidebar com informações
st.sidebar.header("ℹ️ Informações")
st.sidebar.info("""
**Dependências necessárias:**

Para cadastrar aerogeradores, você precisa ter:

✅ **Fabricantes** cadastrados
✅ **Tipos de Turbina** cadastrados  
✅ **Tipos de Gerador** cadastrados
✅ **Tipos de Controle** cadastrados

Se algum item estiver faltando, use a página anterior **Parâmetros das Turbinas**.
""")

# Verificar dependências
st.markdown("### 🔍 Verificação de Dependências")

try:
    from turbine_parameters import (
        ManufacturerRepository, TurbineTypeRepository,
        GeneratorTypeRepository, ControlTypeRepository
    )
    
    # Verificar cada dependência
    dependencias_ok = True
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fabricantes
    try:
        manufacturer_repo = ManufacturerRepository()
        manufacturers_count = manufacturer_repo.contar_total()
        with col1:
            if manufacturers_count > 0:
                st.success(f"✅ Fabricantes: {manufacturers_count}")
            else:
                st.error("❌ Nenhum fabricante")
                dependencias_ok = False
    except:
        with col1:
            st.error("❌ Erro fabricantes")
            dependencias_ok = False
    
    # Tipos de Turbina
    try:
        turbine_type_repo = TurbineTypeRepository()
        turbine_types_count = turbine_type_repo.contar_total()
        with col2:
            if turbine_types_count > 0:
                st.success(f"✅ Tipos Turbina: {turbine_types_count}")
            else:
                st.error("❌ Nenhum tipo turbina")
                dependencias_ok = False
    except:
        with col2:
            st.error("❌ Erro tipos turbina")
            dependencias_ok = False
    
    # Tipos de Gerador
    try:
        generator_type_repo = GeneratorTypeRepository()
        generator_types_count = generator_type_repo.contar_total()
        with col3:
            if generator_types_count > 0:
                st.success(f"✅ Tipos Gerador: {generator_types_count}")
            else:
                st.error("❌ Nenhum tipo gerador")
                dependencias_ok = False
    except:
        with col3:
            st.error("❌ Erro tipos gerador")
            dependencias_ok = False
    
    # Tipos de Controle
    try:
        control_type_repo = ControlTypeRepository()
        control_types_count = control_type_repo.contar_total()
        with col4:
            if control_types_count > 0:
                st.success(f"✅ Tipos Controle: {control_types_count}")
            else:
                st.error("❌ Nenhum tipo controle")
                dependencias_ok = False
    except:
        with col4:
            st.error("❌ Erro tipos controle")
            dependencias_ok = False
    
    if not dependencias_ok:
        st.error("""
        ❌ **Dependências não atendidas!**
        
        Você precisa cadastrar os parâmetros básicos antes de criar aerogeradores.
        Acesse a página **5 - Parâmetros das Turbinas** para cadastrar os dados necessários.
        """)
        st.stop()

except Exception as e:
    st.error(f"❌ Erro ao verificar dependências: {str(e)}")
    st.stop()

# Inicializar estado da sessão se não existir
if 'selected_aerogenerator_action' not in st.session_state:
    st.session_state.selected_aerogenerator_action = 'create'

# Interface de seleção de ação
st.markdown("---")
st.markdown("### 🎯 Ações dos Aerogeradores")

# Criar quatro colunas para os botões de ação
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Cadastrar Aerogerador", use_container_width=True,
                 type="primary" if st.session_state.selected_aerogenerator_action == "create" else "secondary"):
        st.session_state.selected_aerogenerator_action = "create"

with col2:
    if st.button("📋 Visualizar Aerogeradores", use_container_width=True,
                 type="primary" if st.session_state.selected_aerogenerator_action == "read" else "secondary"):
        st.session_state.selected_aerogenerator_action = "read"

with col3:
    if st.button("✏️ Editar Aerogerador", use_container_width=True,
                 type="primary" if st.session_state.selected_aerogenerator_action == "update" else "secondary"):
        st.session_state.selected_aerogenerator_action = "update"

with col4:
    if st.button("🗑️ Excluir Aerogerador", use_container_width=True,
                 type="primary" if st.session_state.selected_aerogenerator_action == "delete" else "secondary"):
        st.session_state.selected_aerogenerator_action = "delete"

st.markdown("---")

# Renderizar a subpágina selecionada
try:
    # Mapeamento das funções
    aerogenerator_functions = {
        "create": create_aerogenerator,
        "read": read_aerogenerator,
        "update": update_aerogenerator,
        "delete": delete_aerogenerator
    }
    
    # Executar a função selecionada
    selected_function = aerogenerator_functions[st.session_state.selected_aerogenerator_action]
    selected_function()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar a página: {str(e)}")
    st.error("Verifique se todos os módulos estão instalados corretamente.")
    
    with st.expander("🔧 Detalhes do erro"):
        import traceback
        st.code(traceback.format_exc())

# Rodapé com estatísticas
st.markdown("---")
st.markdown("### 📊 Estatísticas dos Aerogeradores")

try:
    from turbine_parameters import AerogeneratorRepository
    
    repo = AerogeneratorRepository()
    aerogenerators_count = repo.contar_total()
    
    if aerogenerators_count > 0:
        # Buscar estatísticas por fabricante
        try:
            stats = repo.buscar_estatisticas_por_fabricante()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Aerogeradores", aerogenerators_count)
            
            with col2:
                if stats:
                    potencia_media = sum([s['avg_power_kw'] for s in stats]) / len(stats)
                    st.metric("Potência Média (kW)", f"{potencia_media:.0f}")
                else:
                    st.metric("Potência Média", "N/A")
            
            with col3:
                fabricantes_unicos = len(stats) if stats else 0
                st.metric("Fabricantes Únicos", fabricantes_unicos)
            
            # Tabela de estatísticas por fabricante
            if stats:
                st.markdown("#### 📈 Estatísticas por Fabricante")
                import pandas as pd
                
                df_stats = pd.DataFrame(stats)
                df_display = df_stats[['manufacturer_name', 'total_models', 'avg_power_kw', 'avg_diameter_m']].copy()
                df_display.columns = ['Fabricante', 'Modelos', 'Potência Média (kW)', 'Diâmetro Médio (m)']
                df_display['Potência Média (kW)'] = df_display['Potência Média (kW)'].round(0)
                df_display['Diâmetro Médio (m)'] = df_display['Diâmetro Médio (m)'].round(1)
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        except Exception as stat_error:
            st.warning(f"⚠️ Erro ao carregar estatísticas detalhadas: {str(stat_error)}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Aerogeradores", aerogenerators_count)
            with col2:
                st.metric("Potência Média", "Erro")
            with col3:
                st.metric("Fabricantes Únicos", "Erro")
    else:
        st.info("ℹ️ Nenhum aerogerador cadastrado ainda.")

except Exception as e:
    st.warning("⚠️ Não foi possível carregar as estatísticas dos aerogeradores.")

# Informações sobre aerogeradores
with st.expander("ℹ️ Sobre os Aerogeradores"):
    st.markdown("""
    **Aerogeradores - Turbinas Eólicas Completas:**
    
    Um aerogerador é uma turbina eólica completa com todas as suas especificações técnicas.
    
    **Dados principais incluem:**
    
    📋 **Identificação:**
    - Código único do modelo
    - Nome do modelo
    - Fabricante e ano de fabricação
    
    ⚡ **Características Elétricas:**
    - Potência nominal (kW)
    - Tensão nominal (kV)
    - Potência aparente e fator de potência
    
    🌪️ **Características do Vento:**
    - Velocidades cut-in, cut-out e nominal
    - Faixa operacional de ventos
    
    🔄 **Características do Rotor:**
    - Diâmetro e número de pás
    - Velocidade de rotação nominal
    
    🎛️ **Controle e Operação:**
    - Tipo de controle (Pitch/Stall)
    - Velocidade variável ou fixa
    - Ângulos de pitch mínimo e máximo
    
    **Importante:** Todos os campos técnicos são validados para garantir consistência física.
    """)
