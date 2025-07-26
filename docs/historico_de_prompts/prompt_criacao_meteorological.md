# Prompt para Desenvolvimento de Módulo Meteorológico
## Primeiro Passo
Analise o projeto e compreenda sua organização e estrutura, é um projeto desenvolvido em streamlit e banco de dados sqlite. Entenda a orginazação das pasta e dos arquivos.

## Contexto e Análise
O projeto conta atualmente com uma estrutura bem definida para dados geográficos, presente no módulo `src/geographic`, com as tabelas `paises`, `regioes` e `cidades`. Fiz algumas alterações recentemente e documentei o modelo de dados no arquivo `docs/estrutura_do_banco_de_dados.md`. Este arquivo reflete o estado atual e correto do banco de dados para o projeto.

## Nova Demanda
Seguindo o mesmo padrão e boas práticas já estabelecidas para o módulo geográfico, desenvolva o módulo meteorológico em `src/meteorological` com as seguintes características:

### Tabelas e Funcionalidade
- **meteorological_data_source**:  
  Tabela destinada a registrar as origens dos dados meteorológicos, como por exemplo "NASA_POWER".
- **meteorological_data**:  
  Tabela que irá armazenar as medições meteorológicas, principalmente velocidade do vento e altura de captura.

### Especificações e Requisitos

#### 1. CRUD
Implemente todos os módulos necessários (CRUD completo) para ambas as tabelas (`meteorological_data_source` e `meteorological_data`) no diretório `src/meteorological`.

#### 2. SQL com Relacionamentos
Inclua nas funções do CRUD de `meteorological_data` exemplos de comandos SQL que realizem consultas relacionadas a outras tabelas, especialmente:
- Consulta que retorne os dados meteorológicos juntamente com o nome da cidade, latitude e longitude.
- Outras junções úteis, como trazer a fonte dos dados junto com cada registro meteorológico.

#### 3. Exemplos e Testes
Na pasta `examples`, crie funções de exemplo e testes incluindo:
- Requisições (selects) exemplificando diferentes tipos de consultas.
- Inserções de dados de fontes e medições meteorológicas.
- Exemplos de atualização e remoção.
- Testes de integração entre as tabelas via SQL, demonstrando as relações entre cidade, fonte e dado meteorológico.

## Observações
- Certifique-se de seguir o padrão de código, nomenclatura e modularização já adotados em `src/geographic`.
- Utilize como referência a documentação em `docs/estrutura_do_banco_de_dados.md` para garantir aderência ao modelo de dados atualizado.
- Nas queries SQL, priorize a legibilidade e a facilidade para integrações futuras.

### Resumo esperado do que será entregue:
- CRUD completo para `meteorological_data_source` e `meteorological_data` em `src/meteorological`.
- Exemplo de queries relacionando dados meteorológicos com cidades e fontes.
- Arquivos de exemplo e teste práticos em `examples`.