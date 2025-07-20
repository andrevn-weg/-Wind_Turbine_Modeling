# Prompt para Implementação do Módulo Climate

## Contexto do Projeto

O sistema de simulação de turbinas eólicas encontra-se com arquitetura modular, moderna e funcional, utilizando **Streamlit** para o frontend, **Python** no backend e **SQLite** como banco de dados.  
O módulo geographic está totalmente implementado e a estrutura para o módulo climate já foi criada, aguardando desenvolvimento.

---

## Objetivo

Implementar o **módulo climate** conforme as melhores práticas do projeto, garantindo integração eficiente com as entidades geográficas já implementadas e aproveitando a base sólida atual.

---

## Requisitos Técnicos e Funcionais

1. **Modelagem de Dados Climáticos**
    - Crie entidades para dados climáticos: `DadosClimaticos`, `HistoricoVento`, `LocalizacaoClimatica`, seguindo o padrão entity/repository já utilizado.
    - Garanta que a modelagem permita armazenar e consultar séries temporais de vento de forma eficiente no banco SQLite.

2. **Integração com APIs Meteorológicas**
    - Implemente clientes para obtenção de dados de vento, priorizando a integração com [power.larc.nasa.gov](https://power.larc.nasa.gov) e/ou Open-Meteo.
    - Estruture as funções de API para facilitar futuras expansões para outras fontes de dados.

3. **Serviços de Processamento de Dados**
    - Desenvolva serviços para análise estatística, cálculo de potencial eólico e processamento de séries temporais.
    - Utilize Pandas, NumPy e outras bibliotecas do projeto para garantir eficiência.

4. **Interface Web (Streamlit)**
    - Crie páginas web para:
        - Vinculação de cidades já cadastradas e configuração dos parâmetros de consulta dos dados de vento.
        - Análise dos dados climáticos obtidos (visualizações, gráficos, mapas, estatísticas).
    - Organize o código em subpastas conforme função: api, models, services, pages, componentes, etc.
    - Mantenha o padrão de navegação por abas e interface moderna já adotados.

5. **Integração com Banco de Dados**
    - Assegure que a persistência dos dados climáticos e de vento seja eficiente e compatível com o SQLite, aproveitando os repositórios existentes.
    - Garanta a relação dos dados climáticos com as entidades geográficas cadastradas.

6. **Documentação e Demonstração**
    - Documente a arquitetura, modelos e fluxos de dados do módulo climate.
    - Implemente exemplos funcionais e scripts de teste para validação do módulo.

---

## Foco Acadêmico

- Demonstre evolução técnica, clareza na separação de responsabilidades, uso de tecnologias atuais e integração eficiente de dados reais para análise e simulação de turbinas eólicas.

---

## Referências

- Estrutura de diretórios já criada em `src/climate/`
- Exemplo funcional disponível em `examples/1_historico_vento.py`
- Banco de dados operacional em `data/wind_turbine.db`

---

## Roadmap

1. Modelagem (Entidades e Repositórios)
2. APIs (power.larc.nasa.gov/Open-Meteo)
3. Serviços de análise
4. Páginas Streamlit
5. Testes e documentação