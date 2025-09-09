# Sistema de Simulação de Turbinas Eólicas - EolicSim

Plataforma de simulação e análise para turbinas eólicas desenvolvida como Trabalho de Conclusão de Curso em Engenharia Elétrica. O sistema integra dados meteorológicos reais, modelagem de turbinas e análises de viabilidade para projetos eólicos.

## Principais Funcionalidades

### Gestão Geográfica
- Cadastro de países, regiões e cidades
- Base de dados geográficos integrada
- Coordenadas GPS para localização

### Dados Meteorológicos
- Integração com APIs meteorológicas (OpenMeteo, NASA Power)
- Histórico de dados de vento, temperatura e umidade
- Análise de séries temporais meteorológicas

### Parâmetros de Turbinas
- Banco de dados de fabricantes e modelos
- Especificações técnicas (potência, diâmetro, velocidades)
- Curvas de potência e coeficientes aerodinâmicos

### Análises Avançadas
- Perfil Vertical do Vento: Lei de Potência e Lei Logarítmica
- Simulação de Componentes: Vento médio, ondas e turbulência
- Análise de Performance: Fator de capacidade, disponibilidade
- Relatórios Técnicos: Viabilidade e recomendações

### Análise Simplificada
- Interface para análises rápidas
- Geração automática de relatórios
- Exportação em CSV e Excel
- Análises por período (diária, mensal, semanal, horária)
- Correlações entre variáveis meteorológicas

## Estrutura do Projeto

```
EolicSim/
├── src/                          # Código principal
│   ├── analysis_tools/           # Ferramentas de análise científica
│   ├── core/                     # Núcleo da aplicação
│   ├── database/                 # Configuração do banco de dados
│   ├── geographic/               # Gestão geográfica (países, regiões, cidades)
│   ├── meteorological/           # Dados meteorológicos e APIs
│   ├── turbine_parameters/       # Parâmetros e modelos de turbinas
│   ├── utils/                    # Utilitários compartilhados
│   └── web/                      # Interface web (Streamlit)
│       ├── pages/                # Páginas da aplicação
│       │   ├── analysis/         # Sistema de análise completo
│       │   └── turbine_parameters_pages/ # Gestão de turbinas
│       └── static/               # Arquivos estáticos (CSS, imagens)
├── docs/                         # Documentação técnica
├── examples/                     # Scripts de exemplo e testes
├── data/                         # Base de dados SQLite
└── main.py                       # Arquivo principal da aplicação
```

## Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- Git

### Instalação
```bash
# Clonar o repositório
git clone https://github.com/andrevn-weg/-Wind_Turbine_Modeling.git
cd Wind_Turbine_Modeling

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run main.py
```

### Acesso à Aplicação
Após executar, acesse: `http://localhost:8501`

## Tecnologias Utilizadas

### Backend
- Python 3.8+ - Linguagem principal
- SQLite - Banco de dados
- Pandas & NumPy - Manipulação e análise de dados
- SciPy - Computação científica

### Frontend
- Streamlit - Framework web para aplicações de dados
- Plotly - Visualizações interativas
- CSS customizado - Interface responsiva

### APIs e Integrações
- OpenMeteo API - Dados meteorológicos globais
- NASA Power API - Dados climáticos satelitais
- Requests & HTTPX - Cliente HTTP

### Análise e Visualização
- Matplotlib & Seaborn - Gráficos estatísticos
- OpenPyXL - Exportação para Excel
- GeoPy - Processamento geográfico

## Como Usar

### 1. Configuração Inicial
- Configure países, regiões e cidades no sistema
- Cadastre fabricantes e modelos de turbinas
- Colete dados meteorológicos históricos

### 2. Análise Simplificada (Recomendado para iniciantes)
- Acesse a página "Análise Simplificada"
- Selecione localidade e turbina do banco de dados
- Configure período de análise
- Visualize resultados e baixe relatórios

### 3. Análise Completa (Para usuários avançados)
- Acesse o sistema de análise em etapas
- Configure parâmetros iniciais detalhados
- Execute análises de perfil de vento
- Simule componentes e turbinas
- Gere relatórios técnicos completos

## Exemplos de Análises

### Análise de Viabilidade
- Fator de capacidade da turbina
- Energia gerada por período
- Disponibilidade operacional
- Condições de vento estatísticas

### Análises Temporais
- Geração por hora do dia
- Padrões semanais e mensais
- Sazonalidade do recurso eólico
- Correlações meteorológicas

### Relatórios Técnicos
- Resumo executivo do projeto
- Especificações técnicas completas
- Recomendações de viabilidade
- Dados para download

## Contexto Acadêmico

### Trabalho de Conclusão de Curso (TCC II)
**Título:** "Emulação de Turbinas Eólicas: Desenvolvimento de Plataforma Integrada para Simulação e Análise de Viabilidade"

**Resumo:** Este trabalho apresenta o desenvolvimento de uma plataforma computacional integrada para simulação e análise de turbinas eólicas, combinando dados meteorológicos reais, modelagem aerodinâmica e análises de viabilidade técnico-econômica. O sistema EolicSim permite avaliar o potencial eólico de localidades, simular o comportamento de diferentes modelos de turbinas e gerar relatórios técnicos detalhados para suporte à tomada de decisão em projetos de energia eólica.

### Informações Acadêmicas
- **Autor:** André Vinícius Lima do Nascimento
- **Orientador:** Prof. Dr. Gustavo Guilherme Koch
- **Instituição:** Universidade Federal de Santa Maria (UFSM)
- **Campus:** Cachoeira do Sul
- **Curso:** Engenharia Elétrica
- **Ano:** 2024/2025

### Objetivos do Projeto
- Desenvolver uma plataforma integrada para análise eólica
- Implementar modelos matemáticos para simulação de turbinas
- Integrar dados meteorológicos reais via APIs
- Criar interface para análises técnicas
- Gerar relatórios de viabilidade automatizados

## Status do Projeto

- Gestão Geográfica - Completo
- Dados Meteorológicos - Completo
- Parâmetros de Turbinas - Completo
- Análise Simplificada - Completo
- Sistema de Análise Completo - Completo
- Relatórios e Downloads - Completo
- Interface Responsiva - Completo

## Contribuindo

Este projeto é parte de um TCC acadêmico. Sugestões e melhorias são bem-vindas através de issues e pull requests.

## Licença

Este projeto é desenvolvido para fins acadêmicos como parte do TCC de Engenharia Elétrica da UFSM.

## Contato

- Email: andre.nascimento@acad.ufsm.br
- LinkedIn: https://www.linkedin.com/in/andre-vinicius-lima/
- Orientador: Prof. Dr. Gustavo Guilherme Koch - UFSM

---
*Projeto desenvolvido para a energia eólica brasileira*