import streamlit as st
import pandas as pd
import os
import sys
import json
from datetime import datetime

# Adiciona o diretório raiz ao path para importar corretamente os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.wind_models.vento_api import VentoAPI

st.set_page_config(page_title="Cadastro de Localidade - Potencial Eólico", layout="wide")
st.title("Cadastro de Localidade para Análise de Potencial Eólico")

# Sidebar para instruções
st.sidebar.header("Instruções")
st.sidebar.info("""
Este módulo permite cadastrar novas localidades para análise de potencial eólico.

Você pode:
1. Buscar localidades pelo nome (usando OpenStreetMap)
2. Informar coordenadas geográficas diretamente
3. Opcionalmente, buscar dados históricos de vento se disponíveis
4. Salvar a localidade no banco de dados local
""")

# Formulário de cadastro
st.header("Informações da Localidade")

col1, col2 = st.columns(2)

with col1:
    # Método de entrada
    metodo_entrada = st.radio(
        "Como deseja cadastrar a localidade?",
        ["Buscar pelo nome", "Informar coordenadas diretamente"]
    )
    
    if metodo_entrada == "Buscar pelo nome":
        nome_local = st.text_input("Nome da localidade (cidade, estado, país)", "")
        buscar = st.button("Buscar Coordenadas", type="primary")
        
        if buscar and nome_local:
            with st.spinner("Buscando coordenadas..."):
                vento_api = VentoAPI()
                resultado = vento_api.obter_coordenadas_por_nome(nome_local)
                
                if resultado:
                    latitude, longitude = resultado
                    st.success(f"Localidade encontrada: {vento_api.local}")
                    st.session_state.localidade = {
                        "nome": vento_api.local,
                        "latitude": latitude,
                        "longitude": longitude
                    }
                else:
                    st.error(f"Não foi possível encontrar coordenadas para '{nome_local}'")
    else:
        nome_local = st.text_input("Nome da localidade", "")
        latitude = st.number_input("Latitude", value=0.0, format="%.6f", min_value=-90.0, max_value=90.0)
        longitude = st.number_input("Longitude", value=0.0, format="%.6f", min_value=-180.0, max_value=180.0)
        
        if st.button("Confirmar Coordenadas", type="primary"):
            if nome_local:
                st.session_state.localidade = {
                    "nome": nome_local,
                    "latitude": latitude,
                    "longitude": longitude
                }
                st.success("Coordenadas confirmadas!")
            else:
                st.error("É necessário informar o nome da localidade.")

with col2:
    # Parâmetros adicionais
    st.subheader("Parâmetros do Local")
    
    # Altura da turbina
    altura = st.slider("Altura de referência (m)", 
                      min_value=10, max_value=150, value=50, step=5)
    
    # Topologia do terreno
    topologias = list(VentoAPI.topologia.keys())
    topologia_selecionada = st.selectbox("Topologia do terreno", options=topologias)
    
    # Velocidade média (opcional)
    usar_vento_manual = st.checkbox("Definir velocidade média manualmente")
    vento_medio = None
    if usar_vento_manual:
        vento_medio = st.slider("Velocidade média do vento (m/s)", 
                               min_value=1.0, max_value=15.0, value=6.5, step=0.1)
    
    # Buscar dados históricos
    buscar_dados = st.checkbox("Buscar dados históricos de vento (se disponível)")
    periodo_dias = 30
    if buscar_dados:
        periodo_dias = st.slider("Período de dados históricos (dias)", 
                               min_value=7, max_value=365, value=30, step=1)

# Visualizar localidade no mapa se disponível
if 'localidade' in st.session_state:
    st.header("Visualização da Localidade")
    localidade = st.session_state.localidade
    
    # Exibir informações
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Informações da Localidade")
        st.write(f"**Nome:** {localidade['nome']}")
        st.write(f"**Latitude:** {localidade['latitude']}")
        st.write(f"**Longitude:** {localidade['longitude']}")
    
    # Exibir mapa
    with col2:
        st.subheader("Localização no Mapa")
        df = pd.DataFrame({
            'lat': [localidade['latitude']],
            'lon': [localidade['longitude']]
        })
        st.map(df)
    
    # Opção para buscar dados históricos
    if buscar_dados:
        st.header("Dados Históricos de Vento")
        
        if st.button("Obter Dados Históricos", type="primary"):
            with st.spinner("Buscando dados históricos de vento..."):
                vento_api = VentoAPI(
                    local=localidade['nome'],
                    altura=altura,
                    topologia_terreno=topologia_selecionada,
                    latitude=localidade['latitude'],
                    longitude=localidade['longitude'],
                    vento_medio=vento_medio
                )
                
                serie_temporal = vento_api.obter_dados_vento_reais(periodo_dias=periodo_dias)
                
                if serie_temporal is not None and not serie_temporal.empty:
                    st.success("Dados históricos obtidos com sucesso!")
                    st.subheader("Visualização dos Dados")
                    
                    # Exibir estatísticas
                    media_vento = serie_temporal['velocidade_vento'].mean()
                    max_vento = serie_temporal['velocidade_vento'].max()
                    min_vento = serie_temporal['velocidade_vento'].min()
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Velocidade Média", f"{media_vento:.2f} m/s")
                    col2.metric("Velocidade Máxima", f"{max_vento:.2f} m/s")
                    col3.metric("Velocidade Mínima", f"{min_vento:.2f} m/s")
                    
                    # Plotar gráfico
                    st.line_chart(serie_temporal.set_index('timestamp')['velocidade_vento'])
                    
                    # Atualizar velocidade média
                    st.session_state.vento_medio = media_vento
                    
                else:
                    st.warning("Não foi possível obter dados históricos para esta localidade.")
                    st.info("Você pode prosseguir com o cadastro usando valores teóricos.")

# Botão para salvar a localidade
st.header("Salvar Localidade")

if 'localidade' in st.session_state:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Clique no botão ao lado para salvar esta localidade no banco de dados.")
        st.write("Isso permitirá utilizar estes dados em simulações futuras.")
        
    with col2:
        if st.button("Salvar Localidade", type="primary"):
            try:
                # Criar instância com os dados atuais
                vento_api = VentoAPI(
                    local=st.session_state.localidade['nome'],
                    altura=altura,
                    topologia_terreno=topologia_selecionada,
                    latitude=st.session_state.localidade['latitude'],
                    longitude=st.session_state.localidade['longitude'],
                    vento_medio=st.session_state.get('vento_medio', vento_medio)
                )
                
                # Salvar no banco de dados
                resultado = vento_api.salvar_localidade()
                
                if resultado:
                    st.success(f"Localidade '{st.session_state.localidade['nome']}' salva com sucesso!")
                    # Adicionar botão para ir para a lista de localidades
                    st.write("Você pode [visualizar todas as localidades cadastradas](/wind_pages/listar_localidades).")
                else:
                    st.error("Erro ao salvar a localidade.")
                    
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")
else:
    st.info("Primeiro, busque ou informe os dados da localidade para poder salvá-la.")

# Informações adicionais
st.sidebar.markdown("---")
st.sidebar.info("""
## Sobre o Módulo
Este módulo permite cadastrar localidades para análise de potencial eólico.

As localidades cadastradas são salvas no banco de dados local 
e podem ser utilizadas nas simulações de potencial eólico.

Para instalar as dependências necessárias:
```
pip install streamlit pandas requests meteostat
```
""")