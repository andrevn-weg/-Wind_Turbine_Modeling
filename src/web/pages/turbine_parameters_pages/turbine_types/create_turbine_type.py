import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import TurbineType, TurbineTypeRepository


def create_turbine_type():
    """
    Interface para cadastro de tipos de turbina
    """
    st.subheader("⚙️ Cadastro de Tipo de Turbina")
    
    with st.form("form_turbine_type", clear_on_submit=False):
        st.markdown("### Dados do Tipo de Turbina")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            type_name = st.text_input(
                "Tipo *", 
                placeholder="Ex: Horizontal, Vertical",
                help="Nome do tipo de turbina"
            )
        
        with col2:
            description = st.text_area(
                "Descrição",
                placeholder="Ex: Turbinas de eixo horizontal - tipo mais comum, com rotor paralelo ao solo",
                help="Descrição detalhada do tipo de turbina (opcional)",
                height=100
            )
        
        # Validações visuais
        valid_type = type_name and len(type_name.strip()) > 0
        
        if type_name:
            if valid_type:
                st.success(f"✅ Tipo válido: {type_name}")
            else:
                st.error("❌ Tipo não pode estar vazio")
        
        if description and description.strip():
            st.success(f"✅ Descrição adicionada ({len(description.strip())} caracteres)")
        
        # Informações sobre tipos comuns
        with st.expander("ℹ️ Tipos Comuns de Turbinas"):
            st.markdown("""
            **Principais tipos de turbinas eólicas:**
            
            🔄 **Horizontal (HAWT - Horizontal Axis Wind Turbine):**
            - Eixo de rotação paralelo ao solo
            - Tipo mais comum e eficiente
            - Requer sistema de orientação ao vento
            - Geralmente 3 pás
            
            ↕️ **Vertical (VAWT - Vertical Axis Wind Turbine):**
            - Eixo de rotação perpendicular ao solo
            - Capta vento de qualquer direção
            - Menos eficiente que horizontal
            - Exemplos: Savonius, Darrieus
            """)
        
        # Botão Submit
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button(
                "💾 Cadastrar Tipo", 
                use_container_width=True,
                type="primary"
            )
    
    # Processar submissão
    if submitted:
        if not valid_type:
            st.error("❌ Tipo de turbina é obrigatório!")
            return
        
        try:
            # Criar instância do tipo de turbina
            turbine_type = TurbineType(
                type=type_name.strip(),
                description=description.strip() if description and description.strip() else None
            )
            
            # Salvar no banco
            repo = TurbineTypeRepository()
            repo.criar_tabela()  # Garante que a tabela existe
            type_id = repo.salvar(turbine_type)
            
            st.success(f"✅ Tipo de turbina cadastrado com sucesso! ID: {type_id}")
            st.balloons()
            
            # Mostrar dados cadastrados
            with st.expander("📋 Dados Cadastrados", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ID", type_id)
                    st.metric("Tipo", turbine_type.type)
                with col2:
                    if turbine_type.description:
                        st.write("**Descrição:**")
                        st.write(turbine_type.description)
                    else:
                        st.info("Sem descrição")
            
        except ValueError as e:
            st.error(f"❌ Erro de validação: {str(e)}")
            
            # Verificar se é erro de tipo duplicado
            if "já existe" in str(e).lower() or "unique" in str(e).lower():
                st.error(f"🔄 **Tipo duplicado:** Já existe um tipo de turbina com o nome '{type_name.strip()}'")
                st.info("💡 **Sugestão:** Use a aba **Visualizar** para ver os tipos já cadastrados.")
                
        except Exception as e:
            st.error(f"❌ Erro ao cadastrar tipo de turbina: {str(e)}")
            st.error("Verifique se o banco de dados está acessível.")
    
    # Seção de inicialização padrão
    st.markdown("---")
    st.markdown("### 🛠️ Inicialização de Tipos Padrão")
    
    if st.button("🔄 Inicializar Tipos Padrão", help="Cria os tipos básicos se não existirem"):
        try:
            repo = TurbineTypeRepository()
            repo.criar_tabela()
            repo.inicializar_tipos_padrao()
            
            st.success("✅ Tipos padrão inicializados com sucesso!")
            st.info("""
            📋 **Tipos criados:**
            - **Horizontal:** Turbinas de eixo horizontal - tipo mais comum
            - **Vertical:** Turbinas de eixo vertical - captam vento de qualquer direção
            """)
            
        except Exception as e:
            st.warning(f"⚠️ Aviso na inicialização: {str(e)}")
            st.info("Os tipos padrão podem já estar cadastrados.")
    
    # Informações adicionais
    with st.expander("ℹ️ Informações sobre Tipos de Turbina"):
        st.markdown("""
        **Tipos de Turbinas Eólicas:**
        
        Os tipos de turbina definem a orientação e configuração básica da turbina eólica.
        Esta classificação é fundamental para análises de performance e características operacionais.
        
        **Principais características:**
        
        🔄 **Turbinas Horizontais (HAWT):**
        - Representa 95% das turbinas comerciais
        - Maior eficiência aerodinâmica
        - Torre mais alta necessária
        - Sistema de orientação (yaw) obrigatório
        
        ↕️ **Turbinas Verticais (VAWT):**
        - Menor eficiência, mas mais robustas
        - Funcionam com vento de qualquer direção
        - Manutenção mais fácil (componentes no solo)
        - Menor impacto visual e sonoro
        
        **Campo obrigatório:** Tipo
        **Campo opcional:** Descrição detalhada
        """)
