# Análise Simplificada de Turbinas Eólicas

## 📋 Visão Geral

A **Análise Simplificada** é uma nova página do sistema EolicSim que resolve o problema de desconexão identificado na análise completa. Esta página oferece uma análise direta e integrada que utiliza corretamente os dados do banco de dados.

## 🎯 Objetivos

1. **Integração Real**: Usar dados reais de cidades, turbinas e fontes meteorológicas do banco
2. **Análise Direta**: Previsão de geração de energia sem passos intermediários complexos  
3. **Flexibilidade**: Permitir escolha de métodos de projeção e fontes de dados
4. **Resultados Práticos**: Mostrar tempo operacional e previsões de geração

## ⚙️ Funcionalidades

### 🌍 Seleção de Localização
- **Cidades com Dados**: Apenas cidades que possuem dados meteorológicos reais
- **Informações Geográficas**: Latitude, longitude, região e país
- **Contagem de Dados**: Quantidade de registros meteorológicos disponíveis

### 🌀 Seleção de Turbina
- **Fabricantes Reais**: Lista de fabricantes cadastrados no banco
- **Turbinas por Fabricante**: Modelos específicos com especificações reais
- **Especificações Técnicas**: Potência, diâmetro, velocidades de corte

### 📊 Parâmetros de Análise

#### Métodos de Projeção de Vento
1. **Lei de Potência**: `v(h) = v_ref × (h/h_ref)^n`
2. **Lei Logarítmica**: `v(h) = v_ref × ln(h/z0) / ln(h_ref/z0)`

#### Tipos de Terreno Pré-configurados
| Terreno | Lei de Potência (n) | Lei Logarítmica (z0) |
|---------|-------------------|-------------------|
| Água/Lagos | 0.10 | 0.0002m |
| Terreno Plano | 0.16 | 0.03m |
| Pastagem | 0.20 | 0.10m |
| Árvores Esparsas | 0.22 | 0.25m |
| Floresta | 0.28 | 1.00m |
| Área Urbana | 0.40 | 2.00m |

### 📅 Configurações de Análise
- **Altura da Turbina**: 20m a 150m
- **Fonte de Dados**: NASA Power ou OpenMeteo
- **Período**: 30, 60, 90, 180 ou 365 dias

## 📈 Resultados Fornecidos

### ⚡ Estatísticas de Geração
- **Potência Média**: Potência média gerada (kW)
- **Energia Estimada**: Energia total para o período (kWh)
- **Velocidade Média**: Velocidade média corrigida para altura da turbina
- **Fator de Capacidade**: Eficiência geral da turbina (%)

### ⏱️ Análise de Tempo Operacional

| Estado | Descrição | Cor |
|--------|-----------|-----|
| 🔴 Inoperante | v < cut-in (turbina parada) | Vermelho |
| 🟡 MPPT | cut-in ≤ v ≤ nominal (busca máxima potência) | Amarelo |
| 🟢 Nominal | nominal < v ≤ cut-out (potência constante) | Verde |
| 🔴 Cut-out | v > cut-out (parada de segurança) | Vermelho |

### 📊 Visualizações
1. **Gráfico de Pizza**: Distribuição percentual do tempo operacional
2. **Gráfico Temporal**: Evolução da potência ao longo do tempo
3. **Histograma**: Distribuição das velocidades do vento
4. **Tabela Diária**: Previsões médias diárias de geração

### 📅 Previsão Média Diária
- Potência média, máxima e energia diária
- Velocidade média do vento
- Percentual de tempo em operação nominal
- Histórico dos últimos 10 dias

## 🔧 Implementação Técnica

### Cálculos Principais

#### Correção de Velocidade
```python
# Lei de Potência
v_corrigida = v_ref * (h_turbina / h_ref) ** n

# Lei Logarítmica  
v_corrigida = v_ref * ln(h_turbina / z0) / ln(h_ref / z0)
```

#### Curva de Potência Simplificada
```python
if v < cut_in or v > cut_out:
    P = 0  # Turbina parada
elif v <= rated_speed:
    P = P_nominal * ((v - cut_in) / (v_nominal - cut_in))³  # MPPT
else:
    P = P_nominal  # Potência nominal constante
```

### Tratamento de Dados
- **Conversão de Tipos**: Todos os valores Decimal são convertidos para float
- **Validação de Dados**: Verificação de dados nulos e inconsistentes  
- **Filtros Flexíveis**: Por período, fonte e disponibilidade

## 🔄 Vantagens sobre a Análise Completa

### ✅ Problemas Resolvidos
1. **Integração Real**: Usa turbinas reais do banco, não modelos hardcoded
2. **Continuidade**: Mantém coerência desde seleção até resultados
3. **Simplicidade**: Interface mais direta e intuitiva
4. **Dados Reais**: Todas as análises baseadas em dados reais cadastrados

### 🚀 Melhorias Implementadas
1. **Seleção Inteligente**: Apenas opções com dados disponíveis
2. **Validação Robusta**: Tratamento de erros e casos especiais
3. **Resultados Práticos**: Foco em métricas operacionais importantes
4. **Visualização Clara**: Gráficos informativos e tabelas organizadas

## 📝 Como Usar

1. **Configure a Localização**: Selecione uma cidade com dados meteorológicos
2. **Escolha a Turbina**: Selecione fabricante e modelo do banco de dados
3. **Defina Parâmetros**: Método de projeção, altura, fonte e período
4. **Execute a Análise**: Clique em "Executar Análise"
5. **Analise Resultados**: Veja estatísticas, gráficos e previsões

## 🎯 Casos de Uso

### 👨‍💼 Análise de Viabilidade
- Estimar geração de energia para uma localidade específica
- Comparar performance de diferentes turbinas
- Avaliar impacto da altura de instalação

### 📊 Planejamento Operacional  
- Prever tempo de inatividade e manutenção
- Estimar receita baseada na geração
- Analisar variações sazonais

### 🔬 Estudos Técnicos
- Comparar métodos de projeção de vento
- Avaliar qualidade de diferentes fontes de dados
- Validar especificações de turbinas

## 🚀 Próximos Passos

1. **Relatórios Exportáveis**: Gerar PDFs com resultados
2. **Análise Comparativa**: Comparar múltiplas turbinas/locais
3. **Previsões Avançadas**: Modelos de machine learning
4. **Integração Econômica**: Análise de retorno de investimento
