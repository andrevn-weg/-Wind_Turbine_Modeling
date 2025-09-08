from pathlib import Path
import streamlit as st
import os
import sys
import pandas as pd
from PIL import Image
import importlib


# Import CSS loader
from utils.css_loader import load_css


# Load centralized CSS
project_root = Path(__file__).parent.parent
css_path = os.path.join(project_root, "static", "styles.css")
load_css(css_path)

def main():
    
      # Título e subtítulo
    st.markdown("""
    <div class="page-main-header">
        <h1>
            <span style="color: #4CAF50; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: bold;">
                EolicSim
            </span>
            - Simulador de Potência Eólica
        </h1>
        <p>
            Sistema computacional para estimativa do potencial eólico de localidades, 
            integrando dados climáticos de APIs, modelos de correção de vento e características técnicas de aerogeradores 
            para análise e visualização interativa de resultados.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    


    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title"> OBJETIVOS DO PROJETO</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Objetivo geral
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">Objetivo Geral</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="detail-container">
    <p>Desenvolver um sistema computacional para estimativa do potencial eólico de uma localidade, 
    integrando dados climáticos obtidos por APIs, modelos de correção de velocidade do vento por altura 
    e características técnicas de aerogeradores, com interface interativa para análise e visualização dos resultados.</p>
    </div>
    """, unsafe_allow_html=True)
      # Objetivos específicos
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">✅ Objetivos Específicos</h4>
    </div>
    """, unsafe_allow_html=True)
    
    objectives = [
        "Revisar a literatura sobre energia eólica, perfis de vento e métodos de estimativa de potencial eólico.",
        "Implementar integração com APIs meteorológicas (Open-Meteo e NASA POWER) para coleta de dados históricos de vento.",
        "Aplicar modelos de correção de velocidade do vento por altura (Lei da Potência e Lei Logarítmica).",
        "Desenvolver um banco de dados relacional (SQLite) para armazenar localidades, dados climáticos e especificações de turbinas.",
        "Criar interface interativa em Streamlit para cadastro, consulta e análise de dados.",
        "Implementar algoritmos para estimativa de produção de energia com base em curvas de potência de aerogeradores.",
        "Validar o sistema por meio de estudo de caso com dados da cidade de Cachoeira do Sul (RS), incluindo ajuste da distribuição de Weibull e projeção de perfis de vento.",
        "Gerar relatórios e visualizações gráficas (curvas de potência, perfis de vento, estimativa de AEP) para suporte a estudos preliminares de viabilidade."
    ]
    
    text = None
    text = ""  # Initialize text as an empty string
    for i, obj in enumerate(objectives, 1):
        text += """<li style="padding: 10px 0; border-bottom: 1px solid #eee;">
                        <b>{i}.</b> {obj}
                    </li>
                """.format(i=i, obj=obj)
    st.markdown("""
    <div class="detail-container">
        <ul style="list-style-type: none; padding-left: 0;">
        {text}</ul>
    </div>
    """.format(text=text), unsafe_allow_html=True)
    
    
    
 
    

      # Seção de contexto
    st.markdown("""
    <div class="wind-info-card slide-in">
        <h4 class="wind-info-title">🌍 Contexto e Motivação</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="detail-container">
        <p> A crescente necessidade de geração de energia elétrica, impulsionada pelo aumento da população e 
        pela expansão econômica, evidencia a <b style="color: #db7b34;">urgência de soluções energéticas eficientes e sustentáveis</b>. 
        A energia eólica emerge como uma opção viável e necessária para atender à demanda crescente por eletricidade de 
        forma <b style="color: #db7b34;">ambientalmente responsável</b>. </p>
        <p> O Brasil tem uma matriz energética considerada uma das mais limpas do mundo, com cerca de 
        <b style="color: #db7b34;">83% da eletricidade proveniente de fontes renováveis</b>. A energia eólica representa aproximadamente 
        <b style="color: #db7b34;">10% da geração elétrica do país</b>, com capacidade instalada superior a <b style="color: #db7b34;">16 gigawatts</b>, e potencial para expansão 
        significativa, especialmente nas regiões <b style="color: #db7b34;">Nordeste e Sul</b>. </p>
        <p> Neste contexto, torna-se fundamental desenvolver <b style="color: #db7b34;">ferramentas computacionais</b> que permitam 
        <b style="color: #db7b34;">avaliar o potencial eólico de diferentes localidades</b> de forma precisa e acessível. A integração de 
        dados meteorológicos históricos, modelos de correção de vento e especificações técnicas de turbinas possibilita 
        <b style="color: #db7b34;">estudos preliminares de viabilidade</b> mais eficientes, contribuindo para o planejamento estratégico 
        e expansão sustentável da matriz energética eólica brasileira. </p>
    </div>
    """, unsafe_allow_html=True)
    






if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro ao iniciar aplicação: {e}")