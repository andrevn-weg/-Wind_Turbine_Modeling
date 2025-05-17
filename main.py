import streamlit as st
import os
import sys
import pandas as pd
from PIL import Image
import importlib

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Simulador de Turbina Eólica",
        page_icon="🌬️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar estilo personalizado
    st.markdown("""
    <style>
        .title {
            font-size: 36px !important;
            font-weight: bold;
        }
        .subtitle {
            font-size: 22px !important;
            font-style: italic;
            color: #4F4F4F;
        }
        .header {
            font-size: 24px !important;
            font-weight: bold;
            margin-top: 20px;
        }
        .subheader {
            font-size: 20px !important;
            font-weight: bold;
            margin-top: 10px;
        }
        hr {
            margin-top: 15px;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Título e subtítulo
    st.markdown('<p class="title">Simulador de Turbina Eólica de Velocidade Variável</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Modelagem e Análise de Componentes de Turbinas Eólicas</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar com menu de navegação
    st.sidebar.title("Navegação")
    
    opcoes = ["Início", "Cadastrar Localidade", "Listar Localidades", "Simulador de Turbina"]
    escolha = st.sidebar.radio("Selecione uma opção", opcoes)
    
    # Páginas baseadas na escolha
    if escolha == "Início":
        mostrar_pagina_inicial()
    elif escolha == "Cadastrar Localidade":
        abrir_cadastro_localidade()
    elif escolha == "Listar Localidades":
        abrir_listar_localidades()
    elif escolha == "Simulador de Turbina":
        abrir_simulador()
    
def mostrar_pagina_inicial():
    # Seção de objetivos
    st.markdown('<p class="header">Objetivos do Projeto</p>', unsafe_allow_html=True)
    
    # Objetivo geral
    st.markdown('<p class="subheader">Objetivo Geral:</p>', unsafe_allow_html=True)
    st.markdown(
        """
        Desenvolver um simulador de turbina eólica de velocidade variável, além de um sistema de supervisão
        que possibilite testar a turbina em diferentes regimes de vento e pontos de operação.
        """
    )
    
    # Objetivos específicos
    st.markdown('<p class="subheader">Objetivos Específicos:</p>', unsafe_allow_html=True)
    
    objectives = [
        "Revisão da literatura sobre sistemas de conversão eólica.",
        "Obtenção do perfil médio de vento em Cachoeira do Sul.",
        "Aquisição da série temporal do vento, incluindo turbulência e rajadas de vento.",
        "Desenvolvimento de um sistema de controle para uma turbina eólica de 20 kW, abrangendo desde a velocidade mínima de cut-in, técnica de MPPT, limitação de potência e cut-off.",
        "Implementação de uma plataforma de simulação que permita a modelagem e análise de todos os componentes de uma turbina eólica.",
        "Desenvolvimento de um sistema de supervisão utilizando Python.",
        "Avaliação do desempenho do sistema de emulação em diferentes cenários operacionais."
    ]
    
    for i, obj in enumerate(objectives, 1):
        st.markdown(f"{i}. {obj}")
    
    st.markdown("---")
    
    # Seção de contexto
    st.markdown('<p class="header">Contexto e Motivação</p>', unsafe_allow_html=True)
    
    context_text = (
        """
        A crescente necessidade de geração de energia elétrica, impulsionada pelo aumento da população e pela 
        expansão econômica, evidencia a urgência de soluções energéticas eficientes e sustentáveis. A energia 
        eólica emerge como uma opção viável e necessária para atender à demanda crescente por eletricidade de 
        forma ambientalmente responsável.

        O Brasil tem uma matriz energética considerada uma das mais limpas do mundo, com cerca de 83% da 
        eletricidade proveniente de fontes renováveis. A energia eólica representa aproximadamente 10% da 
        geração elétrica do país, com capacidade instalada superior a 16 gigawatts, e potencial para expansão 
        significativa, especialmente nas regiões Nordeste e Sul.

        Com investimentos substanciais tanto do setor público quanto do privado, o setor de energia eólica no 
        Brasil continua em expansão. Neste contexto, torna-se cada vez mais necessário desenvolver estudos para 
        prever e reduzir problemas no controle de turbinas, otimizando a qualidade da energia produzida através 
        do aprimoramento das técnicas de operação, controle de velocidade e limitação de potência.
        """
    )
    
    st.markdown(context_text)

def abrir_cadastro_localidade():
    st.title("Cadastrar Localidade")
    
    try:
        # Tentativa de importar o módulo de cadastro
        if os.path.exists("pages/cadastro_localidade.py"):
            modulo = importlib.import_module("pages.cadastro_localidade")
            modulo.show_streamlit()
        elif os.path.exists("pagess/wind_pages/cadastro_localidade.py"):
            modulo = importlib.import_module("pagess.wind_pages.cadastro_localidade")
            modulo.show_streamlit()
        else:
            st.error("Módulo de cadastro de localidade não encontrado.")
            st.info("Esta funcionalidade está em desenvolvimento.")
            
            # Interface básica para cadastro (placeholder)
            with st.form("cadastro_form"):
                nome = st.text_input("Nome da Localidade")
                latitude = st.number_input("Latitude", format="%.6f")
                longitude = st.number_input("Longitude", format="%.6f")
                notas = st.text_area("Observações")
                
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    st.success("Função de cadastro em implementação.")
                    
    except Exception as e:
        st.error(f"Erro ao carregar módulo de cadastro: {e}")

def abrir_listar_localidades():
    st.title("Listar Localidades")
    
    try:
        # Tentativa de importar o módulo de listagem
        if os.path.exists("pages/listar_localidades.py"):
            modulo = importlib.import_module("pages.listar_localidades")
            modulo.show_streamlit()
        elif os.path.exists("pagess/wind_pages/listar_localidades.py"):
            modulo = importlib.import_module("pagess.wind_pages.listar_localidades")
            modulo.show_streamlit()
        else:
            st.error("Módulo de listagem de localidades não encontrado.")
            st.info("Esta funcionalidade está em desenvolvimento.")
            
            # Dados de exemplo para exibição
            dados_exemplo = {
                "Nome": ["Cachoeira do Sul", "São Gabriel", "Santa Maria"],
                "Latitude": [-30.033056, -30.336389, -29.684722],
                "Longitude": [-52.892778, -54.322222, -53.806944],
                "Observações": ["Região central", "Oeste do estado", "Centro-oeste do estado"]
            }
            
            df = pd.DataFrame(dados_exemplo)
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"Erro ao carregar módulo de listagem: {e}")

def abrir_simulador():
    st.title("Simulador de Turbina Eólica")
    st.info("O módulo de simulação está em desenvolvimento.")
    
    # Exemplo de interface para o futuro simulador
    st.subheader("Parâmetros da Simulação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        velocidade = st.slider("Velocidade do Vento (m/s)", 0.0, 25.0, 10.0, 0.1)
        altura = st.slider("Altura da Medição (m)", 10.0, 150.0, 80.0, 5.0)
        turbulencia = st.slider("Índice de Turbulência (%)", 0, 30, 10)
    
    with col2:
        potencia = st.slider("Potência Nominal da Turbina (kW)", 5, 100, 20)
        diametro = st.slider("Diâmetro do Rotor (m)", 5, 50, 15)
        angulo_passo = st.slider("Ângulo de Passo (graus)", 0, 30, 0)
    
    if st.button("Iniciar Simulação"):
        st.warning("Funcionalidade ainda não implementada.")
        # Espaço para exibição de gráficos de simulação no futuro
        st.markdown("### Resultados da Simulação")
        
        # Placeholder para futuros gráficos
        st.line_chart({"Velocidade do Vento": [x*0.1+velocidade-1+x*x*0.01 for x in range(100)],
                      "Potência Gerada": [min(potencia, (x*0.1+velocidade-1+x*x*0.01)**3 * 0.2) for x in range(100)]})

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro ao iniciar aplicação: {e}")