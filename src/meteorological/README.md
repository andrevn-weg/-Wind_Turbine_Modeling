# Módulo Meteorológico - Sistema de Simulação de Turbinas Eólicas

## 📋 Visão Geral

O módulo meteorológico implementa funcionalidades completas para gerenciamento de dados meteorológicos, incluindo fontes de dados e medições meteorológicas. Foi desenvolvido seguindo os mesmos padrões e arquitetura do módulo geográfico, garantindo consistência e qualidade do código.

## 🏗️ Arquitetura

O módulo segue a arquitetura **Entity-Repository**, separando claramente as responsabilidades:

```
src/meteorological/
├── __init__.py                          # Módulo principal
├── meteorological_data_source/          # Fontes de dados meteorológicos
│   ├── __init__.py
│   ├── entity.py                        # Entidade MeteorologicalDataSource
│   └── repository.py                    # Repositório com CRUD completo
└── meteorological_data/                 # Dados meteorológicos
    ├── __init__.py
    ├── entity.py                        # Entidade MeteorologicalData
    └── repository.py                    # Repositório com CRUD e consultas relacionais
```

## 📊 Modelo de Dados

### Tabela: `meteorological_data_source`
Armazena informações sobre as fontes de dados meteorológicos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER (PK) | Identificador único |
| `name` | VARCHAR (UNIQUE) | Nome da fonte (ex: NASA_POWER, INMET) |
| `description` | VARCHAR | Descrição detalhada da fonte |

### Tabela: `meteorological_data`
Armazena as medições meteorológicas coletadas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER (PK) | Identificador único |
| `meteorological_data_source_id` | INTEGER (FK) | Referência à fonte dos dados |
| `cidade_id` | INTEGER (FK) | Referência à cidade |
| `data` | DATE | Data da medição |
| `altura_captura` | FLOAT | Altura de captura do vento (metros) |
| `velocidade_vento` | FLOAT | Velocidade do vento (m/s) |
| `temperatura` | FLOAT | Temperatura (°C) |
| `umidade` | FLOAT | Umidade relativa (%) |
| `created_at` | TIMESTAMP | Timestamp de criação |

## 🚀 Funcionalidades Implementadas

### ✅ CRUD Completo
- **Fontes de Dados**: Criar, ler, atualizar e deletar fontes meteorológicas
- **Dados Meteorológicos**: Gerenciamento completo de medições meteorológicas
- **Validações**: Verificações de integridade de dados e regras de negócio

### ✅ Consultas Relacionais Avançadas
- Dados meteorológicos com informações geográficas completas
- Estatísticas de vento por cidade e região
- Análise temporal de dados meteorológicos
- Comparação entre diferentes fontes de dados

### ✅ Análise de Viabilidade Eólica
- Classificação de velocidade do vento (Escala de Beaufort)
- Cálculo de potencial eólico por localização
- Correção de altura para turbinas eólicas
- Estimativa de fator de capacidade e geração de energia

### ✅ Validações e Classificações
- Validação de dados meteorológicos
- Classificação automática de ventos
- Verificação de ranges válidos para temperatura, umidade e velocidade
- Detecção de dados disponíveis por tipo

## 📚 Exemplos de Uso

### Importação Básica
```python
from meteorological import (
    MeteorologicalDataSource, MeteorologicalDataSourceRepository,
    MeteorologicalData, MeteorologicalDataRepository
)
```

### Criando uma Fonte de Dados
```python
# Criar repositório
fonte_repo = MeteorologicalDataSourceRepository()

# Criar fonte
fonte = MeteorologicalDataSource(
    name="NASA_POWER",
    description="NASA Prediction of Worldwide Energy Resources"
)

# Salvar no banco
fonte_id = fonte_repo.salvar(fonte)
```

### Adicionando Dados Meteorológicos
```python
from datetime import date

# Criar repositório
dados_repo = MeteorologicalDataRepository()

# Criar dados meteorológicos
dados = MeteorologicalData(
    meteorological_data_source_id=fonte_id,
    cidade_id=1,
    data=date.today(),
    altura_captura=50.0,
    velocidade_vento=7.5,
    temperatura=25.0,
    umidade=65.0
)

# Salvar no banco
dados_id = dados_repo.salvar(dados)
```

### Consultas Relacionais
```python
# Buscar dados com informações geográficas
dados_completos = dados_repo.buscar_com_detalhes_cidade(limite=10)

for dados in dados_completos:
    print(f"Data: {dados['data']}")
    print(f"Cidade: {dados['cidade_nome']}, {dados['regiao_nome']}")
    print(f"Coordenadas: {dados['latitude']}, {dados['longitude']}")
    print(f"Vento: {dados['velocidade_vento']} m/s")
    print(f"Fonte: {dados['fonte_nome']}")
```

### Análise de Viabilidade Eólica
```python
# Calcular estatísticas de vento
stats = dados_repo.buscar_estatisticas_vento_por_cidade(cidade_id=1)

print(f"Total de registros: {stats['total_registros']}")
print(f"Velocidade média: {stats['velocidade_media']:.2f} m/s")
print(f"Velocidade máxima: {stats['velocidade_maxima']:.2f} m/s")

# Classificar vento
dados = MeteorologicalData(velocidade_vento=8.5)
classificacao = dados.classificar_vento()
print(f"Classificação: {classificacao}")  # Ex: "Vento fresco"
```

## 🧪 Scripts de Exemplo

O módulo inclui scripts completos de demonstração e teste:

### `examples/migrate_meteorological.py`
Script de migração que cria as tabelas e popula dados básicos.

```bash
python examples/migrate_meteorological.py
```

### `examples/3_meteorological_complete.py`
Demonstração completa de todas as funcionalidades do módulo.

```bash
python examples/3_meteorological_complete.py
```

### `examples/4_meteorological_integration.py`
Exemplo de integração com dados reais e análise de viabilidade eólica.

```bash
python examples/4_meteorological_integration.py
```

### `examples/test_meteorological.py`
Suite de testes completa para validar todas as funcionalidades.

```bash
python examples/test_meteorological.py
```

## 🔍 Consultas SQL Avançadas

### Dados Meteorológicos com Informações Geográficas
```sql
SELECT 
    md.data, md.velocidade_vento, md.temperatura,
    c.nome as cidade_nome, c.latitude, c.longitude,
    r.nome as regiao_nome, p.nome as pais_nome,
    mds.name as fonte_nome
FROM meteorological_data md
JOIN cidades c ON md.cidade_id = c.id
LEFT JOIN regioes r ON c.regiao_id = r.id
LEFT JOIN paises p ON c.pais_id = p.id
JOIN meteorological_data_source mds ON md.meteorological_data_source_id = mds.id
ORDER BY md.data DESC;
```

### Estatísticas de Vento por Cidade
```sql
SELECT 
    c.nome as cidade,
    COUNT(*) as total_registros,
    AVG(md.velocidade_vento) as velocidade_media,
    MAX(md.velocidade_vento) as velocidade_maxima,
    MIN(md.velocidade_vento) as velocidade_minima
FROM meteorological_data md
JOIN cidades c ON md.cidade_id = c.id
WHERE md.velocidade_vento IS NOT NULL
GROUP BY c.id, c.nome
ORDER BY velocidade_media DESC;
```

### Dados Recentes por Região
```sql
SELECT 
    md.data, md.velocidade_vento, md.temperatura,
    c.nome as cidade_nome,
    mds.name as fonte_nome
FROM meteorological_data md
JOIN cidades c ON md.cidade_id = c.id
JOIN meteorological_data_source mds ON md.meteorological_data_source_id = mds.id
WHERE c.regiao_id = ? 
AND md.data >= date('now', '-30 days')
ORDER BY md.data DESC, c.nome;
```

## 🛠️ Configuração e Instalação

### Pré-requisitos
- Python 3.x
- SQLite3 (incluído no Python)
- Módulo geográfico configurado

### Configuração
1. Execute a migração para criar as tabelas:
```bash
python examples/migrate_meteorological.py
```

2. Teste a instalação:
```bash
python examples/test_meteorological.py
```

3. Execute exemplos completos:
```bash
python examples/3_meteorological_complete.py
python examples/4_meteorological_integration.py
```

## 📈 Análise de Viabilidade Eólica

O módulo inclui funcionalidades avançadas para análise de viabilidade eólica:

### Classificação de Velocidade do Vento
Baseada na Escala de Beaufort:
- **0-0.3 m/s**: Calmo
- **0.3-1.6 m/s**: Brisa leve  
- **1.6-3.4 m/s**: Brisa fraca
- **3.4-5.5 m/s**: Brisa moderada
- **5.5-8.0 m/s**: Brisa forte
- **8.0-10.8 m/s**: Vento fresco
- **10.8+ m/s**: Vento forte/Ventania

### Correção de Altura
Utiliza a lei de potência para correção da velocidade do vento:
```
V2 = V1 × (H2/H1)^α
```
Onde α ≈ 0.2 para terrenos abertos.

### Cálculo de Potencial Energético
Estima o potencial de geração baseado em:
- Velocidade média do vento corrigida para altura da turbina
- Distribuição de velocidades
- Fator de capacidade estimado
- Energia anual estimada (MWh)

## 🔧 Manutenção e Operações

### Limpeza de Dados
```python
# Remover dados antigos por período
dados_repo = MeteorologicalDataRepository()
removidos = dados_repo.excluir_por_cidade_e_periodo(
    cidade_id=1,
    data_inicio=date(2023, 1, 1),
    data_fim=date(2023, 12, 31)
)
```

### Verificação de Integridade
```python
# Validar dados antes de salvar
dados = MeteorologicalData(...)
if dados.validar():
    dados_repo.salvar(dados)
else:
    print("Dados inválidos!")
```

### Monitoramento
```python
# Verificar estatísticas gerais
todas_fontes = fonte_repo.listar_todos()
todos_dados = dados_repo.listar_todos(limite=1000)

print(f"Fontes cadastradas: {len(todas_fontes)}")
print(f"Registros meteorológicos: {len(todos_dados)}")
```

## 🎯 Próximos Passos

1. **Interface Web**: Criar páginas Streamlit para visualização de dados meteorológicos
2. **APIs Externas**: Implementar clientes para APIs como Open-Meteo e NASA POWER
3. **Relatórios**: Gerar relatórios automáticos de viabilidade eólica
4. **Visualizações**: Gráficos e mapas interativos dos dados meteorológicos
5. **Exportação**: Funcionalidades de export para CSV, JSON e outros formatos

## 📝 Contribuição

Para contribuir com o módulo meteorológico:

1. Siga os padrões estabelecidos na arquitetura Entity-Repository
2. Adicione testes para novas funcionalidades
3. Mantenha a documentação atualizada
4. Execute os testes existentes antes de submeter alterações

---

**Desenvolvido como parte do projeto de TCC - Sistema de Simulação de Turbinas Eólicas**  
**Autor:** André Vinícius Lima do Nascimento  
**Orientador:** Prof. Dr. Gustavo Guilherme Koch  
**Instituição:** UFSM - Campus Cachoeira do Sul
