# Dados Meteorológicos: Temperatura e Umidade

## Visão Geral

O sistema foi expandido para incluir coleta e armazenamento de dados de **temperatura** e **umidade relativa** junto com os dados de velocidade do vento. Esta documentação descreve as especificações técnicas e funcionais desta expansão.

## Especificações de Altura dos Dados

### ⚠️ IMPORTANTE: Diferentes Alturas por Tipo de Dado

Os dados meteorológicos são coletados em diferentes alturas dependendo do parâmetro:

| Parâmetro | Altura de Captura | APIs Suportadas |
|-----------|-------------------|-----------------|
| **Velocidade do Vento** | 10m, 50m, 80m, 120m, 180m* | Open-Meteo, NASA POWER |
| **Temperatura** | **2 metros** | Open-Meteo, NASA POWER |
| **Umidade Relativa** | **2 metros** | Open-Meteo, NASA POWER |

*\*NASA POWER suporta apenas 10m e 50m para velocidade do vento*

### Alturas Específicas por API

#### Open-Meteo API
- **Vento:** 10m, 80m, 120m, 180m
- **Temperatura:** 2m (fixo)
- **Umidade:** 2m (fixo)

#### NASA POWER API  
- **Vento:** 10m, 50m
- **Temperatura:** 2m (fixo)
- **Umidade:** 2m (fixo)

## Funcionalidades Implementadas

### 1. Coleta Simultânea
- Velocidade do vento, temperatura e umidade são coletadas em uma **única requisição** para cada API
- Isso garante consistência temporal entre os dados
- Reduz o número de chamadas às APIs externas

### 2. Tolerância a Falhas
- **Se algum parâmetro não estiver disponível**, os demais são coletados normalmente
- O sistema continua funcionando mesmo se temperatura ou umidade falharem
- Valores ausentes são registrados como `NULL` no banco de dados

### 3. Armazenamento no Banco
- Campos `temperatura` e `umidade` na entidade `MeteorologicalData`
- Valores podem ser `NULL` se não disponíveis
- Campo `altura_captura` sempre se refere à altura do vento (10m, 50m, etc.)
- Temperatura e umidade sempre a 2m são associadas ao mesmo registro

## Avisos ao Usuário

### Na Interface Web
Sempre que dados meteorológicos são exibidos, os seguintes avisos são mostrados:

> **📏 Informação sobre Alturas:**
> - Velocidade do vento: obtida nas alturas especificadas (10m, 50m, 80m, 120m, 180m)
> - Temperatura: sempre obtida a **2 metros** de altura
> - Umidade relativa: sempre obtida a **2 metros** de altura

> **⚠️ Disponibilidade dos Dados:**
> - Se algum parâmetro não estiver disponível na API, será registrado como "não disponível"
> - Isso não prejudica a coleta dos demais parâmetros
> - A análise pode prosseguir com os dados disponíveis

### Nas Análises e Relatórios
- Metadados sempre incluem informação sobre quais dados estão disponíveis
- Indicação clara das alturas para cada tipo de parâmetro
- Estatísticas separadas para cada tipo de dado

## Implementação Técnica

### Modificações nas APIs

#### Open-Meteo Client (`open_meteo.py`)
```python
# Parâmetros agora incluem temperatura e umidade
parametros_horarios = [f"wind_speed_{altura}m" for altura in alturas]
if incluir_temperatura:
    parametros_horarios.append("temperature_2m")
if incluir_umidade:
    parametros_horarios.append("relative_humidity_2m")
```

#### NASA POWER Client (`nasa_power.py`)
```python
# Parâmetros NASA POWER para dados completos
parametros = []
for altura in alturas:
    if altura == 10: parametros.append("WS10M")
    elif altura == 50: parametros.append("WS50M")
if incluir_temperatura: parametros.append("T2M")
if incluir_umidade: parametros.append("RH2M")
```

### Estrutura de Resposta
```python
{
    'metadata': {
        'dados_incluidos': {
            'velocidade_vento': True,
            'temperatura': True/False,
            'umidade': True/False
        },
        'alturas_dados': {
            'velocidade_vento': '10m, 50m',
            'temperatura': '2m',
            'umidade': '2m'
        }
    },
    'dados': [
        {
            'data_hora': datetime,
            'velocidade_vento': float,
            'temperatura': float,  # Pode ser None
            'umidade': float,      # Pode ser None
            'altura_captura': int  # Altura do vento
        }
    ]
}
```

## Exemplos de Uso

### Coletando Dados Completos
```python
from meteorological.api.open_meteo import OpenMeteoClient

client = OpenMeteoClient()
dados = client.obter_dados_historicos_vento(
    latitude=-26.4869,
    longitude=-49.0679,
    data_inicio='2024-01-01',
    data_fim='2024-01-31',
    alturas=[10],
    incluir_temperatura=True,
    incluir_umidade=True
)
```

### Coletando Apenas Vento (Compatibilidade)
```python
# Funciona como antes
dados = client.obter_dados_historicos_vento(
    latitude=-26.4869,
    longitude=-49.0679,
    data_inicio='2024-01-01',
    data_fim='2024-01-31',
    alturas=[10],
    incluir_temperatura=False,
    incluir_umidade=False
)
```

## Validações na Entidade

A entidade `MeteorologicalData` inclui validações para os novos campos:

```python
def validar(self) -> bool:
    # Temperatura: -100°C a 60°C (valores extremos possíveis)
    if self.temperatura is not None and (self.temperatura < -100 or self.temperatura > 60):
        return False
    
    # Umidade: 0% a 100%
    if self.umidade is not None and (self.umidade < 0 or self.umidade > 100):
        return False
    
    return True

def tem_dados_temperatura(self) -> bool:
    return self.temperatura is not None

def tem_dados_umidade(self) -> bool:
    return self.umidade is not None and 0 <= self.umidade <= 100
```

## Benefícios da Implementação

1. **Dados Mais Completos:** Análises meteorológicas mais abrangentes
2. **Consistência Temporal:** Todos os parâmetros coletados no mesmo momento
3. **Flexibilidade:** Sistema funciona com ou sem temperatura/umidade
4. **Transparência:** Usuário sempre informado sobre disponibilidade dos dados
5. **Compatibilidade:** Código existente continua funcionando sem modificações

## Considerações Futuras

- Possibilidade de incluir outros parâmetros meteorológicos (pressão, direção do vento, etc.)
- Expansão para outras APIs meteorológicas
- Implementação de interpolação para alturas não padronizadas
- Análises correlacionais entre temperatura, umidade e velocidade do vento
