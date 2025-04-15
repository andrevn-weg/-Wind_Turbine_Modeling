import streamlit as st
import pandas as pd
import os
import sys
import json
from datetime import datetime

# Adiciona o diretório raiz ao path para importar corretamente os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.wind_models.vento_api import VentoAPI

st.set_page_config(page_title="Localidades Cadastradas - Potencial Eólico", layout="wide")
st.title("Localidades Cadastradas para Análise Eólica")

# Sidebar para instruções
st.sidebar.header("Informações")
st.sidebar.info("""
Este módulo exibe todas as localidades cadastradas para análise de potencial eólico.

Você pode:
1. Visualizar todas as localidades cadastradas
2. Ver os detalhes de cada localidade
3. Iniciar simulações com base nessas localidades
4. Excluir localidades
""")

# Função para carregar localidades
def carregar_localidades():
    localidades = []
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database'))
    
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        return []
    
    for filename in os.listdir(db_path):
        if filename.endswith('.json'):
            file_path = os.path.join(db_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Adiciona o caminho do arquivo para possível exclusão
                    data['file_path'] = file_path
                    localidades.append(data)
            except Exception as e:
                st.error(f"Erro ao carregar arquivo {filename}: {str(e)}")
    
    return localidades

# Exibir título e informações
st.header("Lista de Localidades Cadastradas")

# Carregar localidades
localidades = carregar_localidades()

if not localidades:
    st.info("Nenhuma localidade cadastrada ainda. [Cadastre uma nova localidade](/wind_pages/cadastro_localidade).")
else:
    # Criar DataFrame para exibição
    df_view = []
    for local in localidades:
        df_view.append({
            'Nome': local.get('nome', 'Sem nome'),
            'Latitude': local.get('latitude', 0),
            'Longitude': local.get('longitude', 0),
            'Altura (m)': local.get('altura', 0),
            'Velocidade Média (m/s)': local.get('vento_medio', 'N/A'),
            'Topologia': local.get('topologia_terreno', 'N/A'),
            'Data Cadastro': local.get('data_cadastro', 'N/A')
        })
    
    df = pd.DataFrame(df_view)
    st.dataframe(df, use_container_width=True)
    
    # Exibir mapa com todas as localidades
    st.subheader("Mapa de Localidades")
    
    map_data = pd.DataFrame({
        'lat': [local.get('latitude', 0) for local in localidades],
        'lon': [local.get('longitude', 0) for local in localidades],
        'name': [local.get('nome', 'Sem nome') for local in localidades]
    })
    
    st.map(map_data)
    
    # Detalhes e ações para localidades específicas
    st.header("Detalhes da Localidade")
    
    # Seleção de localidade
    nomes_localidades = [local.get('nome', f"Localidade {i}") for i, local in enumerate(localidades)]
    localidade_selecionada = st.selectbox("Selecione uma localidade para ver detalhes", nomes_localidades)
    
    # Encontrar a localidade selecionada
    indice = nomes_localidades.index(localidade_selecionada)
    local = localidades[indice]
    
    # Exibir detalhes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Informações")
        st.write(f"**Nome:** {local.get('nome', 'N/A')}")
        st.write(f"**Latitude:** {local.get('latitude', 'N/A')}")
        st.write(f"**Longitude:** {local.get('longitude', 'N/A')}")
        st.write(f"**Altura de referência:** {local.get('altura', 'N/A')} metros")
        st.write(f"**Topologia:** {local.get('topologia_terreno', 'N/A')}")
        st.write(f"**Velocidade Média do Vento:** {local.get('vento_medio', 'N/A')} m/s")
        st.write(f"**Data de Cadastro:** {local.get('data_cadastro', 'N/A')}")
    
    with col2:
        st.subheader("Ações")
        
        # Botão para iniciar simulação com esta localidade
        if st.button("Iniciar Simulação", key=f"sim_{indice}"):
            # Redirecionar para a página de simulação (a ser implementada)
            st.success(f"Iniciando simulação para {local.get('nome', 'esta localidade')}...")
            st.info("Funcionalidade de simulação a ser implementada.")
        
        # Botão para atualizar dados
        if st.button("Atualizar Dados", key=f"upd_{indice}"):
            st.session_state.localidade_para_atualizar = local
            st.success(f"Redirecionando para atualização de {local.get('nome', 'esta localidade')}...")
            st.info("Funcionalidade de atualização a ser implementada.")
        
        # Botão para excluir localidade
        if st.button("Excluir Localidade", key=f"del_{indice}", type="secondary"):
            if 'confirmar_exclusao' not in st.session_state:
                st.session_state.confirmar_exclusao = None
            
            if st.session_state.confirmar_exclusao == indice:
                # Excluir o arquivo
                file_path = local.get('file_path')
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        st.success(f"Localidade '{local.get('nome', 'Sem nome')}' excluída com sucesso!")
                        st.session_state.confirmar_exclusao = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {str(e)}")
                else:
                    st.error("Caminho do arquivo não encontrado.")
            else:
                st.session_state.confirmar_exclusao = indice
                st.warning(f"Tem certeza que deseja excluir '{local.get('nome', 'esta localidade')}'? Clique novamente para confirmar.")
        
        # Limpar confirmação se mudar a seleção
        if 'confirmar_exclusao' in st.session_state and st.session_state.confirmar_exclusao != indice:
            st.session_state.confirmar_exclusao = None

# Botão para adicionar nova localidade
st.sidebar.markdown("---")
if st.sidebar.button("Adicionar Nova Localidade", type="primary"):
    st.sidebar.success("Redirecionando para o cadastro...")
    st.sidebar.markdown("[Clique aqui se não for redirecionado](/wind_pages/cadastro_localidade)")

# Informações adicionais no rodapé
st.sidebar.markdown("---")
st.sidebar.info("""
## Sobre o Sistema
Este sistema permite o gerenciamento de localidades para análise de potencial eólico.

As localidades cadastradas podem ser utilizadas para:
- Análise de viabilidade de instalação de turbinas eólicas
- Previsão de geração de energia
- Simulação de diferentes cenários de vento
""")