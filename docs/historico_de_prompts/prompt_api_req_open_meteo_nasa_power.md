# Prompt para criação dos módulos de requisição às APIs meteorológicas

## Contexto
O objetivo é criar integrações automatizadas para obtenção de dados históricos de velocidade do vento utilizando as APIs do **Open-Meteo** e **NASA POWER**. Os códigos devem ser criados na pasta `src/meteorological/api`, e exemplos de uso devem ser incluídos na pasta `examples`. Os exemplos **não** devem realizar inserção no banco de dados.

---

## Especificações

**1. Localização dos códigos**
- Os clientes (códigos para requisição) devem ser implementados em `src/meteorological/api/`:
  - `open_meteo.py`
  - `nasa_power.py`

**2. Foco das requisições**
- Apenas dados históricos de velocidade do vento.
- As requisições devem ser horárias (`hourly`) para o período especificado.
- O período padrão das requisições deve ser de **um ano** retroativo a partir da data atual ou podendo ser o ano completo (Ex.: 01/01/2024 a 31/12/2024 para o ano de 2024), podendo ser parametrizado.
  
**3. Limitações de altura**
- **NASA POWER:** somente alturas de 10 metros e 50 metros.
  - Se o usuário tentar solicitar outra altura, deve ser lançado um erro ou alerta.
- **Open-Meteo:** alturas de 10m, 80m, 120m e 180m.
  - Se o usuário solicitar altura não suportada, deve ser lançado erro ou alerta.
- Quero que essas informações de limitação estejam como comentário no início do código.

**4. Interface dos métodos**
- Neste momento, **não é necessário definir uma interface única ou padronizada**. O foco será apenas na implementação dos métodos para requisição dos dados históricos.
- Os métodos devem retornar os dados em formato estruturado (ex: dicionário ou objeto Python).

**5. Códigos de exemplo**
- Na pasta `examples/`, criar:
  - `example_open_meteo.py`: Exemplo de requisição utilizando cidades do banco de dados (com latitude e longitude já armazenadas), fazendo requisições para as quatro alturas disponíveis de uma só vez, para cada cidade, exibindo os dados obtidos.
  - `example_nasa_power.py`: Exemplo de requisição utilizando cidades do banco de dados, fazendo requisições para ambas as alturas disponíveis (10m e 50m) de uma só vez, para cada cidade, exibindo os dados obtidos.
- Os exemplos **NÃO** devem gravar dados no banco, apenas exibir ou salvar em arquivo local (opcional).
- Os exemplos devem demonstrar a busca otimizada, requisitando todos os dados disponíveis para cada cidade em uma única chamada para cada serviço.

**6. Documentação e mensagens**
- Incluir docstrings explicando as limitações de cada API e informando as alturas suportadas.
- Incluir tratamento de erro e mensagens explicativas caso o usuário solicite altura não suportada.

---

## Resumo esperado
- `src/meteorological/api/open_meteo.py`: Cliente para a API Open-Meteo, respeitando alturas e parâmetros definidos.
- `src/meteorological/api/nasa_power.py`: Cliente para a API NASA POWER, respeitando alturas e parâmetros definidos.
- `examples/example_open_meteo.py`: Exemplo de requisição para cidades do banco, exibindo dados para todas as alturas disponíveis.
- `examples/example_nasa_power.py`: Exemplo de requisição para cidades do banco, exibindo dados para ambas as alturas disponíveis.

---
**Observação:** Não realizar inserção no banco de dados nos exemplos.