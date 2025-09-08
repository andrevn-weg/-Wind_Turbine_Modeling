## UNIVERSIDADE FEDERAL DE SANTA MARIA

## CAMPUS CACHOEIRA DO SUL

## CURSO DE GRADUAÇÃO EM ENGENHARIA ELÉTRICA

# André Vinícius Lima do Nascimento

## DESENVOLVIMENTO DE UM SISTEMA DE SIMULAÇÃO DE

## TURBINAS EÓLICAS

## Cachoeira do Sul, RS

## 2025


```
André Vinícius Lima do Nascimento
```
###### DESENVOLVIMENTO DE UM SISTEMA DE SIMULAÇÃO DE TURBINAS

###### EÓLICAS

```
Trabalho de Conclusão de Curso apresentado ao
Curso de Graduação em Engenharia Elétrica, da
Universidade Federal de Santa Maria, campus
Cachoeira do Sul (UFSM-CS, RS), como requi-
sito parcial para obtenção de grau deBacharel
em Engenharia Elétrica.
```
```
ORIENTADOR: Prof. Dr. Gustavo Guilherme Koch
```
```
Cachoeira do Sul, RS
2025
```

```
André Vinícius Lima do Nascimento
```
###### DESENVOLVIMENTO DE UM SISTEMA DE SIMULAÇÃO DE TURBINAS

###### EÓLICAS

```
Trabalho de Conclusão de Curso apresentado ao
Curso de Graduação em Engenharia Elétrica, da
Universidade Federal de Santa Maria, campus
Cachoeira do Sul (UFSM-CS, RS), como requi-
sito parcial para obtenção de grau deBacharel
em Engenharia Elétrica.
```
```
Aprovado em 7 de agosto de 2025:
```
```
Gustavo Guilherme Koch, Dr. (UFSM)
```
```
Dion Lenon Prediger Feil, Dr. (UFSM)
```
```
Diogo Ribeiro Vargas, Dr. (UFSM)
```
```
Cachoeira do Sul, RS
2025
```

RESUMO

```
DESENVOLVIMENTO DE UM SISTEMA DE SIMULAÇÃO DE
TURBINAS EÓLICAS
```
```
AUTOR: André Vinícius Lima do Nascimento
ORIENTADOR: Gustavo Guilherme Koch
```
O aumento da necessidade de geração de energia elétrica devido ao crescimento populacional
e à expansão econômica destaca a urgência de soluções energéticas eficientes e sustentáveis. A
energia eólica surge como uma alternativa viável para reduzir a dependência de combustíveis
fósseis e minimizar os impactos ambientais. No Brasil, a energia eólica tem ganhado importân-
cia, contribuindo significativamente para a matriz energética do país, que é uma das mais limpas
do mundo. Assim, este trabalho tem como objetivo desenvolver um simulador de turbina eólica
de velocidade variável, juntamente com um sistema de supervisão, permitindo testar a turbina
em diferentes regimes de vento e pontos de operação. A metodologia envolve o uso dosoftware
MATLAB/SIMULINK para modelagem e simulação das séries temporais do vento e do sistema
de emulação do aerogerador. O modelo do aerogerador será desenvolvido em software, abor-
dando seus comportamentos construtivos e elétricos. A validação dos modelos será realizada
comparando os resultados das simulações com dados teóricos e estudos de caso. O desenvolvi-
mento da plataforma de simulação de turbina eólica incorpora todos os modelos desenvolvidos,
permitindo a análise dos diversos componentes presentes em uma turbina e a geração de um
relatório de desempenho.

Palavras-chave:Energia eólica, Simulação, Modelagem, Sistemas eólicos, Sustentabilidade.


ABSTRACT

DEVELOPMENT OF A WIND TURBINE SIMULATION SYSTEM

```
AUTHOR: André Vinícius Lima do Nascimento
ADVISOR: Gustavo Guilherme Koch
```
The increasing need for electricity generation due to population growth and economic expan-
sion highlights the urgency for efficient and sustainable energy solutions. Wind energy emerges
as a viable alternative to reduce dependence on fossil fuels and minimize environmental im-
pacts. In Brazil, wind energy has gained importance, contributing significantly to the country’s
energy matrix, which is one of the cleanest in the world. Thus, this work aims to develop a
variable-speed wind turbine simulator, along with a supervisory system, allowing the turbine to
be tested under different wind regimes and operating points. The methodology involves the use
of MATLAB/SIMULINK software for modeling and simulating wind time series and the wind
turbine emulation system. The wind turbine model will be developed in software, addressing
its constructive and electrical behaviors. The validation of the models will be performed by
comparing the simulation results with theoretical data and case studies. The development of the
wind turbine simulation platform incorporates all developed models, allowing the analysis of
the various components present in a turbine and the generation of a performance report.

Keywords:Wind energy, Simulation, Modeling, Wind systems, Sustainability.


## LISTA DE FIGURAS


Figura 4.3 – Fotografia do anemômetro instalado na UFSM Campus Cachoeira do Sul... 57
Figura 4.4 – Gráfico dos dados do anemômetro instalado na UFSM Campus Cachoeira do
Sul................................................................. 58
Figura 4.5 – Distribuição de Weibull ajustada aos dados do anemômetro instalado na UFSM
Campus Cachoeira do Sul............................................. 58
Figura 4.6 – Perfis de velocidade do vento em função da altura, obtidos pela Lei da Potên-
cia e pela Lei Logarítmica............................................ 59


###### LISTA DE TABELAS

Tabela 1.1 – Geração de energia elétrica por fonte renováveis no Brasil (2024).......... 9
Tabela 2.1 – Principais características das escalas atmosféricas........................ 18
Tabela 2.2 – Fatornpara diferentes tipos de superfícies............................... 23
Tabela 2.3 – Valores de comprimentos de rugosidade para diferentes terrenos........... 24
Tabela 2.4 – Parâmetros utilizados para o cálculo doCp(λ,β)segundo diferentes auto-
res/modelos.......................................................... 31
Tabela 2.5 – Fatores de turbulência para diferentes terrenos............................ 40
Tabela 2.6 – Comparação entre geração estimada com dados teóricos e dados reais de ge-
ração de energia eólica na Vila Santa Terezinha, Franca – SP.............. 48
Tabela 2.7 – Características Elétricas do Aerogerador TE24........................... 49
Tabela 2.8 – Características Construtivas do Aerogerador TE24........................ 49
Tabela 3.1 – Cronograma de ações.................................................. 53
Tabela 4.1 – Comparação das velocidades do vento estimadas pela Lei da Potência e Lei
Logarítmica em diferentes alturas...................................... 59


## SUMÁRIO

   - Figura 1.1 – Crescimento das energias renováveis no Brasil nos últimos anos.
   - Figura 2.1 – Evolução da Capacidade Instalada de Energia Eólica
      - médias anuais. Figura 2.2 – Atlas do Potencial Eólico Brasileiro desenvolvido pelo modelo Brams em
   - Figura 2.3 – Camadas da Atmosfera
   - Figura 2.4 – Formação dos ventos devido ao movimento das massas de ar
   - Figura 2.5 – Esquema representativo da circulação geral da atmosfera terrestre.
- Figura 2.6 – Circulação de ventos em escala local.(a) Brisa Marítima e (b) Brisa Terrestre.
      - nha. Figura 2.7 – Circulação de ventos em escala local.(a) Brisa do Vale e (b) Brisa da Monta-
   - Figura 2.8 – Variações de velocidade ao longo do tempo na Dinamarca.
   - Figura 2.9 – Esquema do perfil de velocidades sobre uma superfície plana.
   - Figura 2.10 – O fluxo de massa de ar com velocidadevatravés de uma áreaA(circular).
   - Figura 2.11 – Área varrida pelas pás de uma turbina de eixo horizontal.
   - Figura 2.12 – Modelo de Darrieus.
   - Figura 2.13 – Curva de potência do vento em função de sua velocidade.
   - Figura 2.14 – Passagem de ar por uma turbina eólica de eixo horizontal.
      - ângulo de passoβ, para equações (2.28) e (2.29). Figura 2.15 – Coeficiente de Potência (Cp) versus Relação de Velocidade na Ponta (λ) para
      - ângulo de passoβ, para equações (2.30) e (2.31). Figura 2.16 – Coeficiente de Potência (Cp) versus Relação de Velocidade na Ponta (λ) para
      - ângulo de passoβ, para equações (2.26) e (2.27). Figura 2.17 – Coeficiente de Potência (Cp) versus Relação de Velocidade na Ponta (λ) para
      - do vento ao longo do tempot. Figura 2.18 – Fluxo de ar decomposto em três categorias.Ué o componente velocidade
   - Figura 2.19 – Representação do vento em velocidade média, ondulação e turbulência.
   - Figura 2.20 – Aproximação do Filtro de Von Karman nosoftwareMATLAB/SIMULINK
      - TLAB/SIMULINK Figura 2.21 – Calculo da constante de tempo Tf do Filtro simulado nosoftwareMA-
         - Figura 2.22 – GanhoKfdo Filtro de Von Karman simulado nosoftwareMATLAB/SIMULINK
         - Figura 2.23 – O ruído utilizado para ativar o filtro gerado nosoftwareMATLAB/SIMULINK
   - Figura 2.24 – Série Temporal de Vento modelado nosoftwareMATLAB/SIMULINK
         - Figura 2.25 – Resultado do modelo da Série Temporal de VentosoftwareMATLAB/SIMULINK
   - Figura 2.26 – Esquema abrangente de operação de um aerogerador.
   - Figura 2.27 – Esquema de Turbina Eólica Moderna.
   - Figura 2.28 – Aspectos de um perfil aerodinâmico.
   - Figura 2.29 – Escoamento ao longo do perfil.
   - Figura 2.30 – Forças Aerodinâmicas
   - Figura 3.1 – Fluxograma de desenvolvimento do projeto.
   - Figura 3.2 – Ilustração do cenário.
   - Figura 4.1 – Atlas Eólico para o Rio Grande do Sul à altura de 100 metros.
   - Figura 4.2 – Velocidade média do vento em Cachoeira do Sul.
- 1 INTRODUÇÃO
- 1.1 OBJETIVO GERAL
- 1.2 OBJETIVOS ESPECÍFICOS
- 1.3 ORGANIZAÇÃO DO TRABALHO
- 2 REFERENCIAL TEÓRICO
- 2.1 BRASIL E SEU MAPA EÓLICO
- 2.1.1 Mapeamento do Potencial Eólico.
- 2.2 ANALISE DOS VENTOS
- 2.2.1 Circulação dos Ventos.
- 2.2.2 Classificação dos Movimentos Atmosféricos.
- 2.2.3 Forças Fundamentais que Regem o Movimento do Vento.
- 2.3 PERFIL DE VENTO
- 2.4 POTÊNCIA GERADA PELOS VENTOS
- 2.4.1 Avaliação da Energia Contida no Vento.
- 2.4.2 Determinação da Energia Convertida em Potência Mecânica.
- 2.5 CURVA COEFICIENTE DE PERFORMANCE (Cp)
- 2.6 SÉRIE TEMPORAL DO VENTO
- 2.6.1 Vento e Fluxo.
- 2.6.2 Modelagem de Séries Temporais com o Filtro de Von Karman.
- 2.7 PRINCÍPIOS DE FUNDAMENTO DAS TURBINAS EÓLICAS
- 2.8 COMPONENTES DE AEROGERADOR DE EIXO HORIZONTAL
- 2.9 PERFIL AERODINÂMICO
- 2.9.1 Coeficientes e Parâmetros Aerodinâmicos.
- 2.10 CONTROLE DE ÂNGULO DE PASSO
- 2.11 CONTROLADOR YAW
- 2.12 TURBINA EÓLICA TE24
- 3 METODOLOGIA.
- 3.1 CRONOGRAMA PARA DESENVOLVIMENTO DO TCC II
- 4 DESENVOLVIMENTO.
- 4.1 ANÁLISE DO CENÁRIO BASE
- 4.1.1 Cachoeira do Sul.
- 4.2 SISTEMA DE GERAÇÃO EÓLICA - EOLICSIM
- 5 CONCLUSÃO
   - REFERÊNCIAS BIBLIOGRÁFICAS.


## 1 INTRODUÇÃO

A crescente necessidade de geração de energia elétrica, impulsionada pelo aumento da
população e pela expansão econômica, tem colocado em evidência a urgência de se encontrar
soluções energéticas que sejam ao mesmo tempo eficientes e sustentáveis. Nos últimos anos,
a busca por alternativas que reduzam a dependência dos combustíveis fósseis e minimizem os
impactos ambientais tem se tornado uma prioridade global. Nesse contexto, fontes de energia
renovável, como a energia eólica, emergem como opções viáveis e necessárias para atender à
demanda crescente por eletricidade de forma ambientalmente responsável.
De acordo com a Agência Internacional de Energia (2024), o consumo mundial de ener-
gia elétrica cresceu cerca de 3,1% ao ano na última década, refletindo o aumento das atividades
industriais e a melhoria dos padrões de vida. No Brasil, a Empresa de Pesquisa Energética
(2024) destaca que, entre 2010 e 2020, o consumo de energia elétrica aumentou em média 4,2%
ao ano, influenciado tanto pelo crescimento econômico quanto pelo aumento da população ur-
bana.
Para atender ao crescente consumo de energia elétrica, muitos países têm recorrido ao
aumento da geração a partir de combustíveis fósseis, como carvão, petróleo e gás natural. Esse
incremento, porém, tem causado uma escalada significativa nas emissões de gases de efeito
estufa, agravando o aquecimento global. Segundo Calijuri e Cunha (2013), "a matriz elétrica
mundial é predominantemente fóssil, e os esforços para reduzir a dependência desses combustí-
veis de alto impacto ambiental são cruciais para mitigar as mudanças climáticas.". Este cenário
evidencia a necessidade urgente de diversificar a matriz energética. Em resposta a isso, a co-
munidade internacional tem intensificado a busca por alternativas mais limpas, como a energia
eólica, e promovido campanhas e acordos para incentivar o uso de fontes renováveis. Iniciativas
como o Protocolo de Kyoto (Nações Unidas, 1997) e o Acordo de Paris (Nações Unidas, 2015),
que introduzem mecanismos de crédito de carbono, têm sido fundamentais para estimular in-
vestimentos em tecnologias sustentáveis e reduzir as emissões globais de carbono.

```
Figuras/Introducao/Grafico_do_crescimento_das_energias_renovaveis.png
```
### Figura 1.1 – Crescimento das energias renováveis no Brasil nos últimos anos.

```
Fonte: Empresa de Pesquisa Energética (EPE) (2025)
```
```
O Brasil destaca-se mundialmente pela adoção de energias renováveis, possuindo uma
```

das matrizes energéticas mais limpas do planeta. Segundo Empresa de Pesquisa Energética
(EPE) (2025), aproximadamente 88% da eletricidade gerada no país tem origem em fontes re-
nováveis, com predominância da energia hídrica. Nos últimos anos, a energia eólica vem assu-
mindo papel cada vez mais relevante no cenário nacional. Em 2024, essa fonte foi responsável
por cerca de 14% da geração elétrica brasileira, e, somada à energia solar fotovoltaica, alcançou
23,7% do total, evidenciando o avanço das energias renováveis no país. Em comparação com
outras fontes, como biomassa, nuclear e solar, conforme ilustrado na Figura 1.1, a energia eó-
lica apresentou crescimento expressivo, consolidando-se como a principal fonte renovável após
a hidrelétrica nos últimos cinco anos, como demonstrado na Tabela 1.1.

```
Tabela 1.1 – Geração de energia elétrica por fonte renováveis no Brasil (2024)
Fonte (GWh) 2024 % do Total
Hidrelétrica 421.799 56,14%
Gás Natural 47.792 6,36%
Eólica 107.654 14,33%
Biomassa 58.027 7,72%
Nuclear 15.767 2,10%
Carvão Vapor 10.247 1,36%
Derivados do Petróleo 5.960 0,79%
Solar Fotovoltaica 70.665 9,41%
Outras 13.425 1,79%
Geração Total 751.335 100%
Fonte: Empresa de Pesquisa Energética (EPE) (2025)
```
A expansão do setor de energia eólica no Brasil tem sido notável, impulsionada por
investimentos substanciais tanto do setor público quanto do privado. Segundo a Associação
Brasileira de Energia Eólica (ABEEólica) (2024), os investimentos acumulados em energia
eólica no Brasil desde 2009 já superam a marca de R$ 100 bilhões. Este influxo de capital tem
permitido a construção de novos parques eólicos e a modernização de infraestruturas existentes,
aumentando significativamente a capacidade de geração. Em 2020, foram investidos cerca de
R$ 13 bilhões em novos projetos, com previsão de investimentos adicionais de R$ 62 bilhões até
2024, conforme relatado pelo BNDES (2024) e Estadão (2024). Este cenário de crescimento
contínuo reflete a confiança dos investidores na energia eólica como uma fonte sustentável e
lucrativa, além de demonstrar o compromisso do Brasil em se tornar um líder global na geração
de energia renovável.
Portanto, é evidente que o campo de geração eólica ainda está em expansão. Dado
esse aumento, torna-se cada vez mais necessários estudos para prever e reduzir a ocorrência de
problemas diversos no controle de turbinas. Desta forma, o presente trabalho busca desenvolver
uma plataforma de simulação de uma turbina eólica, a fim de colaborar com estudos no setor
e buscar a otimização da qualidade de energia produzida a partir do vento, com o estudo de


técnicas de modos de operação, velocidade e limitação de potência.

## 1.1 OBJETIVO GERAL

O objetivo do trabalho é desenvolver um simulador de turbina eólica de velocidade variá-
vel. Além disso, busca-se desenvolver um sistema de supervisão, possibilitando testar a turbina
em diferentes regimes de vento e pontos de operação.

## 1.2 OBJETIVOS ESPECÍFICOS

1. Revisar a literatura sobre sistemas de conversão eólica.
2. Obter o perfil médio de vento em Cachoeira do Sul.
3. Adquirir a série temporal do vento, incluindo turbulência e rajadas de vento.
4. Desenvolver um sistema de controle para uma turbina eólica de 20 kW, abrangendo desde
    a velocidade mínima decut-in, técnica de MPPT, limitação de potência ecut-off.
5. Implementar uma plataforma de simulação que permita a modelagem e análise de todos
    os componentes de uma turbina eólica (com possibilidade de uso de Python).
6. Desenvolver um sistema de supervisão utilizando Python.
7. Avaliar o desempenho do sistema de emulação em diferentes cenários operacionais.

## 1.3 ORGANIZAÇÃO DO TRABALHO

O trabalho está organizado da seguinte maneira:
O capítulo 2 apresenta uma revisão da literatura sobre os principais conceitos relacio-
nados ao estudo. Neste capítulo é obtido e desenvolvido a análise dos ventos, perfil de vento,
potência gerada pelos ventos, série temporal do vento e o mapa eólico do Brasil. Também são
discutidos os modelos matemáticos e físicos que fundamentam a simulação de turbinas eólicas.
No capítulo 3 aborda os conceitos básicos de energia eólica e princípios fundamentais
das turbinas eólicas. São descritos os componentes de um aerogerador de eixo horizontal, com
destaque para a turbina eólica TE24, e as características técnicas e construtivas relevantes para
o desenvolvimento do simulador.


No capítulo 4 é detalhada a metodologia utilizada para o desenvolvimento do sistema de
simulação de turbinas eólicas. Inclui a descrição das ferramentas e técnicas empregadas, como
o software MATLAB/SIMULINK, bem como os critérios e procedimentos para a modelagem
e simulação das séries temporais do vento e do sistema de emulação do aerogerador.
No capítulo 5, são expostas as conclusões gerais do estudo.


## 2 REFERENCIAL TEÓRICO

A crescente demanda por fontes de energia renovável e a necessidade de mitigar os im-
pactos ambientais têm impulsionado o desenvolvimento e a adoção de tecnologias eólicas no
Brasil e no mundo. Este capítulo apresenta os fundamentos teóricos essenciais para a com-
preensão do aproveitamento da energia eólica, abordando desde o potencial eólico nacional,
os fenômenos atmosféricos que influenciam o vento, até os princípios de funcionamento, com-
ponentes e características construtivas das turbinas eólicas modernas. São discutidos ainda os
principais modelos matemáticos para análise do perfil de vento, a estimativa da potência gerada,
a modelagem de séries temporais e os parâmetros aerodinâmicos que impactam o desempenho
dos aerogeradores, com destaque para a turbina TE24 utilizada neste trabalho.

## 2.1 BRASIL E SEU MAPA EÓLICO

As energias renováveis têm ganhado destaque no cenário energético mundial devido à
urgência de mitigar as mudanças climáticas e reduzir as emissões de gases de efeito estufa. No
Brasil, o potencial para a adoção de energias renováveis é vasto, dado seu território extenso e
condições climáticas favoráveis. Entre as fontes renováveis, a energia eólica se destaca como
uma das mais promissoras, contribuindo significativamente para a matriz energética do país.
O desenvolvimento da energia eólica no Brasil começou a se intensificar no início dos
anos 2000, impulsionado por políticas públicas e incentivos governamentais. O Programa de
Incentivo às Fontes Alternativas de Energia Elétrica (PROINFA) (2024), lançado em 2002, foi
um marco inicial, proporcionando contratos de compra de energia de longo prazo que atraíram
investidores. A partir de 2009, a realização de leilões específicos para fontes renováveis, in-
cluindo a eólica, promoveu uma expansão acelerada do setor, tornando a energia eólica uma das
fontes mais competitivas no Brasil.
O Brasil rapidamente se tornou um dos maiores mercados para energia eólica no mundo.
A capacidade instalada de energia eólica passou de menos de 1 GW em 2009 para mais de 30
GW em 2024, como destacado na Figura 2.1. Este crescimento foi suportado pela combina-
ção de políticas públicas favoráveis, avanços tecnológicos, e a competitividade econômica da
energia eólica.
As regiões Nordeste e Sul do Brasil são as que mais se destacam em termos de potencial
eólico e número de parques eólicos instalados. O Rio Grande do Norte, a Bahia e o Ceará são
os estados líderes na produção de energia eólica no país.


### Figura 2.1 – Evolução da Capacidade Instalada de Energia Eólica

```
Figuras/Teorico/evoluÃğÃčo da capacidade instalada2.png
```
```
Fonte: Associação Brasileira de Energia Eólica (ABEEólica) (2024)
```
## 2.1.1 Mapeamento do Potencial Eólico.

O mapeamento do potencial eólico no Brasil tem sido objeto de diversas pesquisas e
estudos ao longo dos anos, realizados por instituições acadêmicas, governamentais e privadas.
Esses estudos são fundamentais para identificar as regiões com maior capacidade para a geração
de energia eólica e para orientar investimentos no setor. Um exemplo é o Centro de Referência
para Energia Solar e Eólica Sérgio de Salvo Brito (CRESESB) com Atlas do Potencial Eólico
Brasileiro, representado na Figura 2.2.

```
Figura 2.2 – Atlas do Potencial Eólico Brasileiro desenvolvido pelo modelo Brams em médias
anuais.
```
```
Figuras/Teorico/Atlas_30m.png
```
```
(a) Velocidade média anual para a altura de 30 me-
tros.
```
```
Figuras/Teorico/Atlas_50m.png
```
```
(b) Velocidade média anual para a altura de 50 me-
tros.
Fonte: Centro de Referência para Energia Solar e Eólica Sérgio de Salvo Brito (CRESESB) (2013)
```

## 2.2 ANALISE DOS VENTOS

Entender os principais fenômenos envolvendo o vento requer compreender que o ar,
assim como qualquer fluido, está sujeito a influências físicas, como variações térmicas e de
pressão. A radiação solar, por exemplo, provoca diferenças de temperatura no ar, criando áreas
de alta e baixa pressão. Esse desequilíbrio faz com que o ar se mova das regiões de alta para as
de baixa pressão, resultando na formação dos ventos.
A estrutura da atmosfera terrestre é composta por diferentes camadas, sendo a troposfera
a mais próxima da superfície e onde ocorrem a maioria dos processos relacionados ao vento. A
Figura 2.3 ilustra as principais camadas da atmosfera.

### Figura 2.3 – Camadas da Atmosfera

```
Figuras/Teorico/atmo.png
```
```
Fonte: Desconhecido (2019)
```
Além dos efeitos térmicos e da estrutura atmosférica, a topografia do terreno exerce
influência significativa sobre o comportamento dos ventos. Montanhas, vales, florestas e cor-
pos d’água podem modificar tanto a direção quanto a velocidade dos ventos, criando padrões
complexos que devem ser considerados para a instalação eficiente de aerogeradores.
De acordo com Fadigas (2011), no passado os dados sobre recursos eólicos eram avali-
ados exclusivamente com base em critérios meteorológicos, considerando apenas o movimento
das grandes massas de ar, tornando as informações insuficientes e inadequadas. Por exemplo,
as torres meteorológicas não esclareciam as condições do vento em terrenos específicos nem a
variação da velocidade do vento com a altura.
Nas últimas décadas, conforme destacado por Fadigas (2011), campanhas de medição de
ventos começaram a ser realizadas em vários países. O objetivo dessas campanhas é obter uma


avaliação mais precisa das condições do vento em diferentes tipos de relevo, rugosidade do solo
e alturas variadas, visando ao aproveitamento energético otimizado dos ventos. Atualmente,
existem bases de dados e mapas eólicos com informações detalhadas coletadas ao longo de
vários anos. Esses dados são provenientes tanto de torres anemométricas quanto de medições
realizadas nas próprias centrais eólicas.
Entretanto, mesmo com a disponibilidade de mapas ou atlas eólicos, é fundamental rea-
lizar medições locais específicas para determinar o potencial eólico com precisão. Recomenda-
se a instalação de torres anemométricas adaptadas ao terreno e à rugosidade local, preferen-
cialmente posicionadas à altura do cubo do aerogerador. Abrangendo um período mínimo de
um ano, para capturar a variabilidade sazonal e mensal dos ventos, garantindo uma avaliação
completa do potencial eólico da região.

## 2.2.1 Circulação dos Ventos.

Os ventos podem ser classificados de acordo com a circulação global ou local. Os de cir-
culação global resultam da incidência solar desigual no planeta, variando conforme a distribui-
ção geográfica, o período do dia e a distribuição anual (MARTINS; GUARNIERI; PEREIRA,
2008). Já os ventos de circulação local são influenciados por características específicas de uma
região, como a topografia, a presença de corpos d’água e as diferenças de temperatura entre
áreas adjacentes.
A radiação solar absorvida de maneira desigual pela Terra é mais intensa próximo a
linha do Equador, gerando desequilíbrio em relação aos polos. Buscando o equilíbrio térmico,
as massas de ar quente e úmida presente na região dos trópicos movimentam-se para os polos,
enquanto as massas de ar fria e seca deslocam-se em sentido a linha do Equador, fechando o
ciclo, conforme visto na figura 2.4.

### Figura 2.4 – Formação dos ventos devido ao movimento das massas de ar

```
Figuras/Teorico/FormacaoDosVentos.png
```
```
Fonte: CEPEL (2001)
```

A rotação da Terra também influencia a formação dos ventos, criando padrões distintos:
no Hemisfério Norte e no Hemisfério Sul. De acordo com Reboita et al. (2012) e Pinto (2014),
devido à força de Coriolis, no Hemisfério Sul, o vento movimenta-se em direção do polo para o
equador sofrendo um deslocamento de sentido negativo ao eixo X. Ao modo que o vento indo
em direção ao polo oriundo do equador sofre um desvio positivo em relação ao eixo X, como
visto na figura 2.5.

### Figura 2.5 – Esquema representativo da circulação geral da atmosfera terrestre.

```
Figuras/Teorico/RegiÃţes de Circulacao.png
```
```
Fonte: Retirado (ROCHA et al., 2023) baseado em (REBOITA et al., 2012)
```
Devido à inclinação do eixo de rotação da Terra em relação ao plano de sua órbita ao
redor do Sol, há variações sazonais na intensidade e direção do vento em qualquer lugar do
planeta. Além do gradiente de pressão e da força de Coriolis (causada pela rotação da Terra), os
ventos atmosféricos também são afetados por forças gravitacionais, inércia do ar e fricção com
a superfície terrestre, resultando em turbulência.
Nas grandes altitudes, o ar se movimenta seguindo linhas de igual pressão, chamadas
isolinhas. Esse movimento de massas de ar a mais de 600 metros de altitude é conhecido como
ventos geotrópicos. Nessa altura, o fluxo de ar não é influenciado pela superfície terrestre.
Em altitudes mais baixas, as diferentes superfícies da Terra, como oceanos, terras e vegetação,
afetam significativamente o fluxo de ar devido a variações de pressão, diferentes níveis de ab-
sorção da radiação solar e umidade, influenciando o clima próximo à superfície. Esta região da
atmosfera, onde os ventos são afetados pela superfície, é chamada de camada limite.
Além de movimentos em escala global (Equador - polos), também há formação de ven-
tos em escala local, como "mar para o continente", "vales para as montanhas"e vice-versa.
As brisas marítimas e terrestres ocorrem em áreas costeiras devido às diferentes capaci-
dades de absorção de calor da terra e do mar. Durante o dia, a terra aquece mais rapidamente
que o mar, elevando a temperatura do ar sobre a terra e criando uma corrente de ar que sopra
do mar para a terra, conhecida como brisa marítima. À noite, a terra esfria mais rapidamente
que a água, resultando em uma corrente de ar que sopra da terra para o mar, chamada de brisa


terrestre, conforme demonstra a figura 2.6.

## Figura 2.6 – Circulação de ventos em escala local.(a) Brisa Marítima e (b) Brisa Terrestre.

```
Figuras/Teorico/brisaMaritima_brisaTerrestre.png
```
```
Fonte: Adaptado da Agência Nacional de Energia Elétrica (ANEEL) (2009)
```
Os ventos em regiões montanhosas e vales também seguem um padrão diário. Durante
o dia, o ar frio nas montanhas se aquece e sobe, permitindo que o ar mais frio dos vales flua
para substituir o ar quente que subiu. À noite, o processo se inverte: o ar frio das montanhas
desce para os vales, enquanto o ar quente dos vales sobe em direção às montanhas, como ilustra
a figura 2.7.

```
Figura 2.7 – Circulação de ventos em escala local.(a) Brisa do Vale e (b) Brisa da Montanha.
```
```
Figuras/Teorico/Brisa do Vale e da Montanha.png
```
```
Fonte: Adaptado da Agência Nacional de Energia Elétrica (ANEEL) (2009)
```
## 2.2.2 Classificação dos Movimentos Atmosféricos.

A formação dos ventos descrita anteriormente é apenas um exemplo dos muitos pro-
cessos que ocorrem na superfície da Terra, muitos dos quais são influenciados por variações
climáticas em diferentes escalas de tempo e espaço. Na meteorologia, há uma classificação
específica para esses movimentos atmosféricos.
Utilizando a classificação de Lutgens e Tarbuck, descrito em (LUTGENS, 2012) e exem-
plificado em (PINTO, 2014), existem três grandes escalas de comprimento na meteorologia:
microescala, mesoescala e macroescala. Esta última é subdividida em duas: escala sinóptica e
escala planetária (ou global), como destaca a tabela 2.1.


```
Tabela 2.1 – Principais características das escalas atmosféricas
Escala Tamanho Duração Fenômeno
Microescala Menos que 1 km Segundos a minutos Semanas a anos
Mesoescala 1 a 100 km Minutos a dias tempestades, torna-
dos e brisa terrestre
Macroescala - Sinóp-
tica
```
```
100 a 5000 km Dias a semanas Ciclones de latitudes
médias, anticiclones
e furacões
Macroescala - Plane-
tária
```
```
1000 a 40.000 km Semanas a anos Ventos alísios e ven-
tos do oeste
```
Os movimentos atmosféricos variam significativamente no tempo e no espaço, abran-
gendo intervalos que vão de segundos a meses e distâncias que variam de centímetros a mi-
lhares de quilômetros. As variações na velocidade do vento ao longo do tempo podem ser
classificadas, de acordo com (PINTO, 2014), em várias categorias:

```
a) Interanuais
```
- Período:Ocorrem em períodos superiores a um ano.
- Impacto:Podem ter um impacto significativo na produção de energia em turbinas
    eólicas de grande porte.
- Dados Necessários:Mínimo de 30 anos de dados para determinar valores climáti-
    cos de longo prazo. Pelo menos 5 anos de dados para estabelecer uma média anual
    confiável de velocidade do vento para uma região específica.
b) Anuais
- Período:Ocorrências devido a variações relevantes na média mensal ou sazonal da
velocidade do vento.
c) Diurnas
- Localização:Ocorrem em latitudes temperadas e tropicais.
- Período:Variam significativamente na escala diária.
- Causa:Devidas às diferenças de aquecimento na superfície terrestre durante o ciclo
diário de radiação solar.
- Exemplo:
* Aumento da velocidade do vento durante o dia.
* Diminuição da velocidade do vento durante as horas noturnas, da meia-noite ao
amanhecer.
d) De Curto Prazo


- Período:Geralmente ocorrem em períodos de 10 minutos ou menos.
- Exemplos:Rajadas de vento e turbulências.
- Turbulências:
    * Definição:Flutuações aleatórias na velocidade do vento que afetam a média
       geral.
    * Direções:
       · Longitudinal (ao longo da direção do vento).
       · Lateral (perpendicular ao vento).
       · Vertical.
- Rajadas:
    * Definição:Evento discreto dentro de um campo turbulento de vento.
    * Caracterização:Medição de quatro fatores principais:
       · Amplitude.
       · Duração.
       · Variação máxima da rajada.
       · Tempo de resposta.
- Impacto nas Turbinas Eólicas:Flutuações turbulentas na velocidade induzem for-
    ças cíclicas na estrutura da turbina, causando problemas de estresse e fadiga. Além
    de que, influenciam diretamente na operação, controle da turbina eólica e na qua-
    lidade da potência gerada. A figura 2.8(b) demostra uma variação típica de curta
    duração.

## 2.2.3 Forças Fundamentais que Regem o Movimento do Vento.

O vento é definido como o movimento das massas de ar na atmosfera. Este fenômeno
pode ser analisado como uma interação dinâmica entre várias parcelas de ar em movimento
contínuo. Esse movimento resulta da interação de diversas forças que se intensificam ou se
atenuam mutuamente. As principais forças envolvidas são cinco:

```
a) Força do Gradiente de Pressão
```
- Descrição:A força do gradiente de pressão é responsável por mover o ar das áreas
    de alta pressão para as áreas de baixa pressão. Este fenômeno é ocasionado pelo
    aquecimento desigual da superfície terrestre devido à radiação solar, criando zonas
    distintas de alta e baixa pressão. O desequilíbrio resultante impulsiona o movimento
    do vento, que naturalmente se desloca da região de maior para a de menor pressão.


### Figura 2.8 – Variações de velocidade ao longo do tempo na Dinamarca.

```
Figuras/Teorico/diurnal.png
```
(a) Variações de velocidade do vento Diurno, inter-
valo de três horas.

```
Figuras/Teorico/turbulencia10s.png
```
```
(b) Variações de velocidade do vento em curta dura-
ção.
Fonte: Danish Wind Industry Association (2000)
```
- Importância:Esta força é fundamental na formação de ventos e sistemas meteoro-
    lógicos.

```
b) Força de Coriolis
```
- Descrição: A força de Coriolis, ou também efeito de Coriolis, nomeada em ho-
    menagem ao matemático e engenheiro Gaspard Gustabe de Coriolis. É uma força
    inercial que é resultante da rotação da Terra, que causa movimentos circulares ou
    em espiral entre os polos e o equador. Seu efeito é percebido na deflexão dos ventos:
    para a direita no hemisfério norte e para a esquerda no hemisfério sul.
- Fórmula:Para efeito de estudo em energia eólica, de acordo com Pinto (2014), a
    formula da força de Coriolis é dada por:

```
Fco= 2 ΩVsinΦ, (2.1)
```
```
em que:
```
```
Fcoé a força de Coriolis,
Ωé a velocidade angular da Terra( 7. 29 × 10 −^5 rad/s),
Vé a velocidade da partícula(m/s),
Φé a latitude da partícula em graus(em graus).
```
- Importância: Esta força é crucial na formação de correntes de vento de grande


```
escala e fenômenos climáticos como ciclones.
```
```
c) Força Centrífuga
```
- Descrição:A força centrífuga é uma força aparente que atua sobre um corpo em
    rotação, afastando-o do centro de rotação.
- Fórmula:
    F=mω^2 r (2.2)
- Importância:Esta força é relevante em sistemas de referência rotativos e afeta o
    movimento de massas de ar em sistemas de baixa pressão.
d) Força de Atrito
- Descrição:A força de atrito é a força que resiste ao movimento relativo de superfí-
cies ou camadas de ar em contato.
- Importância: Esta força reduz a velocidade dos ventos próximos à superfície da
Terra e influencia a formação de padrões climáticos locais.
e) Força da Gravidade
- Descrição:A força da gravidade é a força que atrai os objetos em direção ao centro
da Terra.
- Importância:A gravidade é fundamental na manutenção da atmosfera terrestre e
afeta o movimento vertical do ar.

## 2.3 PERFIL DE VENTO

Conforme demonstrado por estudos em mecânica dos fluidos, a velocidade de um fluido
que flui próximo a uma superfície é reduzida a zero devido ao atrito entre o fluido e a superfície.
Ao observar o perfil de velocidade do fluido em relação à altura, percebe-se que a velocidade
aumenta de zero até alcançar a velocidade de escoamento (ν). Essa variação é mais acentuada
próxima à superfície e diminui em altitudes mais elevadas (BATCHELOR, 2000).
A região próxima à superfície, onde essa mudança rápida de velocidade ocorre, é deno-
minada camada limite, como ilustrado na Figura 2.9(a). Dentro dessa camada, o ar geralmente
apresenta turbulência, influenciada por fatores como densidade e viscosidade do fluido, rugosi-
dade da superfície e a presença de obstáculos (SCHLICHTING, 2000).
A potência contida no vento é função da densidade do ar, que, por sua vez, é influenciada
pela temperatura e pressão, ambas variáveis com a altura em relação ao solo. Como os aero-
geradores em operação comercial são instalados dentro da camada limite (até 150 m), é crucial


### Figura 2.9 – Esquema do perfil de velocidades sobre uma superfície plana.

```
Figuras/Teorico/velocidades sobre uma placa plana.png
```
```
(a) Alto efeito viscoso. (b) Baixo efeito viscoso.
Fonte: Passos (2014)
```
compreender a distribuição da velocidade do vento com a altura. Isso é importante porque a
velocidade do vento determina a produtividade de uma turbina instalada em uma torre de certa
altura e influencia a vida útil das pás do rotor, que são submetidas a cargas cíclicas devido à
turbulência do vento.
Os ventos turbulentos resultam da dissipação da energia cinética em energia térmica
através da criação e destruição de pequenas rajadas progressivas. Esses ventos são caracte-
rizados por várias propriedades estatísticas: intensidade, função densidade de probabilidade,
autocorrelação, escala integral de tempo e função densidade espectral de potência. Detalhados
com mais detalhes por Rohatgi e Nelson (1994), apud Manwell J.G. McGowan (2004).
Em estudos sobre o aproveitamento energético dos ventos, dois modelos matemáticos
são comumente utilizados para representar o perfil vertical dos ventos: a lei da potência e a lei
logarítmica (FADIGAS, 2011).
A lei da potência é um modelo simples derivado de estudos sobre a camada limite em
uma placa plana. É fácil de aplicar, mas não oferece alta precisão. A lei da potência é expressa
pela seguinte fórmula:

```
V=Vr
```
###### 

###### H

```
Hr
```
```
n
(2.3)
```
em que

- V= velocidade do vento na altura (H)
- Vr= velocidade do vento na altura de referência (medida)
- H= altura desejada
- Hr= altura de referência
- n= expoente da lei de potência


O expoentenrepresenta a influência da natureza do terreno no perfil vertical da velo-
cidade do vento e indica a correspondência entre o perfil do vento e o fluxo sobre uma placa
plana. Além da natureza do terreno, o expoententambém é influenciado pela hora do dia, tem-
peratura, parâmetros térmicos e mecânicos, e estação do ano. Em outras palavras, o expoente
nnão é constante e pode variar conforme as condições ambientais mudam ao longo dos meses.
A Tabela 2.2 apresenta alguns valores denpara diferentes tipos de terrenos planos (FADIGAS,
2011).

```
Tabela 2.2 – Fatornpara diferentes tipos de superfícies
DESCRIÇÃO DO TERRENO FATORn
Superfície lisa, lago ou oceano 0,10
Grama baixa 0,14
Vegetação rasteira (até 0,3m), árvores ocasionais 0,16
Arbustos, árvores ocasionais 0,20
Árvores, construções ocasionais 0,22 – 0,24
Áreas residenciais 0,28 – 0,40
Fonte: Hirata (1985) apud Dutra (2001)
```
É preciso ter cautela ao aplicar a lei da potência em regiões com relevo acidentado, como
terrenos montanhosos ou com depressões, e para alturas superiores a 50 metros.
O modelo baseado na lei logarítmica é mais adequado e realista para entender o per-
fil vertical do vento, pois considera que o fluxo atmosférico é altamente turbulento (TROEN;
PETERSEN, 1989; SILVA, 1999; FADIGAS, 2011). Este modelo utiliza o parâmetro "L –
comprimento de mistura", que incorpora a constante de Von KármánKce o comprimento de
rugosidadeZo, reconhecendo que a superfície da Terra nunca é completamente lisa.
Para altas velocidades, o perfil vertical do vento é descrito pela lei logarítmica:

```
V(z) =
v 0
Kcln
```
```
z
z 0
```
###### 

###### (2.4)

```
em que
```
- V(z)é a velocidade do vento na alturaz;
- z 0 é o comprimento de rugosidade que caracteriza a rugosidade do terreno;
- Kcé a constante de Von Kármán (Kc= 0 ,4);
- v 0 é a velocidade de atrito, relacionada com a tensão de cisalhamento na superfícieτe a
    densidade do arρpela expressãoτ=ρv^20 ;
       Para velocidades moderadas, o perfil vertical do vento se desvia do perfil logarítmico
quandozexcede algumas dezenas de metros, devido às forças de empuxo da turbulência. Nesse
caso, é necessário incluir parâmetros que descrevam o fluxo de calor na superfície. O perfil
vertical genérico do vento é dado por:


```
V(z) =vk^0
c
```
###### 

```
ln
```
###### 

```
z
z 0
```
###### 

```
−ψ
```
```
z
L
```
###### 

###### (2.5)

em queψé uma função dependente da estabilidade, sendo positiva para condições instáveis e
negativa para condições estáveis. O comprimento de misturaLé definido por:

```
L=T^0 cpv
```
(^30)
kcgH 0 (2.6)
em que:

- T 0 = temperatura absoluta
- H 0 = fluxo de calor na superfície
- cp= calor específico do ar à pressão constante
- g= aceleração da gravidade
    Para estimar a velocidade do vento de uma altura de referênciaZrpara outro nível de
alturaZ, utiliza-se a seguinte equação:

```
V(z)
V(zr)=
```
```
ln
```
###### 

```
z
z 0
```
###### 

```
ln
```
```
z
zr
0
```
######  (2.7)

A Tabela 2.3 apresenta os valores do comprimento de rugosidade para diferentes tipos
de terrenos.

```
Tabela 2.3 – Valores de comprimentos de rugosidade para diferentes terrenos
DESCRIÇÃO DO TERRENO z 0 (mm)
Liso, gelo, lama 0,01
Mar aberto e calmo 0,20
Mar agitado 0,50
Neve 3,00
Gramado 8,00
Pasto acidentado 10,00
Campo em declive 30,00
Cultivado 50,00
Poucas árvores 100,00
Muitas árvores, poucos edifícios, cercas 250,00
Florestas 500,00
Subúrbios 1.500,00
Zonas urbanas com edifícios altos 3.000,00
```
Fonte: Fadigas (2011) adaptado de Manwell J.G. McGowan (2004).


## 2.4 POTÊNCIA GERADA PELOS VENTOS

O movimento do ar gera energia, conhecida como energia eólica, que é uma forma
de energia cinética. Devido à natureza estocástica do vento, sua direção e velocidade variam
constantemente. A potência, em termos físicos, é a medida da quantidade de trabalho realizado
por unidade de tempo. Para estimar a potência do vento, o processo pode ser dividido em duas
etapas: primeiramente, avaliando a energia contida no vento e, em seguida, determinando a
fração dessa energia que será convertida em energia mecânica.

## 2.4.1 Avaliação da Energia Contida no Vento.

Para estimar a energia cinética, iremos inicialmente considerar o exemplo de um cilin-
dro, conforme ilustrado na Figura 2.10. Toda a quantidade de ar que se desloca a uma dada
velocidade (v) atravessa perpendicularmente o cilindro.

### Figura 2.10 – O fluxo de massa de ar com velocidadevatravés de uma áreaA(circular).

```
Figuras/Teorico/Fluxo de massa de ar com velocidade V atravÃľs de uma Ãąrea A.jpeg
```
```
Fonte: Carvalho (2003)
```
Supondo que a massa de ar que passa pelo cilindro sejam, a energia cinética (Ec) de
uma massa de ar é dada por:

Ec=^12 mv^2 (2.8)
Essa equação mostra que a energia cinética aumenta com o quadrado da velocidade do
vento. Em termos mais simples, ao duplicar a velocidade do vento de um ventilador doméstico,
a energia cinética do vento quadruplica. Para encontrar a potência do vento, devemos calcular
como essa energia cinética varia ao longo do tempo, o que é feito pela derivada da energia
cinética em relação ao tempo. Assim, a potência (P) disponível do vento é:

```
P=∂∂Etc=mv
```
```
2
2 (2.9)
```

```
Para tornar a equação (2.9) mais prática, substitui-semporρAv, resultando em
```
P=^12 ρAv^3 (2.10)
Essa equação fornece uma boa análise do fluxo de potência eólica. Pode-se também
interpretá-la como a quantidade de energia por uma dada área:

```
P
A=
```
###### 1

```
2 ρv
```
(^3) (2.11)
sendo as variáveis

- P: potência disponível do vento (W)
- m: fluxo de massa de ar (kg/s)
- ρ: densidade do ar (kg/m^3 )
- A: área da seção transversal do cilindro atravessada pelo vento (m^2 )
- v: velocidade do vento (m/s)
- Ec: energia cinética do vento (joules/s)
- PA: densidade de potência (W/m^2 )
    A análise da equação (2.10) revela que a potência disponível no vento é diretamente
proporcional ao cubo da velocidade do vento. Se a velocidade do vento dobrar, a potência
aumentará oito vezes. A densidade de potênciaPA representa a potência contida no vento que
atinge a parte frontal da turbina.
A densidade do ar depende da pressão (P), da temperatura absoluta (T) e da constante
do gás (R), conforme a equação (2.12), que para efeitos de analiseρ= 1 .225 kg/m^3.

```
ρ=RP·T (2.12)
```
Considerando a analise para aplicação de uma turbina eólica de eixo horizontal, como
a ilustrada na Figura 2.11, a área varrida pelas pás pode ser determinada a partir da seguinte
equação:

```
A=π 4 D^2 (2.13)
```
em queDé o diâmetro do rotor.
A determinação da área para a turbina de eixo vertical modelo Darrieus, mostrada na
figura 2.12, é mais complexa, pois envolve integrais elípticas. No entanto, ao aproximar o for-
mato das pás a uma parábola, a seguinte expressão simplificada pode ser utilizada (FADIGAS,
2011):


### Figura 2.11 – Área varrida pelas pás de uma turbina de eixo horizontal.

```
Figuras/Teorico/areaTurbina.png
```
```
Fonte: Fadigas (2011) adaptado de Burton et al. (2001).
```
A=^23 ·(largura máxima do rotor até o centro)×(altura do rotor) (2.14)
Os aspectos mais importantes, destaca Fadigas (2011), são que a potência do vento
depende da área de captação e é proporcional ao cubo de sua velocidade. Pequenas variações
na velocidade do vento podem resultar em grandes mudanças na potência.
A figura 2.13 demonstra como a densidade de potência do vento varia com a velocidade.
Por exemplo, na figura 2.13 é possível ver em destaque para uma velocidade de 8 m/s com a
densidade de potência (ao nível do mar) de 314 W/m². Quando a velocidade dobra para 16 m/s,
a densidade de potência aumenta para 2.509 W/m², ou seja, oito vezes maior. Isso enfatiza a
importância de obter dados altamente precisos.

## 2.4.2 Determinação da Energia Convertida em Potência Mecânica.

A equação (2.10) refere-se a potência contida nos ventos ou potência eólica determinada
para um cilindro, em função da massa específica do ar, área de captação e velocidade do vento.
Entretanto, nesta estimativa a velocidade não sofre pertubação, ou seja, é uma estimativa de
potência antes de atingir as pás do rotor. Em cenário real, esse vento ao encontrar as pás do
aerogerador terá o seu perfil modificado, como ressaltado na figura 2.14.
O vento, ao passar pelo aerogerador, tem uma parte de sua potência convertida em potên-
cia mecânica. Como resultado dessa conversão, a velocidade inicial do vento diminui durante a
passagem pelo aerogerador, e a área de fluxo de ar aumenta. Utilizando a equação da continui-
dade, sabemos que o fluxo de massa ̇mpermanece constante, conforme destacado na equação
(2.15). Além disso, a potência mecânica (Pmec) gerada é igual à diferença entre a potência de
entrada (Pin) e a potência de saída (Pout), conforme expresso na equação (2.16).


### Figura 2.12 – Modelo de Darrieus.

```
Figuras/Teorico/modelo Darrieus.jpeg
```
```
Fonte: Quora (2024).
```
```
ρ 1 A 1 v 1 =ρ 2 A 2 v 2 =m ̇ (kg/s) (2.15)
```
```
Pmec=Pin−Pout (2.16)
As potências de entrada e saída podem ser expressas a partir de (2.10)
```
```
Pin=^12 ρA 1 v^31 (2.17)
```
```
Pout=^12 ρA 2 v^32 (2.18)
```
assim, substituindo em (2.16), tem-se

```
Pmec=^12 ρA 1 v^31 −^12 ρA 2 v^32 =^12 ρ(A 1 v^31 −A 2 v^32 ) (2.19)
```
em que, a potência mecânicaPmecextraída é equivalente à diferença entre o fluxo de ar antes e
após a passagem pela turbina. Aplicando a equação da continuidade (2.15) em (2.19), obtém-se:

```
Pmec=^1
2
ρA 1 v 1 (v^21 −v^22 ) =^1
2
m(v^21 −v^22 ) (2.20)
```

### Figura 2.13 – Curva de potência do vento em função de sua velocidade.

```
Figuras/Teorico/Cubo de Velocidade do Vento.png
```
```
Fonte: Danish Wind Industry Association (2000).
```
### Figura 2.14 – Passagem de ar por uma turbina eólica de eixo horizontal.

```
Figuras/Teorico/Fluxo de ar atravÃľs de uma turbina eÃşlica de eixo horizontal.png
```
```
Fonte: Rocha et al. (2023).
```
## 2.5 CURVA COEFICIENTE DE PERFORMANCE (Cp)

A curvaCp, ou curva do coeficiente de potência, é uma representação fundamental na
análise de desempenho de turbinas eólicas, ilustrando a eficiência com que uma turbina converte
a energia cinética do vento em energia mecânica no eixo da turbina. O coeficiente de potência
Cpé adimensional e varia em função da razão de velocidade das pontas das pásλ(tip speed
ratio, TSR), que é uma medida da velocidade linear das pontas das pás relativa à velocidade do
vento.
Segundo Betz (1926), uma turbina eólica ideal reduz a velocidade do vento a 2/3 da
velocidade original, limitando a potência capturável a aproximadamente 59% da potência total
disponível. Esse limite é conhecido como o limite de Betz. Assim aplicando o conceito a


equação 2.10 da potência do extraída do vento, tem-se:

```
Pmec=^12 CpρAv^3 (2.21)
```
o coeficiente de potência em termos isolados:

```
Cp= 1 Pmec
2 ρAv^3
```
###### (2.22)

- Pmecrepresenta a potência mecânica produzida pela turbina,
- ρé a densidade do ar,
- Acorresponde à área alcançada pelas pás da turbina,
- vindica a velocidade do vento ao entrar na turbina.
    Em turbinas eólicas reais, o coeficiente de performance varia tipicamente de acordo com
o TSR (λ), dada pela equação, e o ângulo de passo das pás.

```
λ=ωR
v
```
###### (2.23)

sendo que

- ω: representa a velocidade angular do rotor, medida em radianos por segundo [rad/s],
- R: indica o raio das pás do rotor, em metros [m],
- v: denota a velocidade do vento, em metros por segundo [m/s].
    O comportamento da curva Cp é influenciado pela aerodinâmica das pás, pelas caracte-
rísticas do rotor, e pelas condições operacionais da turbina. Em turbinas com controle ativo de
passo, o ângulo das pás (β) é ajustado para maximizarCppara diferentes velocidades do vento
e para proteger a turbina em condições de vento forte.
Modelos matemáticos, como os desenvolvidos por Heier (2014) e por Slootweg, Polin-
der e Kling (2003), utilizam séries de equações, (2.23) - (2.24), para estimarCpem função do
TSR e do ângulo de passo das pás (β). Esses modelos são cruciais para o design otimizado
e a operação eficiente de turbinas eólicas, permitindo que operadores e designers ajustem as
turbinas para operar próximo ao máximo coeficiente de performance sob várias condições de
vento.

```
Cp(λ,β) =c 1
```
###### 

```
c 2
λi−c^3 β−c^4 βc^5 −c^6
```
###### 

```
e−
```
```
c 7
λi (2.24)
```
```
λi= 1 1
λ+c 8 β−
```
```
c 9
β^3 + 1
```
###### (2.25)


βé o ângulo de passo das pás.
λé o coeficiente de velocidade.
Os coeficientesciestão delineados na Tabela 2.4, conforme descrito por Heier (2014),
Slootweg, Polinder e Kling (2003) e Raiambal e Chellamuth (2002). A metodologia para esti-
mar a eficiência aerodinâmica sugerida por Heier e Raiambal é aplicável universalmente, abran-
gendo tanto turbinas de velocidade fixa quanto variável. Por outro lado, Slootweg, Polinder e
Kling (2003) adaptaram os parâmetros nas equações (2.24) e (2.25) para refletir as particula-
ridades dessas duas categorias de turbinas eólicas, permitindo uma representação mais precisa
das curvas de desempenho em simulações computacionais.

```
Tabela 2.4 – Parâmetros utilizados para o cálculo doCp(λ,β)segundo diferentes
autores/modelos
```
```
Modelo c 1 c 2 c 3 c 4 c 5 c 6 c 7 c 8 c 9
Heier (2014) 0.5 116 0.4 0 – 5 21 0.08 0.035
Raiambal (2002) 0.5 116 0.4 0 – 5 16.5 0.089 0.035
Velocidade Const. 0.44 125 0 0 0 6.94 16.5 0 − 0. 002
Velocidade Variável 0.73 151 0.58 0.002 2.14 13.2 18.4 − 0. 02 − 0. 003
```
Fonte: Vian (2021).

```
Inserindo os valores da Tabela 2.4 em (2.24) e (2.25), tem-se conforme Heier (2014)
```
```
Cp(λ,β) = 0. 5
```
###### 

###### 116

```
λi −^0.^4 β−^5
```
###### 

```
e−
```
(^21) λ
i (2.26)
λi= 1 1
λ+ 0. 08 β−
0. 035
β^3 + 1

###### (2.27)

```
De acordo com Raiambal e Chellamuth (2002), obtêm-se
```
```
Cp(λ,β) = 0. 5
```
###### 

###### 116

```
λi −^0.^4 β−^5
```
###### 

```
e−
```
(^16) λ. 5
i (2.28)
λi=

###### 1

```
1
λ+ 0. 089 −
0. 035
β^3 + 1
```
###### (2.29)

Por fim, para os paramentos estabelecidos por Slootweg, Polinder e Kling (2003), tem-se
para velocidade variável

```
Cp(λ,β) = 0. 73
```
###### 

###### 151

```
λi −^0.^58 β−^0.^002 β
```
2. (^14) − 13. 2

###### 

```
e−
```
(^18) λ. 4
i (2.30)
λi= 1 1
λ− 0. 02 β−
− 0. 003
β^3 + 1

###### (2.31)


Nas figuras 2.15, 2.16 e 2.17, são apresentadas as curvas de potência para três metodo-
logias de eficiência diferentes, simuladas via script no MATLAB para a turbina do projeto. A
análise dos gráficos destacou a eficiência típica de 45% para aerogeradores horizontais de três
pás, valor comumente observado em turbinas desse tipo (SMART SERVO, 2024).

```
Figura 2.15 – Coeficiente de Potência (Cp) versus Relação de Velocidade na Ponta (λ) para
ângulo de passoβ, para equações (2.28) e (2.29).
```
```
Figuras/Teorico/graph1.png
```
```
Figura 2.16 – Coeficiente de Potência (Cp) versus Relação de Velocidade na Ponta (λ) para
ângulo de passoβ, para equações (2.30) e (2.31).
```
```
Figuras/Teorico/graph2.png
```
## 2.6 SÉRIE TEMPORAL DO VENTO

Neste capitulo será apresentado a modelagem da série temporal de vento. Tal implemen-
tação torna-se necessária pois a série temporal de vento representa a variação da velocidade e


```
Figura 2.17 – Coeficiente de Potência (Cp) versus Relação de Velocidade na Ponta (λ) para
ângulo de passoβ, para equações (2.26) e (2.27).
```
```
Figuras/Teorico/graph3.png
```
seu comportamento ao longo do tempo. Toda a modelagem e simulação foi feita com o uso do
software MATLAB/SIMULINK. O desenvolvimento da série temporal será dividido em duas
partes: Vento e Fluxo e a Modelagem de Séries Temporais com o Filtro de Von Karman.
As séries temporais de vento são registros contínuos da velocidade e direção do vento
que desempenham um papel crucial no processo de conversão eólica. Essas séries permitem a
análise de padrões históricos e a previsão de flutuações futuras essenciais para a operação efici-
ente de aerogeradores. A abordagem ’Vento e Fluxo’ divide o vento em categorias, facilitando
a compreensão dos comportamentos ruidosos presentes nele. Na próxima seção será abordado
o passo a passo para a representação da série temporal.

## 2.6.1 Vento e Fluxo.

Dividir o fluxo de vento em categorias, como vento médio, turbulência e ondas, ajuda a
entender e prever o comportamento do vento sob diversas condições atmosféricas. Cada uma
dessas categorias pode ocorrer isoladamente ou simultaneamente, influenciando de maneira
distinta a camada limite atmosférica, onde ocorre o transporte de calor, umidade e poluentes. A
representação das três categorias pode ser vista na figura 2.18.

- Vento Médio
    - Transporte Horizontal Rápido (Advecção):O vento médio é responsável por um
       transporte horizontal muito rápido conhecido como advecção, que é crucial para a
       movimentação de massas de ar e suas propriedades dentro da camada limite.
    - Velocidade do Vento: Na camada limite, ventos horizontais variam geralmente


```
Figura 2.18 – Fluxo de ar decomposto em três categorias.Ué o componente velocidade do
vento ao longo do tempot.
```
Figuras/Teorico/vento_sub3_fonte.png

```
Fonte: (STULL, 1988)
```
```
entre 2 e 10 m/s. Esses ventos são essenciais para a dispersão de poluentes e o
transporte de calor e umidade.
```
- Influência da Fricção:A fricção com a superfície da Terra reduz a velocidade do
    vento médio perto do solo. Esta redução é mais pronunciada nas proximidades do
    solo devido ao aumento do arrasto friccional.
- Ondas
- Presença na Camada Limite Noturna: Ondas atmosféricas são frequentemente
observadas durante a noite na camada limite. Elas se formam devido a variações de
temperatura e vento e podem se propagar a partir de fontes distantes como tempes-
tades ou explosões.
- Transporte de Calor e Poluentes:Embora as ondas transportem pouco calor, umi-
dade e outros escaladores (como poluentes), são muito eficazes no transporte de
momento e energia.
- Geração de Ondas:Essas ondas podem ser geradas localmente por cisalhamentos
do vento médio ou pelo fluxo de ar sobre obstáculos como montanhas ou edifícios.
Elas podem se propagar a partir de fontes distantes e influenciar a dinâmica da ca-
mada limite.
- Turbulência


- Caracterização: A turbulência é visualizada como redemoinhos irregulares, cha-
    mados vórtices, e é um fenômeno superposto ao vento médio. Ela consiste em
    muitos vórtices de tamanhos diferentes que se sobrepõem.
- Geração de Turbulência:Grande parte da turbulência na camada limite é gerada
    por forças no solo como o aquecimento solar do solo, que cria termas de ar quente
    que sobem, e o arrasto friccional do ar ao passar sobre o solo. Obstáculos como
    árvores e edifícios também podem defletir o fluxo de ar, criando áreas de turbulência
    adjacentes e a jusante dos obstáculos.
- Espectro de Turbulência: A intensidade relativa dos diferentes vórtices define o
    espectro de turbulência, que descreve a distribuição de energia entre os vórtices de
    diferentes tamanhos.

Individualmente, cada categoria representa um efeito, ação ou força que atua sobre o
fluxo de ar. Esta subdivisão do vento permite gerar uma representação matemática do vento
ruidoso. Assim, de acordo com o comportamento, é possível estipular as seguintes equações:

```
vvento turbulento=
```
```
p
−2 lnx 1 (2.32)
```
```
vvento ondulante=sin( 2 πx 2 ) (2.33)
Representado no MATLAB/SIMULINK nos gráficos da Figura 2.19.
```
## 2.6.2 Modelagem de Séries Temporais com o Filtro de Von Karman.

Para modelar adequadamente as séries temporais do vento, é comum utilizar técnicas
estatísticas e matemáticas, como o filtro de Von Karman, que ajuda a simular a turbulência do
vento. Este filtro é especialmente útil para representar as características caóticas e não lineares
do vento, que são críticas para a precisão das simulações. Baseando-se em Koch (2010) para o
desenvolvimento do modelo.
Para efeito de análise, podemos considerar que a série temporal do vento é composta
por dois termos: um constante e outro variável, sendo respectivamente a velocidade média do
vento (v) e a série temporal de turbulência do vento (vt):

```
v(t) =v+vt (2.34)
```
A parcela que representa a série temporal de turbulência do ventovtpode ser calculada
utilizando o filtro de Von Karman, que é expresso pela função de transferência:


### Figura 2.19 – Representação do vento em velocidade média, ondulação e turbulência.

Figuras/Teorico/vento_sub3.png


```
GKarman(s) = Kf
( 1 +sTf)^5 /^6
```
###### (2.35)

```
Em que:
```
- Kf é o ganho do filtro;
- Tf é a constante de tempo.
    Quando ativado por uma fonte de ruído gaussiano normalizado, a aproximação do filtro
de Von Karman por meio de uma função de transferência racional se torna prática. A equação
(2.36) e a Figura 2.20 representam esta aproximação.

```
G′karman(s) =Kf(T (m^1 Tfs+^1 )
fs+^1 )(m 2 Tfs+^1 )
```
###### (2.36)

sendo os valores das constantes de Von Karman, dados por

- m 1 = 0 .4;
- m 2 = 0 .25.

### Figura 2.20 – Aproximação do Filtro de Von Karman nosoftwareMATLAB/SIMULINK

```
Figuras/Teorico/Aprox_Filtro_VonKarman.png
```
Segundo Stannard e Bumby (2007), a constante de tempoTf está vinculada às especifi-
cidades do ambiente onde a turbina está instalada e varia inversamente com a velocidade média
do vento conforme a equação:

```
Tf=Lturbv (2.37)
```

Em queLturbrefere-se ao comprimento de turbulência, um fator influenciado pelas ca-
racterísticas físicas do terreno que não dependem do tipo de turbina utilizada. A determinação
precisa deLturbpode ser complexa devido à necessidade de considerar múltiplos fatores ambi-
entais e topográficos.
Para simplificar essa estimativa, Martins (2010) propôs uma aproximação prática em
queLturbpode ser calculado como 6.5 vezes a altura da torre da turbinah. Assim, pode-se dizer
que:

```
Lturb= 6. 5 h (2.38)
```
representado na Figura 2.21.

```
Figura 2.21 – Calculo da constante de tempoTfdo Filtro simulado nosoftware
MATLAB/SIMULINK
```
```
Figuras/Teorico/constante_de_tempoTf.png
```
O coeficienteKf, conhecido como ganho do filtro, é influenciado pela constante de
tempoTf e pela frequência de amostragem utilizada nas simulações. O ajuste dessas constan-
tes, que são fundamentais no modelo de Von Karman, pode ser observado na Figura 2.22. A
expressão para calcularKf é dada por

```
Kf=
```
s
2 πTf
B(x,y)Ts (2.39)
Em queB(x,y)representa a função beta de Euler, componente crucial para a normaliza-
ção do filtro em relação à distribuição de frequências.
Um aspecto crucial relacionado ao ganhoKfé que ele precisa ser calculado de maneira
a preservar o desvio padrão do sinal de saída como unitário. A frequência de amostragemTs
definida neste estudo é 0.04 segundos.
O ruído utilizado para excitação do filtro é dado pelas equações utilizadas no vento
turbulento (2.32) e vento ondulante (2.33), assim o ruído é dado por:

```
r=
```
```
p
−2 ln(x 1 )sin( 2 πx 2 ) (2.40)
```
e representado na figura 2.23.


##### Figura 2.22 – GanhoKfdo Filtro de Von Karman simulado nosoftwareMATLAB/SIMULINK

Figuras/Teorico/GanhoDoFiltro_Kf.png

##### Figura 2.23 – O ruído utilizado para ativar o filtro gerado nosoftwareMATLAB/SIMULINK

```
Figuras/Teorico/ruidoGaussiano.png
```

Este ruído, tem um desvio padrão unitário e segue uma distribuição gaussiana, e é gerado
a partir de duas variáveis aleatóriasx 1 ex 2 , ambas com distribuição uniforme no intervalo de
0 a 1. Esse método de geração de ruído é fundamental para simular com precisão a natureza
aleatória e estocástica da turbulência do vento em modelos de séries temporais.
O desvio padrão da turbulênciaDpvaria em função do coeficiente de turbulência longi-
tudinalKpe da velocidade média do ventov, seguindo a relação

```
Dp(vt) =Kpv (2.41)
```
O coeficienteKp, também chamado de fator de turbulência, é determinado pelas caracte-
rísticas específicas do terreno. Conforme Stannard e Bumby (2007), foram compilados valores
estimados paraKppara diversos tipos de terreno demonstrados na Tabela 2.5

```
Tabela 2.5 – Fatores de turbulência para diferentes terrenos
Tipo de Terreno Kp
Áreas Litorâneas 0.123
Lagos 0.145
Lugares Abertos 0.189
Áreas em construção 0.285
Centros Urbanos 0.434
Fonte: Adaptado de Koch (2010)
```
Esta tabela é essencial para entender como variáveis ambientais influenciam a turbulên-
cia do vento em diferentes locais. Assim, adotando todas as equações e fatores topográficos,
tem-se o modelo da serie temporal no MATLAB/SIMULINK representando na Figura 2.24 e a
serie temporal gerada na Figura 2.25.

### Figura 2.24 – Série Temporal de Vento modelado nosoftwareMATLAB/SIMULINK

```
Figuras/Teorico/SerieTemporaldeVento.png
```

##### Figura 2.25 – Resultado do modelo da Série Temporal de VentosoftwareMATLAB/SIMULINK

```
Figuras/Teorico/serie temporal de vento_.png
```
## 2.7 PRINCÍPIOS DE FUNDAMENTO DAS TURBINAS EÓLICAS

As turbinas eólicas, comumente conhecidas como aerogeradores, são dispositivos proje-
tados para otimizar a captação da energia cinética do vento, transformando-a em energia elétrica
utilizável. O processo de conversão inicia-se quando o vento interage com as pás do rotor, que
giram devido à força do vento. Essa rotação segue o princípio da conservação de energia, con-
vertendo a energia cinética em energia mecânica no rotor, que, por sua vez, é transmitida ao
gerador elétrico.
Na figura 2.26, observa-se um esquema detalhado desse processo. O vento impulsiona
as pás da turbina, gerando energia mecânica que é transmitida por meio de um multiplicador
mecânico, responsável pela conversão de torque e velocidade. Essa energia mecânica elevada é
então convertida em energia elétrica no gerador. A conversão de energia mecânica em elétrica
é acompanhada por um sistema de controle e proteção eletrônica, garantindo a segurança e
eficiência da operação. Em seguida, um transformador elevador ajusta a tensão da energia
gerada para níveis compatíveis com a rede elétrica, facilitando a distribuição.
Historicamente, diversos tipos de turbinas foram experimentados, incluindo configura-
ções de eixo horizontal e vertical, com várias quantidades de pás. Contudo, para geração em
grande e médio porte, predominam atualmente as turbinas de eixo horizontal, com estrutura
robusta, três pás e geradores de indução, que também possuem alinhamento ativo, como exem-
plificado na imagem 2.27. Apesar de sua popularidade, algumas características dessas turbinas,
como o controle do ângulo de passo, ainda são alvo de discussões técnicas e ajustes para apri-
morar a eficiência da captação de energia e a resposta às condições variáveis do vento.
Além disso, existem vários aspectos que caracterizam um aerogerador, entre eles a to-
pologia, o tamanho, o nível de potência, a eficiência energética e a localização.


### Figura 2.26 – Esquema abrangente de operação de um aerogerador.

```
Figuras/Teorico/Esquema geral de funcionamento de um aerogerador.png
```
```
Fonte: Pavinatto (2005)
```
## 2.8 COMPONENTES DE AEROGERADOR DE EIXO HORIZONTAL

Os aerogeradores de eixo horizontal são os mais comuns e amplamente utilizados no
setor de energia eólica devido à sua eficiência e capacidade de gerar grandes quantidades de
energia. A estrutura básica de um aerogerador de eixo horizontal é composta por diversos
componentes essenciais que trabalham em conjunto para converter a energia cinética do vento
em energia elétrica.

```
I Pás: Ou lâminas, utilizando os mesmos perfis aerodinâmicos das asas de aviões, elas
captam a energia cinética produzida pelos ventos e transferem para o rotor. Compostas
geralmente de materiais leves e resistentes, como fibra de vidro ou carbono.
II Rotor: Composto pelas pás e pelo cubo do rotor, o rotor é responsável por converter a
energia cinética do vento em energia mecânica.
```
```
III Nacele: É o compartimento instalado no alto da torre, sendo ele o responsável por abrigar,
suportar e proteger os principais componentes do sistema de geração de energia, como
gerador, eixo e demais acoplamentos (de acordo com a configuração).
```
```
IV Multiplicador de velocidade: Ou caixa de engrenagens. Utilizado em sistema com ge-
radores assíncronos, sua principal funcionalidade é transformar uma rotação lenta em
uma rotação rápida, geralmente de um intervalo de 10-60 rpm para valores próximos a
1200-1800 rpm.
```

### Figura 2.27 – Esquema de Turbina Eólica Moderna.

```
Figuras/Teorico/Construtivos.png
```
Fonte: CENTRO BRASILEIRO DE ENERGIA EÓLICA -– CBEE (2000)


```
V Acoplamento elástico: É um tipo de acoplamento utilizado para conectar eixos rotativos.
Sua função é transmitir o torque de um eixo a outro, absorvendo choques, vibrações e
desalinhamento.
VI Gerador Elétrico: Responsável pela conversão de energia mecânica em energia elétrica.
Sendo mais comumente utilizado gerador de indução (ACKERMANN, 2005).
VII Sensores de vento: Esses sensores monitoram as condições do vento, medindo a veloci-
dade e a direção, por sua vez, comunicando ao mecanismo de orientação direcional.
VIII Controle de giro: Também conhecido como sistema deyaw, é o componente responsá-
vel pelo posicionamento da nacele, alinhando-a em direção do vento e maximizando a
captação.
IX Torre de sustentação: Estrutura vertical responsável por suporta a nacele e o rotor, permi-
tindo a captação dos ventos em uma altura maior.
X Sistema de Freio: O sistema de freio é empregado para parar ou controlar a rotação do
rotor em condições específicas, como durante a manutenção, em situações de emergência
ou quando há vento excessivo.
XI Sistema de controle: Responsável por garantir a segurança e otimizar a potência gerada
através do controle de rotação, acionamento dos freios e/ou controle de passo. Além de,
garantir a qualidade da energia gerada.
```
## 2.9 PERFIL AERODINÂMICO

ANALISAR E COMENTAR - Analisar e comentar
O perfil aerodinâmico das pás de um aerogerador desempenha um papel fundamental
na eficiência e na capacidade de geração de energia do sistema. As pás dos aerogeradores são
projetadas para transformar a energia cinética do vento em energia mecânica de rotação, que,
por sua vez, é convertida em eletricidade pelo gerador. Para maximizar a eficiência dessa con-
versão, é essencial que o design do perfil das pás considere uma série de fatores aerodinâmicos,
como a forma e o ângulo de ataque da superfície, a curvatura e o alongamento.
Um bom projeto de perfil aerodinâmico visa maximizar o coeficiente de sustentação e
minimizar o coeficiente de arrasto em uma ampla faixa de velocidades de vento e ângulos de
operação. Esse equilíbrio entre sustentação e arrasto é crucial, pois permite que as pás gerem
a força de rotação necessária com menor resistência, contribuindo para uma maior eficiência
energética do aerogerador, como destacado na figura 2.28. Além disso, o perfil deve ser re-
sistente a condições extremas e oferecer boa resposta a variações de intensidade e direção do
vento, otimizando o desempenho e a durabilidade do aerogerador.


### Figura 2.28 – Aspectos de um perfil aerodinâmico.

```
Figuras//Teorico/PerfilAerodinamico01.png
```
```
Fonte: JUNIOR e RANGEL (2012)
```
- Bordo de Ataque e Bordo de Fuga:Referem-se, respectivamente, aos pontos dianteiro
    e traseiro do aerofólio. O bordo de ataque é o ponto inicial de contato do ar com o
    perfil, enquanto o bordo de fuga é o ponto final, onde o ar se desprende da superfície do
    aerofólio.
- Extradorso e Intradorso:Estas são as superfícies externas do aerofólio, sendo o extra-
    dorso a superfície superior e o intradorso a superfície inferior, que se estendem do bordo
    de ataque até o bordo de fuga.
- Linha de Corda: Trata-se de uma linha imaginária que conecta o bordo de ataque ao
    bordo de fuga. Essa linha serve como referência para a análise de diversos parâmetros
    geométricos e aerodinâmicos do aerofólio.
- Corda:Corresponde ao comprimento do segmento de reta que une os pontos do bordo
    de ataque e do bordo de fuga. É uma medida fundamental na caracterização geométrica
    do aerofólio e influencia diretamente suas propriedades aerodinâmicas.
- Linha de Curvatura: Refere-se ao lugar geométrico dos pontos equidistantes entre o
    extradorso e o intradorso, medidos perpendicularmente à linha de corda. A linha de
    curvatura define a forma média do aerofólio, sendo útil para determinar o comportamento
    aerodinâmico e o perfil de pressão ao longo do aerofólio.
- Camber:Denomina-se "camber"à assimetria entre as superfícies superior (extradorso) e
    inferior (intradorso) de um aerofólio. Essa assimetria é responsável por gerar sustentação,
    uma vez que altera a distribuição de pressão ao redor do perfil.


### Figura 2.29 – Escoamento ao longo do perfil.

```
Figuras//Teorico/EscoamentoCirculandoOPerfil.png
```
```
Fonte: Peixoto e Rodrigues (2009)
```
### Figura 2.30 – Forças Aerodinâmicas

```
Figuras//Teorico/EsforÃğos AerodinÃćmicos.png
```
```
Fonte: Weltner e outros (2001)
```
## 2.9.1 Coeficientes e Parâmetros Aerodinâmicos.

Quando um perfil aerodinâmico é imerso em um escoamento de fluido, o ar (ou outro
fluido) que se movimenta em sua direção se divide em duas correntes principais. Como pode
ser visto na figura 2.29, uma dessas correntes passa sobre a superfície superior do perfil, co-
nhecida comoextradorso, enquanto a outra corrente circula pela superfície inferior, chamada
intradorso.
Essa divisão do fluxo de ar ao redor do perfil cria diferenças de pressão entre o extradorso
e o intradorso. Normalmente, devido à curvatura do perfil, o fluido que passa pelo extradorso
se move mais rapidamente do que aquele que passa pelo intradorso. Segundo o princípio de
Bernoulli, essa diferença de velocidade gera uma pressão menor no extradorso em comparação
ao intradorso, resultando em uma força de sustentação que age sobre o perfil e uma força de
arrasto que age perpendicular a ela, como pode ser visualizado na figura 2.30.
Para calcular a Força de SustentaçãoLe Força de ArrastoDem um perfil aerodinâmico,


utiliza-se repectivamente a Equação 2.42 e 2.43, conforme descrito por Halliday, Resnick e
Walker (1996):

```
L=^12 ·ρ·V^2 ·AS·CL (2.42)
```
```
D=^12 ·ρ·V^2 ·AS·CD (2.43)
Em que:
```
- ρ: representa a densidade do fluido ao redor do perfil;
- V: é a velocidade relativa do escoamento;
- As: é a área de superfície do perfil;
- CL: é o coeficiente de sustentação, que depende da forma e do ângulo de ataque do perfil.
- CD: é o coeficiente de Arrasto, que indica a resistência ao movimento do perfil dentro do
    fluido.

Essa expressão demonstra que a força de sustentação aumenta com a densidade do
fluido, com o quadrado da velocidade do escoamento e com o coeficiente de sustentação, que
reflete as características aerodinâmicas do perfil. Quanto maior o coeficiente de sustentação,
maior a capacidade do perfil de gerar sustentação.
Por outro lado, a Força de Arrasto atua paralelamente à direção do fluxo e se opõe ao
movimento do perfil no escoamento. Essa força é resultado da interação entre o aerofólio e o
fluido, e está relacionada principalmente a duas causas: o arrasto de atrito e o arrasto de forma.

- Arrasto de Atrito: Esse tipo de arrasto ocorre devido às tensões de cisalhamento na
    superfície do perfil, geradas pela fricção entre o fluido e a superfície do objeto.
- Arrasto de Forma:Esse tipo de arrasto é causado pelo desequilíbrio de pressão em torno
    do perfil, especialmente nas regiões onde o fluxo se separa da superfície.


## 2.10 CONTROLE DE ÂNGULO DE PASSO

## 2.11 CONTROLADOR YAW

## 2.12 TURBINA EÓLICA TE24

Para o desenvolvimento deste trabalho, foi utilizada a turbina eólica TE24, produzida
pela VIND Aerogeradores. Ela se destaca por sua tecnologia totalmente nacional, facilitando o
suporte técnico e a manutenção local. Este aerogerador é projetado para maximizar a eficiência
e a flexibilidade operacional, incorporando técnicas e tecnologias geralmente aplicadas apenas
a aerogeradores de grande porte.
Desenvolvida em parceria com o Instituto Tecnológico de Aeronáutica (ITA), a turbina
apresenta variadores de passo eletronicamente controlados e sistemas de controle de última
geração, garantindo alta eficiência e adaptabilidade a diferentes condições de vento.
A TE24 é equipada com um rotor de 15 metros de diâmetro e possui uma potência no-
minal de 24KW, capaz de gerar eletricidade suficiente para atender a demanda de pequenos
empreendimentos comerciais ou unidades industriais. A turbina opera eficientemente em uma
ampla variação de velocidade de vento, indo de 2,3 m/s (velocidade decut-in) até 20 m/s (ve-
locidade decut-out). Essa faixa operacional ampla permite aplicabilidade em diversas regiões,
adaptando-se a diferentes perfis de vento. Essa característica é destacada nos dados obtidos da
operação em Franca-SP, detalhados na Tabela 2.6.

```
Tabela 2.6 – Comparação entre geração estimada com dados teóricos e dados reais de geração
de energia eólica na Vila Santa Terezinha, Franca – SP.
Vel. Média de Vento (ms) Geração estimada com dados teóricos (kWhmês) Geração estimada com dados reais (kWhmês) %
3 1150 1808 57%
3.5 1871 2722 45%
4 2748 3729 36%
4.5 3727 4776 28%
5 4748 5817 23%
5.5 5763 6817 18%
6 6736 7753 15%
6.5 7642 8610 13%
7 8469 9381 11%
7.5 9206 10061 9%
8 9848 10645 8%
Fonte: Dados de Geração TE24 - Real - Franca
```
A turbina eólica TE24 é projetada para operar de forma eficiente e durável, incorporando
materiais de alta qualidade. As pás são feitas de compósitos reforçados com fibras de vidro, ga-
rantindo durabilidade e resistência. A torre é galvanizada a fogo com tripla camada de proteção
contra corrosão, aumentando a vida útil do equipamento. A tensão de saída da turbina pode ser


configurada para 220V, 380V ou 440V trifásica, conforme as necessidades da instalação. Suas
característica técnicas elétricas estão descritas na tabela 2.7.

```
Tabela 2.7 – Características Elétricas do Aerogerador TE24
```
```
Característica Descrição
Potência nominal do gerador 30 KVA ou 24KW
Tensão de saída 220/380/440V trifásica
Velocidade nominal do vento 9,0 m/s
Velocidade mínima 2,3 m/s (“cut-in”)
Velocidade máxima de operação 20,0 m/s (“cut-out”)
Velocidade de proteção 45,0 m/s (rajada)
Controle de prioridades de carga 4 ramais
Inversor de Frequência Versão “ON GRID” ou similar
```
Além disso, a turbina TE24 oferece flexibilidade na instalação, podendo ser configurada
para diferentes alturas de torre e tipos de solo. A possibilidade de conexão on-grid permite
a compensação da energia gerada com o consumo, reduzindo significativamente os custos de
eletricidade e aumentando a viabilidade econômica do projeto. Suas característica técnicas
construtivas estão descritas na tabela 2.8.

```
Tabela 2.8 – Características Construtivas do Aerogerador TE24
```
```
Característica Descrição
Tipo de turbina Três pás
Posição do eixo Horizontal
Diâmetro do rotor 15 metros
Variador de Passo de hélice Ativo – mecanismo original
Movimento Azimutal (“yaw”) Ativo
Material das pás Compósitos
Torre – configuração Chapa dobrada e galvanizada a fogo
Proteção contra corrosão Tripla camada
Altura da torre Variável de acordo com o local escolhido
Sistema de aterramento da torre Sim
Sistema de freio de emergência Sim
```
Devido às diversas características presentes neste modelo de aerogerador, ele foi esco-
lhido como referência para o desenvolvimento deste trabalho. Suas propriedades construtivas,
incluindo o controle do ângulo de passo da hélice, permitem a análise da máxima potência.
Além disso, as características elétricas, como a velocidade decut-inde 2,3 m/s, conferem alta
aplicabilidade em cenários adversos, tornando este modelo uma excelente opção para o estudo
e desenvolvimento propostos.
Considerando todos esses aspectos, a turbina eólica TE24 será utilizada como referência
para as simulações, análises e validações desenvolvidas nos próximos capítulos deste trabalho.


Dessa forma, estabelece-se uma conexão direta entre a fundamentação teórica apresentada e a
aplicação prática do estudo.


## 3 METODOLOGIA.

Este trabalho está sendo desenvolvido mediante pesquisa explicativa a fim de entender
como diferentes fatores modificam e afetam o desempenho das turbinas eólicas, buscando ana-
lisar e validar modelos teóricos. A figura 3.1 apresenta o fluxograma que ilustra o fluxo dessas
etapas. Desse modo, será adotado uma abordagem composta por procedimentos de pesquisa
bibliográfica e documental, simulação computacional e análise de dados.
Inicialmente, serão realizado estudos sobre perfis de vento, abordando as características
atmosféricas e locais, determinando assim o potencial eólico, a curva de potência e a serie tem-
poral. Em seguida, será desenvolvido o estudo e a modelagem dos componentes pertencentes a
turbina eólica a fim de criar o modelo da turbina.
Serão consultados artigos científicos, livros, teses, dissertações e publicações técnicas,
além de documentos técnicos, como especificações de turbinas eólicas e relatórios de desempe-
nho de sistemas eólicos.
A pesquisa será conduzida com base no perfil de vento da cidade de Cachoeira do Sul-
RS. Este cenário foi escolhido devido às suas características de vento favoráveis para a geração
de energia eólica.
Para o desenvolvimento e execução das simulações será utilizado o software MATLAB/
Simulink. Os dados de vento de Cachoeira do Sul serão integrados aos modelos, a fim de criar
um cenário de simulação, a Figura 3.2 sintetiza de maneira ilustrativa o cenário a ser simulado.
Elaborado o cenário, inicia-se o refinamento através de análise, que inclui a avaliação de mé-
tricas de desempenho, como eficiência de conversão de energia e comportamento dinâmico dos
componentes. A validação dos modelos simulados será realizada comparando os resultados das
simulações com dados teóricos e com dados disponíveis na literatura.
Assim, dentre os objetos da pesquisa tem-se o desenvolvimento de uma plataforma de
simulação de turbina eólica, que permite a modelagem e análise dos diversos componentes
de uma turbina eólica. A pesquisa se concentra na modelagem teórica do comportamento do
vento e dos componentes, como as pás, o rotor, o gerador e os sistemas de controle. Além
disso, os dados de vento de Cachoeira do Sul são utilizados como base para as simulações
teóricas, permitindo uma avaliação de inserção de aerogeradores na UFSM campus universitário
de Cachoeira do Sul.


### Figura 3.1 – Fluxograma de desenvolvimento do projeto.

Figuras/Teorico/TCC - AEROGERADOR.png


### Figura 3.2 – Ilustração do cenário.

```
Figuras/Teorico/metodologia_page-0001.jpg
```
## 3.1 CRONOGRAMA PARA DESENVOLVIMENTO DO TCC II

O cronograma a seguir detalha as atividades planejadas para o desenvolvimento da se-
gunda parte do TCC, abordando os passos restantes para o desenvolvimento do trabalho. Este
cronograma está organizado de agosto a dezembro. Cada ação está programada para ocorrer em
períodos específicos, garantindo uma abordagem estruturada e organizada do projeto.

```
Tabela 3.1 – Cronograma de ações
Ação AGO SET OUT NOV DEZ
Analise para Modelos de
Controle de Operação
Desenvolvimento do Sistema
de Controle da Turbina
Desenvolvimento da Plata-
forma de Simulação
Testes e Validação do Sistema
Avaliação do Desempenho
Documentação e Preparação
do Relatório Final
```
```
O cronograma é abordado em detalhes a seguir:
```

1. Análise para Modelos de Controle de Operação:Será realizada a análise para o desen-
    volvimento dos modelos de controle de operação. Esta etapa é fundamental para entender
    as necessidades do sistema e definir os parâmetros de controle.
2. Desenvolvimento do Sistema de Controle da Turbina:Esta fase envolve a implemen-
    tação de algoritmos de controle e ajustes necessários para otimizar o funcionamento da
    turbina.
3. Desenvolvimento da Plataforma de Simulação: Início do desenvolvimento da plata-
    forma de simulação. Esta etapa é crucial para integrar os modelos matemáticos e de
    controle em um ambiente de simulação.
4. Testes e Validação do Sistema: Início dos testes e validação do sistema, verificando
    a precisão dos modelos e a eficácia dos controles implementados em estudos de casos
    envolvendo turbinas eólicas de velocidade variável.
5. Avaliação do Desempenho:Início da avaliação do desempenho do sistema de simulação,
    analisando a eficácia e eficiência sob diferentes condições operacionais.
6. Documentação e Preparação do Relatório Final:Compilação de toda a documentação
    do projeto e preparação do relatório final. Esta etapa inclui os resultados, conclusões e
    recomendações baseadas nas análises realizadas ao longo do projeto.


## 4 DESENVOLVIMENTO.

## 4.1 ANÁLISE DO CENÁRIO BASE

Nesta seção, apresenta-se uma análise detalhada do cenário base para a avaliação do
potencial eólico, com foco na cidade de Cachoeira do Sul. O objetivo é caracterizar as condições
locais de vento, fundamentais para o desenvolvimento e a simulação de sistemas de geração de
energia eólica.
A escolha de Cachoeira do Sul como estudo de caso justifica-se por ser o local de desen-
volvimento deste trabalho e por apresentar características representativas do potencial eólico
da região Sul do Brasil. Além disso, a disponibilidade de dados experimentais coletados lo-
calmente permite uma análise mais precisa e fundamentada, contribuindo para a validação dos
modelos e metodologias adotados.

## 4.1.1 Cachoeira do Sul.

Cachoeira do Sul, localizada no estado do Rio Grande do Sul, destaca-se pelo signifi-
cativo potencial eólico. A região Sul do Brasil, especialmente o Rio Grande do Sul, apresenta
condições climáticas favoráveis que tornam a energia eólica uma alternativa viável e promis-
sora, como ilustrado na 4.1. Assim, a análise das características eólicas de Cachoeira do Sul
torna-se relevante não apenas por ser a cidade onde este trabalho está sendo desenvolvido, mas
também pela oportunidade de explorar e modelar os recursos eólicos disponíveis.
A velocidade média do vento em Cachoeira do Sul é superior a 2,3 m/s a uma altura
de 10 metros acima do solo, apresentando poucas variações sazonais, conforme representado
na 4.2. Embora moderada, essa velocidade indica um bom potencial para a geração de energia
eólica.
Para fins comparativos, foram obtidos dados de velocidade do vento na UFSM de Ca-
choeira do Sul, por meio de anemômetro já instalado, mostrado na 4.3. Os dados, referentes
ao ano de 2023, foram coletados em intervalos horários a uma altura de aproximadamente três
metros, resultando no gráfico da 4.4. Para análise, os dados foram ajustados à distribuição de
Weibull, conforme 4.5.
Devido ao anemômetro estar muito próximo ao solo, os valores obtidos apresentam
grande variabilidade. Conforme recomendado por Fadigas (2011), o ideal é que o anemômetro
esteja posicionado à altura do cubo do aerogerador. Essa altura permite medições mais precisas
e representativas das condições de vento enfrentadas pela turbina, minimizando interferências
causadas pela rugosidade do solo e por obstáculos próximos, resultando em dados mais confiá-


### Figura 4.1 – Atlas Eólico para o Rio Grande do Sul à altura de 100 metros.

Figuras/Teorico/Atlas RS.png

```
Fonte: Associação Brasileira de Energia Eólica (ABEEólica) (2017).
```

### Figura 4.2 – Velocidade média do vento em Cachoeira do Sul.

```
Figuras/Teorico/Velocidade mÃľdia do vento em Cachoeira do Sul.png
```
```
Fonte: WeatherSpark (2024).
```
```
Figura 4.3 – Fotografia do anemômetro instalado na UFSM Campus Cachoeira do Sul.
```
```
Figuras/Teorico/anemometro_CampusUFSM.jpg
```
veis para a modelagem do vento e a operação eficiente dos aerogeradores.
Para analisar a variação da velocidade do vento com a altura em Cachoeira do Sul, foram
aplicados dois modelos consagrados de estimativa, discutidos na Seção 2.3: a Lei da Potência
e a Lei Logarítmica. Considerando uma velocidade média de 2,7 m/s a 10 metros de altura,
foi possível traçar os perfis de velocidade em diferentes alturas, conforme ilustrado na 4.6 e
detalhado na 4.1.
A análise do cenário base em Cachoeira do Sul evidencia que, apesar das limitações
impostas pela altura do anemômetro utilizado, a região apresenta potencial significativo para
a geração de energia eólica. Os dados coletados e os modelos aplicados demonstram que o
aumento da altura de instalação dos aerogeradores proporciona ganhos relevantes na velocidade
do vento, tornando o aproveitamento energético mais eficiente. Dessa forma, a caracterização
detalhada do perfil de vento local é fundamental para o dimensionamento e a operação adequada


Figura 4.4 – Gráfico dos dados do anemômetro instalado na UFSM Campus Cachoeira do Sul.

```
Figuras/Teorico/Average Wind Speed Over Time2.png
```
```
Figura 4.5 – Distribuição de Weibull ajustada aos dados do anemômetro instalado na UFSM
Campus Cachoeira do Sul.
```
```
Figuras/Teorico/DistribuicaoWeibull.png
```

Figura 4.6 – Perfis de velocidade do vento em função da altura, obtidos pela Lei da Potência e
pela Lei Logarítmica.

```
Figuras/Teorico/Lei da Potencia e Lei Logaritmica2.jpg
```
```
Tabela 4.1 – Comparação das velocidades do vento estimadas pela Lei da Potência e Lei
Logarítmica em diferentes alturas.
```
```
Altura (m) Lei Potência (m/s) Lei Logarítmica (m/s) Diferença (m/s)
10 2.70 2.70 0.000
20 3.14 3.15 0.001
30 3.44 3.41 0.032
40 3.66 3.59 0.072
50 3.85 3.73 0.112
60 4.00 3.85 0.153
70 4.14 3.95 0.192
80 4.27 4.04 0.229
90 4.38 4.11 0.266
100 4.48 4.18 0.301
Fonte: O autor.
```

de sistemas eólicos, reforçando a viabilidade da implementação de turbinas na região.

## 4.2 SISTEMA DE GERAÇÃO EÓLICA - EOLICSIM


## 5 CONCLUSÃO

Este trabalho tem como objetivo desenvolver um sistema de simulação para turbinas eó-
licas utilizando MATLAB/SIMULINK®, focando na modelagem e análise do comportamento
de aerogeradores, especialmente o modelo TE24, sob diferentes condições de vento. O desen-
volvimento desse simulador permitira a avaliação detalhada dos componentes da turbina, como
pás, rotor, gerador e sistemas de controle, contribuindo para uma melhor compreensão de como
otimizar a eficiência energética dos aerogeradores.
A metodologia empregada incluiu a integração de dados de vento reais da cidade de
Cachoeira do Sul, possibilitando a criação de cenários de simulação realistas. A validação
dos modelos teóricos com dados empíricos demonstrou a precisão das simulações realizadas,
destacando a relevância do uso de software como MATLAB/SIMULINK® para estudos na área
de energia eólica.
Os resultados obtidos reforçam a importância do desenvolvimento da plataforma de si-
mulação na previsão de desempenho. O desenvolvimento e a validação de modelos precisos
são essenciais para o avanço das tecnologias de conversão de energia eólica, contribuindo para
a inserção eficiente de aerogeradores na matriz energética brasileira.
Além disso, este trabalho evidencia o potencial de crescimento da energia eólica no
Brasil, destacando a relevância de investimentos contínuos em pesquisa e desenvolvimento na
área. A utilização de fontes renováveis como a energia eólica é crucial para a diversificação da
matriz energética e para a redução dos impactos ambientais associados à geração de eletricidade.
Em suma, a pesquisa alcançou seus objetivos para desenvolvimento do TCC 1, assim,
tendo um primeiro modelo de perfil eólico e sugerindo a integração de sistemas de supervisão
e controle mais avançados, bem como a análise de diferentes regimes operacionais para tur-
binas eólicas. A continuidade desse tipo de pesquisa é fundamental para o desenvolvimento
sustentável do setor energético.


### REFERÊNCIAS BIBLIOGRÁFICAS.

ACKERMANN, T.Wind Power in Power System. 1. ed. London: John Wiley & Sons, Ltd,
2005.

Agência Internacional de Energia.Dados sobre o crescimento do consumo mundial de ener-
gia elétrica. 2024. Acesso em: 17 jul. 2024. Disponível em: <https://www.iea.org>.

Agência Nacional de Energia Elétrica (ANEEL).Capacidade de Geração no Brasil. 2009.
Disponível em: <http://www.aneel.gov.br/aplicacoes/capacidadebrasil/capaci-dadebrasil.asp>.

Associação Brasileira de Energia Eólica (ABEEólica). Energia eólica chega à
sétima posição no ranking mundial de geração abastecendo 10% do Bra-
sil. 2017. Acesso em: 24 jul. 2024. Disponível em: <https://abeeolica.org.br/
energia-eolica-chega-a-setima-posicao-no-ranking-mundial-de-geracao-abastecendo-10-do-brasil/
>.

.Boletim Anual 2024. 2024. Acesso em: 24 jul. 2024. Disponível em: <https://abeeolica.
org.br/wp-content/uploads/2024/07/424\_ABEEOLICA\_BOLETIM-ANUAL-2024\
_DIGITAL\_PT\_V3.pdf>.

BATCHELOR, G. K.An Introduction to Fluid Dynamics. [S.l.]: Cambridge University Press,
2000.

BETZ, A.Wind-Energie und ihre Ausnutzung durch Windmühlen. Göttingen: Vandenho-
eck & Ruprecht, 1926.

BNDES, B. N. de Desenvolvimento Econômico e S.Dados sobre investimentos no setor de
energia eólica e previsões de investimentos futuros. 2024. Acesso em: 17 jul. 2024. Disponí-
vel em: <https://www.bndes.gov.br>.

BURTON, T. et al.Wind Energy Handbook. Londres: John Wiley & Sons, 2001.

CALIJURI, M. L.; CUNHA, D. G. A matriz elétrica mundial é predominantemente fóssil, e
os esforços para reduzir a dependência desses combustíveis de alto impacto ambiental são cru-
ciais para mitigar as mudanças climáticas. In: ANTAC.Anais do 10. Encontro Nacional de
Tecnologia do Ambiente Construído. São Paulo, 2013. p. 485–494.

CARVALHO, P.Geração Eólica. Fortaleza: Imprensa Universitária, 2003.

CENTRO BRASILEIRO DE ENERGIA EÓLICA -– CBEE.Energia Eólica. Boulder, 2000.
Acesso em 9 abr. 2024. Disponível em: <https://livroaberto.ibict.br/bitstream/1/582/7/06\%20-\
%20Energia\%20E\%C2\%BElica\%283\%29.pdf>.

Centro de Referência para Energia Solar e Eólica Sérgio de Salvo Brito (CRESESB).Atlas
Eólico. 2013. Acesso em: 24 jul. 2024. Disponível em: <https://cresesb.cepel.br/index.php?
section=atlas\_eolico&>.

CEPEL.Atlas do Potencial Eólico Brasileiro. Rio de Janeiro, RJ: CEPEL, 2001.

Danish Wind Industry Association.Wind Energy Reference Manual. 2000. Acessado em:
junho 2024. Disponível em: <http://ele.aut.ac.ir/~wind/en/tour/wres/variab.htm>.


DESCONHECIDO. Como é formada a ATMOSFERA TERRESTRE. Boulder, 2019.
Acesso em: 14 jun. 2024. Disponível em: <https://hangarmma.com.br/blog/atmosfera-terrestre/
>.

DUTRA, R.Viabilidade técnico-econômica da energia eólica face ao novo marco regulató-
rio do setor elétrico brasileiro. 2001. 259 p. Dissertação (Dissertação (Mestrado em Ciências
em Planejamento Energético)) — Universidade Federal do Rio de Janeiro, Rio de Janeiro, 2001.
Programa de Pós-Graduação em Engenharia (Coppe).

Empresa de Pesquisa Energética.Dados sobre o crescimento do consumo de energia elétrica
no Brasil entre 2010 e 2020. 2024. Acesso em: 17 jul. 2024. Disponível em: <https://www.
epe.gov.br>.

Empresa de Pesquisa Energética (EPE). Balanço Energético Nacional 2025: Ano base
2024. Rio de Janeiro: [s.n.], 2025. Acesso em: 10 jun. 2025. Disponível em: <https:
//www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/
publicacao-885/topico-767/BEN\_S\%C3\%ADntese\_2025\_PT.pdf>.

Estadão. Energia eólica no Brasil: crescimento e investimentos. 2024. Acesso
em: 17 jul. 2024. Disponível em: <https://www.estadao.com.br/economia/negocios/
energia-eolica-brasil-crescimento-investimentos/>.

FADIGAS, E. A. F. A.Energia Eólica. E-book. Barueri, SP: Editora Manole, 2011. Acesso
em: 14 jun. 2024. ISBN 9788520446539. Disponível em: <https://integrada.minhabiblioteca.
com.br/\#/books/9788520446539/>.

HALLIDAY, D.; RESNICK, R.; WALKER, J.Fundamentos de Física 2. [S.l.]: s.n., 1996. v. 4.

HEIER, S.Wind Energy Systems: Operation and Control. [S.l.]: Springer, 2014.

HIRATA, M.Energia Eólica – Uma Introdução. Rio de Janeiro: COPPE/UFRJ, 1985.

JUNIOR, T.; RANGEL, C.Desempeño aerodinámico de turbinas eólicas de eje vertical en
función de temperatura de superficie de álabe. 2012. Dissertação (Mestrado) — Universidad
de Chile, 2012.

KOCH, G. G.Implementação de um Simulador para Turbina Eólica de Velocidade Va-
riável com MATLAB/SIMULINK® e Estudo do Sistema de Emulação do Aerogerador
DR14. 2010. Dissertação (Mestrado) — Universidade Federal de Santa Maria, Santa Maria,
RS, Brazil, 2010.

LUTGENS, E. J. T. F. K.The Atmosphere: An Introduction to Meteorology. 12th. ed. [S.l.]:
Prentice Hall, 2012. 506 p. ISBN 978-0321756312.

MANWELL J.G. MCGOWAN, A. R. J.Wind Energy Explained: Theory, Design and Ap-
plications. London: John Wiley & Sons, 2004.

MARTINS, F. R.; GUARNIERI, R. A.; PEREIRA, E. B. O aproveitamento da energia eólica.
Revista Brasileira de Ensino de Física, v. 30, n. 1, 2008. Acesso em: 21 set. 2020. Disponível
em: <http://www.scielo.br/scielo.php?script=sci\_arttext&pid=S1806-11172008000100005>.

MARTINS, M.Avaliação da Qualidade de Energia e Performance de Potência de Turbinas
Eólicas Conectadas à Rede Elétrica. 2010. Dissertação (Mestrado) — Universidade Federal
de Santa Catarina, Florianópolis, SC, Brazil, 2010.


Nações Unidas.Protocolo de Kyoto à Convenção-Quadro das Nações Unidas sobre Mu-
dança do Clima. Kyoto, Japão, 1997.

```
.Acordo de Paris. Paris, França, 2015.
```
PASSOS, J. C.Camada limite. [S.l.], 2014.

PAVINATTO, E. F.Ferramenta para Auxílio à Análise de Viabilidade Técnica da Cone-
xão de Parques Eólicos à Rede Elétrica. 2005. Dissertação (Dissertação de Mestrado) —
Programa de Engenharia Elétrica, COPPE / UFRJ, Rio de Janeiro, 2005. 2005.

PEIXOTO, P. d. S.; RODRIGUES, W. G.Noções de mecânica de fluidos com aplicações em
perfis aerodinâmicos. [S.l.]: São Paulo, 2009.

PINTO, M. d. O. O vento. In: Fundamentos da energia eólica. 1. ed. Rio de Janeiro: LTC,

2014. p. 47–66.

Programa de Incentivo às Fontes Alternativas de Energia Elétrica (PROINFA).Programa de
Incentivo às Fontes Alternativas de Energia Elétrica Proinfa. 2024. Acesso em: 24 jul.

2024. Disponível em: <https://proinfa.enbpar.gov.br/>.

QUORA. Quais são as desvantagens das turbinas Darrieus. 2024. Acesso
em: 10 jul. 2024. Disponível em: <https://pt.quora.com/Quais-s\%C3\
%A3o-as-desvantagens-das-turbinas-darrieus>.

RAIAMBAL, K.; CHELLAMUTH, C. Modeling and simulation of grid connected wind elec-
tric generating system. In: Proceedings of IEEE TENCON’02. [s.n.], 2002. p. 1847–1952.
Disponível em: <https://ieeexplore.ieee.org/document/1182696>.

REBOITA, M. S. et al. Entendendo o tempo e o clima na américa do sul.Terra e Didática, v. 8,
n. 1, p. 34–50, 2012. Acesso em: 20 set. 2020. Disponível em: <https://cutt.ly/0gssd5Q>.

ROCHA, A. V. d. et al.Fundamentos de Energia Eólica. 1. ed. Natal: Instituto Federal de
Educação, Ciência e Tecnologia do Rio Grande do Norte, 2023.

ROHATGI, J.; NELSON, V.Wind Characteristics: An Analysis for the Generation of Wind
Power. Canyon: West Texas A&M University, 1994.

SCHLICHTING, H.Boundary-Layer Theory. 8th. ed. [S.l.]: Springer, 2000.

SILVA, P.Sistema para tratamento, armazenamento e disseminação de dados de vento.

1999. 113 p. Dissertação (Dissertação (Mestrado em Ciências em Engenharia Mecânica)) —
Universidade Federal do Rio de Janeiro, Rio de Janeiro, 1999. Programa de Pós-Graduação em
Engenharia (Coppe).

SLOOTWEG, J. G.; POLINDER, H.; KLING, W. L. Dynamic modelling of a wind turbine with
doubly fed induction generator. In:Proceedings of the IEEE. [S.l.: s.n.], 2003.

SMART SERVO. Comparison of the Efficiency of Various Wind Turbines – Horizon-
tal/Vertical Axis. 2024. Acesso em: 14 jul. 2024. Disponível em: <https://smartservo.org/
comparison-of-the-efficiency-of-various-wind-turbines-horizontal-vertical-axis>.

STANNARD, N.; BUMBY, J. Performance aspects of mains connected small-scale wind turbi-
nes.IET Generation, Transmission & Distribution, IET, v. 1, n. 2, p. 348–356, 2007.


STULL, R. B.An Introduction to Boundary Layer Meteorology. Dordrecht: Kluwer Aca-
demic Publishers, 1988. 666 p. ISBN 978-94-010-8609-0.

TROEN, I.; PETERSEN, E.European Wind Atlas. 1. ed. [S.l.]: Roskilde, Riso National
Laboratory, 1989.

VIAN Ângelo.Energia Eólica: Fundamentos, Tecnologia e Aplicações. [S.l.]: Editora Blu-
cher, 2021. E-book. ISBN 9786555500585.

WeatherSpark. Clima característico em Cachoeira do Sul, Rio Grande
do Sul, Brasil durante o ano. 2024. Acesso em: 24 jul. 2024. Dis-
ponível em: <https://pt.weatherspark.com/y/29610/Clima-caracter\%C3\
%ADstico-em-Cachoeira-do-Sul-Rio-Grande-do-Sul-Brasil-durante-o-ano\
#Sections-Sources>.

WELTNER, K.; OUTROS. A dinâmica dos fluidos complementada e a sustentação da asa.
Revista Brasileira de Ensino de Física, SciELO Brasil, v. 23, n. 4, p. 429, 2001.


