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
            Plataforma para análise, modelagem e simulação estatística da geração eólica, 
            permitindo avaliar o desempenho de turbinas em diferentes condições de vento e cenários operacionais.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    


    st.markdown("""
    <div class="section-header">
        <h4>🎯 Objetivos do Projeto</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Objetivo geral
    st.markdown("""
    <div class="section-header-minor">
        <h4>Objetivo Geral</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="detail-container">
    <p>Desenvolver um simulador de turbina eólica de velocidade variável, além de um sistema de supervisão
    que possibilite testar a turbina em diferentes regimes de vento e pontos de operação.</p>
    </div>
    """, unsafe_allow_html=True)
      # Objetivos específicos
    st.markdown("""
    <div class="thermal-section">
        <h4>Objetivos Específicos</h4>
    </div>
    """, unsafe_allow_html=True)
    
    objectives = [
        "Revisão da literatura sobre sistemas de conversão eólica.",
        "Obtenção do perfil médio de vento em Cachoeira do Sul.",
        "Aquisição da série temporal do vento, incluindo turbulência e rajadas de vento.",
        "Desenvolvimento de um sistema de controle para uma turbina eólica de 20 kW, abrangendo desde a velocidade mínima de cut-in, técnica de MPPT, limitação de potência e cut-off.",
        "Implementação de uma plataforma de simulação que permita a modelagem e análise de todos os componentes de uma turbina eólica.",
        "Desenvolvimento de um sistema de supervisão utilizando Python.",
        "Avaliação do desempenho do sistema de emulação em diferentes cenários operacionais."
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
    <div class="section-header">
        <h4>🌍 Contexto e Motivação</h4>
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
        <p> Com investimentos substanciais tanto do setor público quanto do privado, o setor de energia eólica no 
        Brasil continua em expansão. Neste contexto, torna-se cada vez mais necessário desenvolver estudos para 
        <b style="color: #db7b34;">prever e reduzir problemas no controle de turbinas</b>, otimizando a qualidade da energia produzida através 
        do aprimoramento das técnicas de <b style="color: #db7b34;">operação, controle de velocidade e limitação de potência</b>. </p>
    </div>
    """, unsafe_allow_html=True)
    






if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro ao iniciar aplicação: {e}")