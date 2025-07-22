"""
Subpágina para cadastro de fontes de dados meteorológicos

Esta página permite cadastrar as origens dos dados meteorológicos como:
- NASA POWER
- Open-Meteo
- Outras fontes personalizadas
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path para imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.meteorological_data_source.entity import MeteorologicalDataSource
from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository


def create_meteorological_data_source():
    """
    Interface para cadastro de fontes de dados meteorológicos
    """
    
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">🗃️ Cadastro de Fonte de Dados Meteorológicos</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar repositório
    try:
        repo = MeteorologicalDataSourceRepository()
        repo.criar_tabela()
        
        # Exibir fontes já cadastradas
        fontes_existentes = repo.listar_todos()
        
        if fontes_existentes:
            st.markdown("""
            <div class="wind-info-card slide-in">
                <h4 class="wind-info-title">📋 Fontes Já Cadastradas</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            for i, fonte in enumerate(fontes_existentes):
                with [col1, col2, col3][i % 3]:
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 5px;">
                        <strong>🏷️ {fonte.name}</strong><br>
                        <small>Descrição: {fonte.description or 'N/A'}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao inicializar repositório: {str(e)}")
        return

    # Formulário para nova fonte
    with st.form("form_fonte_dados", clear_on_submit=True):
        st.markdown("""
        <div class="wind-info-card slide-in">
            <h4 class="wind-info-title">➕ Nova Fonte de Dados</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Dados básicos
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome da Fonte *",
                placeholder="Ex: NASA_POWER, OPEN_METEO, INMET",
                help="Nome identificador da fonte de dados"
            )
        
        with col2:        
            # Descrição e observações
            descricao = st.text_area(
                "Descrição",
                placeholder="Descreva brevemente esta fonte de dados...",
                help="Informações adicionais sobre a fonte",
                height=100
            )
        
        # Configurações específicas (removido para compatibilidade com a entidade simplificada)
        
        # Botões do formulário
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submitted = st.form_submit_button("💾 Salvar Fonte", use_container_width=True, type="primary")
        
        with col2:
            clear_form = st.form_submit_button("🗑️ Limpar", use_container_width=True)
    
    # Processar formulário
    if submitted:
        # Validações
        erros = []
        
        if not nome or len(nome.strip()) < 2:
            erros.append("Nome deve ter pelo menos 2 caracteres")
        
        if erros:
            for erro in erros:
                st.error(f"❌ {erro}")
            return
        
        try:
            # Verificar se já existe uma fonte com o mesmo nome
            fonte_existente = repo.buscar_por_nome(nome.strip())
            if fonte_existente:
                st.error(f"❌ Já existe uma fonte de dados com o nome '{nome}'. Escolha um nome diferente.")
                return
            
            # Criar nova fonte
            nova_fonte = MeteorologicalDataSource(
                name=nome.strip(),
                description=descricao.strip() if descricao else None
            )
            
            # Salvar no banco
            fonte_id = repo.criar(nova_fonte)
            
            if fonte_id:
                st.success(f"✅ Fonte de dados '{nome}' cadastrada com sucesso! (ID: {fonte_id})")
                st.balloons()
                
                # Recarregar a página para mostrar a nova fonte
                st.rerun()
            else:
                st.error("❌ Erro ao salvar fonte de dados")
                
        except ValueError as ve:
            st.error(f"❌ Erro de validação: {str(ve)}")
        except Exception as e:
            st.error(f"❌ Erro ao cadastrar fonte: {str(e)}")
    
   
    
    # Informações adicionais
    st.markdown("---")
    with st.expander("📚 Informações sobre Fontes de Dados"):
        col1, col2 = st.columns(2)
        col1.markdown("""
        ### 🛰️ NASA POWER
        - **Cobertura:** Global
        - **Resolução temporal:** Diária
        - **Período:** 1981 - presente
        - **Alturas disponíveis:** 10m, 50m
        - **Gratuito:** Sim
        """)
        col2.markdown("""
        ### 🌍 Open-Meteo
        - **Cobertura:** Global
        - **Resolução temporal:** Horária
        - **Período:** 1940 - presente  
        - **Alturas disponíveis:** 10m, 80m, 120m, 180m
        - **Gratuito:** Sim (com limites)
        """)



if __name__ == "__main__":
    create_meteorological_data_source()
