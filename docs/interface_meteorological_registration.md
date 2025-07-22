# Interface de Cadastro de Dados Meteorológicos

Esta documentação descreve como usar a nova interface de cadastro de dados meteorológicos implementada no sistema de simulação de turbinas eólicas.

## 📁 Estrutura Criada

```
src/web/pages/
├── meteorological_registration.py           # Página principal
└── meteorological_registration/             # Subpáginas
    ├── __init__.py
    ├── create_meteorological_data_source.py # Cadastro de fontes
    └── create_meteorological_data.py        # Cadastro de dados
```

## 🚀 Como Executar

### Método 1: Via Streamlit direto
```bash
streamlit run src/web/pages/meteorological_registration.py
```

### Método 2: Navegar pelo sistema
1. Execute a aplicação principal do Streamlit
2. Navegue até a página "Cadastro de Dados Meteorológicos"

## 🛠️ Funcionalidades Implementadas

### 1. 🗃️ Cadastro de Fontes de Dados (`create_meteorological_data_source`)

**Funcionalidades:**
- ✅ Cadastro manual de fontes personalizadas
- ✅ Validação para evitar fontes duplicadas
- ✅ Botões para cadastro rápido de fontes pré-configuradas
- ✅ Visualização de fontes já cadastradas
- ✅ Interface seguindo padrão visual do projeto

**Fontes Pré-configuradas:**
- 🛰️ **NASA POWER** - Dados meteorológicos globais via satélite
- 🌍 **Open-Meteo** - API de dados históricos meteorológicos

**Campos da Fonte:**
- `name` (obrigatório): Nome identificador da fonte
- `description` (opcional): Descrição detalhada da fonte

### 2. 🌪️ Cadastro de Dados Meteorológicos (`create_meteorological_data`)

**Funcionalidades:**
- ✅ Seleção de cidade com informações completas (formato especificado)
- ✅ Definição de período de coleta (data início/fim)
- ✅ Seleção de fontes com checkboxes organizados em colunas
- ✅ Seleção de alturas específicas para cada fonte
- ✅ Validação rigorosa para evitar dados duplicados
- ✅ Coleta automática via APIs NASA POWER e Open-Meteo
- ✅ Feedback em tempo real durante a coleta
- ✅ Estatísticas dos dados coletados

**Formato de Exibição das Cidades:**
```
cidade - sigla do estado - código do país - lat: <latitude> - lon: <longitude>
```
Exemplo: `Jaraguá do Sul - SC - BR - lat: -26.4867 - lon: -49.0773`

**Alturas Disponíveis:**
- **NASA POWER**: 10m, 50m
- **Open-Meteo**: 10m, 80m, 120m, 180m

## 🔒 Prevenção de Dados Duplicados

O sistema implementa validação rigorosa para evitar inserções duplicadas baseada em:

1. **Cidade** (cidade_id)
2. **Período** (data_inicio até data_fim)
3. **Fonte de Dados** (meteorological_data_source_id)
4. **Altura de Captura** (altura_captura)

### Como Funciona:
1. Antes de cada inserção, o sistema consulta registros existentes
2. Se encontrar dados para a mesma combinação, impede a inserção
3. Exibe mensagem clara informando sobre a duplicata
4. Permite continuar com outras combinações não duplicadas

## 🎨 Padrão Visual

A interface segue rigorosamente o padrão CSS estabelecido no projeto:

### Classes CSS Utilizadas:
- `.page-main-header` - Cabeçalho principal das páginas
- `.wind-info-card` - Cards de informação
- `.wind-info-title` - Títulos dos cards
- `.slide-in` - Animações de entrada

### Exemplos de Uso:
```python
st.markdown("""
<div class="page-main-header">
    <h1>🌤️ Cadastro de Dados Meteorológicos</h1>
    <p>Gerencie fontes de dados e colete informações climáticas</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="wind-info-card slide-in">
    <h4 class="wind-info-title">🗃️ Cadastro de Fonte de Dados</h4>
</div>
""", unsafe_allow_html=True)
```

## 📊 Estrutura dos Dados

### Entidade MeteorologicalDataSource
```python
@dataclass
class MeteorologicalDataSource:
    id: Optional[int] = None
    name: str = ""                    # Nome da fonte (ex: "NASA_POWER")
    description: Optional[str] = None # Descrição detalhada
```

### Entidade MeteorologicalData
```python
@dataclass
class MeteorologicalData:
    id: Optional[int] = None
    meteorological_data_source_id: int = 0  # FK para fonte
    cidade_id: int = 0                      # FK para cidade
    data: Optional[date] = None             # Data da medição
    altura_captura: Optional[float] = None  # Altura de captura (m)
    velocidade_vento: Optional[float] = None # Velocidade do vento (m/s)
    temperatura: Optional[float] = None     # Temperatura (°C)
    umidade: Optional[float] = None         # Umidade relativa (%)
    created_at: Optional[datetime] = None   # Timestamp de criação
```

## 🧪 Testes

### Teste Automatizado
Execute o teste da interface:
```bash
python test_meteorological_interface.py
```

### Teste Manual
1. Acesse a interface via Streamlit
2. Cadastre uma fonte de dados (ex: NASA_POWER)
3. Selecione uma cidade cadastrada
4. Escolha um período de coleta
5. Selecione fonte e alturas
6. Execute a coleta
7. Verifique os dados salvos

## 🔧 Solução de Problemas

### Erro: "Nenhuma fonte de dados cadastrada"
**Solução:** Acesse a aba "Cadastrar Fonte de Dados" e registre NASA_POWER ou OPEN_METEO

### Erro: "Nenhuma cidade cadastrada"
**Solução:** Use o sistema de cadastro de localidades para registrar cidades primeiro

### Erro: "Dados já existem"
**Causa:** Tentativa de inserir dados duplicados
**Solução:** Escolha período diferente ou outra combinação cidade/fonte/altura

### APIs Não Respondem
**NASA POWER:** Pode ser lenta, aguarde alguns minutos
**Open-Meteo:** Verifique limite de requisições diárias

## 📈 Próximos Passos

- [ ] Implementar filtros avançados na visualização
- [ ] Adicionar gráficos de análise dos dados coletados
- [ ] Criar exportação de dados em CSV/Excel
- [ ] Implementar previsões baseadas nos dados históricos
- [ ] Adicionar mais fontes de dados (INMET, outras APIs)

## 💡 Dicas de Uso

1. **Cadastre fontes primeiro** antes de tentar coletar dados
2. **Períodos menores** são processados mais rapidamente
3. **Multiple alturas** aumentam a precisão das análises
4. **Dados históricos** são mais estáveis que dados recentes
5. **Combine fontes** para validação cruzada dos dados

## 🎯 Integração com Análise de Turbinas

Os dados coletados por esta interface serão utilizados para:
- Modelagem de performance de turbinas eólicas
- Análise de viabilidade de instalações
- Cálculos de geração energética esperada
- Otimização de altura e posicionamento de turbinas

---

**Desenvolvido por:** André Vinícius Lima do Nascimento  
**Data:** 2025  
**Sistema:** Simulação de Turbinas Eólicas
