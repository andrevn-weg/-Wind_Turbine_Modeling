import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from models.vento import Vento
from models.wind_models.vento_api import VentoAPI

# Configurar o título e layout da página
st.set_page_config(page_title="Emulação de Vento - TCC", layout="wide")
st.title("Emulação de Vento para Potencial Eólico")

# Sidebar para parâmetros de entrada
st.sidebar.header("Parâmetros de Entrada")

# Localização
local = st.sidebar.text_input("Localização (cidade ou região)")

# Velocidade média (opcional)
usar_vento_manual = st.sidebar.checkbox("Definir velocidade média manualmente")
vento_medio = None
if usar_vento_manual:
    vento_medio = st.sidebar.slider("Velocidade média do vento (m/s)", 
                                   min_value=1.0, max_value=15.0, value=6.5, step=0.1)

# Altura da turbina
altura = st.sidebar.slider("Altura da turbina (m)", 
                          min_value=10, max_value=150, value=50, step=5)

# Período de simulação
periodo = st.sidebar.slider("Período de simulação (horas)", 
                           min_value=24, max_value=720, value=168, step=24)

# Topologia do terreno
topologias = list(Vento.topologia.keys())
topologia_selecionada = st.sidebar.selectbox("Topologia do terreno", options=topologias)

# Verificar se há localidades salvas para usar
try:
    localidades_salvas = VentoAPI.listar_localidades()
    if localidades_salvas:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Localidades Salvas")
        nomes_localidades = [loc["nome"] for loc in localidades_salvas]
        usar_salva = st.sidebar.checkbox("Usar localidade salva", key="usar_loc_salva")
        
        if usar_salva:
            loc_selecionada = st.sidebar.selectbox("Selecione a localidade", options=nomes_localidades)
            # Encontrar os dados da localidade selecionada
            loc_dados = next((loc for loc in localidades_salvas if loc["nome"] == loc_selecionada), None)
            
            if loc_dados:
                # Atualizar os campos com os dados da localidade selecionada
                local = loc_dados["nome"]
                if "velocidade_media" in loc_dados and loc_dados["velocidade_media"]:
                    vento_medio = loc_dados["velocidade_media"]
except Exception as e:
    # Em caso de erro, apenas continua sem exibir localidades salvas
    pass

# Botão para gerar simulação
gerar = st.sidebar.button("Gerar Simulação", type="primary")

# Instancia a classe Vento (para acesso às informações mesmo sem gerar)
vento = Vento(local=local, altura=altura, periodo=periodo, 
              vento_medio=vento_medio, topologia_terreno=topologia_selecionada)

# Mostrar informações básicas
st.header("Informações do Cenário")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Localização e Vento")
    if local:
        st.write(f"**Local selecionado:** {local}")
    else:
        st.write("**Local:** Não especificado")
    
    st.write(f"**Velocidade média do vento:** {vento.vento_medio:.2f} m/s")
    if not usar_vento_manual and local:
        if local in vento.dados_locais:
            st.write("(Dados obtidos do banco de dados local)")
        else:
            st.write("(Utilizando valor médio padrão para o Brasil)")
    elif usar_vento_manual:
        st.write("(Valor definido manualmente)")

with col2:
    st.subheader("Parâmetros da Simulação")
    st.write(f"**Altura da turbina:** {altura} m")
    st.write(f"**Período de simulação:** {periodo} horas")
    st.write(f"**Topologia do terreno:** {topologia_selecionada}")
    st.write(f"**Rugosidade do terreno (Lei Logarítmica):** {vento.topologia_terreno['Lei Logarítmica']/1000:.5f} m")
    st.write(f"**Expoente da potência (Lei da Potência):** {vento.topologia_terreno['Lei da Potencia']:.2f}")

# Quando o botão for clicado
if gerar:
    st.header("Resultados da Simulação")
    
    # Gerar a série temporal e calcular o potencial eólico
    with st.spinner("Gerando série temporal e calculando potencial eólico..."):
        serie_temporal, potencial_eolico = vento.gerar_serie_temporal()
    
    # Exibir informações sobre o potencial eólico
    st.subheader("Potencial Eólico")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Potencial Eólico Médio", value=f"{potencial_eolico:.2f} W/m²")
    
    with col2:
        # Calcular o potencial máximo
        potencial_max = serie_temporal['potencial_eolico'].max()
        st.metric(label="Potencial Eólico Máximo", value=f"{potencial_max:.2f} W/m²")
    
    with col3:
        # Estimar energia anual por m²
        energia_anual = potencial_eolico * 8760 / 1000  # kWh/m²/ano
        st.metric(label="Energia Anual Estimada", value=f"{energia_anual:.2f} kWh/m²/ano")
    
    # Gráfico da série temporal
    st.subheader("Série Temporal do Vento")
    
    fig, ax = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
    
    # Gráfico da velocidade do vento
    ax[0].plot(serie_temporal['timestamp'], serie_temporal['velocidade_vento'], linewidth=1)
    ax[0].set_title('Velocidade do Vento')
    ax[0].set_ylabel('Velocidade (m/s)')
    ax[0].grid(True)
    
    # Gráfico do potencial eólico
    ax[1].plot(serie_temporal['timestamp'], serie_temporal['potencial_eolico'], 
               linewidth=1, color='orange')
    ax[1].set_title('Potencial Eólico')
    ax[1].set_xlabel('Tempo')
    ax[1].set_ylabel('Potência (W/m²)')
    ax[1].grid(True)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Estatísticas da série temporal
    st.subheader("Estatísticas da Série Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Velocidade do Vento**")
        stats_vento = serie_temporal['velocidade_vento'].describe()
        st.write(f"- Média: {stats_vento['mean']:.2f} m/s")
        st.write(f"- Mínima: {stats_vento['min']:.2f} m/s")
        st.write(f"- Máxima: {stats_vento['max']:.2f} m/s")
        st.write(f"- Desvio Padrão: {stats_vento['std']:.2f} m/s")
    
    with col2:
        st.write("**Potencial Eólico**")
        stats_potencial = serie_temporal['potencial_eolico'].describe()
        st.write(f"- Média: {stats_potencial['mean']:.2f} W/m²")
        st.write(f"- Mínima: {stats_potencial['min']:.2f} W/m²")
        st.write(f"- Máxima: {stats_potencial['max']:.2f} W/m²")
        st.write(f"- Desvio Padrão: {stats_potencial['std']:.2f} W/m²")
    
    # Mostrar perfil vertical do vento
    st.subheader("Perfil Vertical do Vento")
    
    # Gerar gráfico com as leis de potência e logarítmica
    fig_leis = plt.figure(figsize=(10, 6))
    plt_leis = vento.Grafico_Vel_Vento_Estipulado(LeiPotencia=True, LeiLogaritmica=True)
    st.pyplot(fig_leis)
    
    # Download dos dados
    st.subheader("Exportar Dados")
    
    # Converter para CSV para download
    csv = serie_temporal.to_csv(index=False)
    st.download_button(
        label="Download da Série Temporal (CSV)",
        data=csv,
        file_name=f"serie_temporal_vento_{local}_{altura}m.csv",
        mime="text/csv",
    )
    
    # Mostrar os primeiros registros da série temporal
    st.subheader("Visualização dos Dados")
    st.dataframe(serie_temporal.head(100))

# Adicionar seção para gerenciamento de localidades 
st.sidebar.markdown("---")
st.sidebar.header("Gerenciamento de Localidades")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.sidebar.button("Cadastrar Nova Localidade", key="btn_cadastrar"):
        st.switch_page("pages/cadastro_localidade.py")
with col2:
    if st.sidebar.button("Listar Localidades", key="btn_listar"):
        st.switch_page("pages/listar_localidades.py")

# Adicionar informações sobre o projeto
st.sidebar.markdown("---")
st.sidebar.info("""
## Sobre o Projeto
Este aplicativo faz parte do Trabalho de Conclusão de Curso sobre Emulação de Turbinas Eólicas.

A interface permite simular o comportamento do vento em diferentes localidades e alturas,
calculando seu potencial eólico e gerando séries temporais.

Agora também é possível cadastrar localidades e armazenar seus dados para uso futuro!
""")

# Verifique se o diretório de banco de dados existe e crie-o se necessário
database_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)