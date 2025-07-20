#!/usr/bin/env python3
"""
Exemplo prático do módulo meteorológico - Sistema de Simulação de Turbinas Eólicas

Este script demonstra o uso completo do módulo meteorológico, incluindo:
- CRUD de fontes de dados meteorológicos
- CRUD de dados meteorológicos  
- Consultas relacionais avançadas
- Integração com o sistema geográfico

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importações do módulo meteorológico
from meteorological import (
    MeteorologicalDataSource, MeteorologicalDataSourceRepository,
    MeteorologicalData, MeteorologicalDataRepository
)

# Importações do módulo geográfico para integração
from geographic.cidade.entity import Cidade
from geographic.cidade.repository import CidadeRepository
from geographic.pais.entity import Pais
from geographic.pais.repository import PaisRepository
from geographic.regiao.entity import Regiao
from geographic.regiao.repository import RegiaoRepository


def configurar_base_de_dados():
    """Cria as tabelas necessárias se não existirem"""
    print("🔧 Configurando base de dados...")
    
    # Repositórios
    fonte_repo = MeteorologicalDataSourceRepository()
    dados_repo = MeteorologicalDataRepository()
    
    # Criar tabelas
    fonte_repo.criar_tabela()
    dados_repo.criar_tabela()
    
    print("✅ Base de dados configurada com sucesso!")


def exemplo_crud_fontes_dados():
    """Demonstra operações CRUD para fontes de dados meteorológicos"""
    print("\n📊 === CRUD DE FONTES DE DADOS METEOROLÓGICOS ===")
    
    repo = MeteorologicalDataSourceRepository()
    
    # 1. CRIAR fontes de dados
    print("\n1️⃣ Criando fontes de dados...")
    
    fontes = [
        MeteorologicalDataSource(
            name="NASA_POWER",
            description="NASA Prediction of Worldwide Energy Resources - Dados satelitais globais"
        ),
        MeteorologicalDataSource(
            name="INMET",
            description="Instituto Nacional de Meteorologia - Dados oficiais do Brasil"
        ),
        MeteorologicalDataSource(
            name="OPEN_METEO",
            description="Open-Meteo API - Dados meteorológicos históricos e previsões"
        ),
        MeteorologicalDataSource(
            name="WEATHER_API",
            description="WeatherAPI - Dados meteorológicos em tempo real"
        )
    ]
    
    ids_fontes = []
    for fonte in fontes:
        try:
            fonte_id = repo.salvar(fonte)
            ids_fontes.append(fonte_id)
            print(f"   ✅ Criada: {fonte.name} (ID: {fonte_id})")
        except Exception as e:
            print(f"   ⚠️ Erro ao criar {fonte.name}: {e}")
    
    # 2. LISTAR todas as fontes
    print("\n2️⃣ Listando todas as fontes...")
    todas_fontes = repo.listar_todos()
    for fonte in todas_fontes:
        print(f"   📊 {fonte}")
    
    # 3. BUSCAR por nome
    print("\n3️⃣ Buscando fonte por nome...")
    nasa_fonte = repo.buscar_por_nome("NASA_POWER")
    if nasa_fonte:
        print(f"   🔍 Encontrada: {nasa_fonte}")
    
    # 4. BUSCAR por termo
    print("\n4️⃣ Buscando fontes por termo 'API'...")
    fontes_api = repo.buscar_por_termo("API")
    for fonte in fontes_api:
        print(f"   🔍 {fonte}")
    
    # 5. ATUALIZAR uma fonte
    print("\n5️⃣ Atualizando descrição da fonte NASA...")
    if nasa_fonte:
        nasa_fonte.description = "NASA POWER - Sistema global de dados meteorológicos e de energia solar"
        sucesso = repo.atualizar(nasa_fonte)
        print(f"   {'✅' if sucesso else '❌'} Atualização: {sucesso}")
    
    # 6. VERIFICAR duplicatas
    print("\n6️⃣ Verificando duplicatas...")
    existe = repo.existe_nome("NASA_POWER")
    print(f"   🔍 'NASA_POWER' já existe: {existe}")
    
    return ids_fontes


def exemplo_crud_dados_meteorologicos():
    """Demonstra operações CRUD para dados meteorológicos"""
    print("\n🌤️ === CRUD DE DADOS METEOROLÓGICOS ===")
    
    dados_repo = MeteorologicalDataRepository()
    fonte_repo = MeteorologicalDataSourceRepository()
    cidade_repo = CidadeRepository()
    
    # Buscar uma fonte e cidade existentes para os testes
    fontes = fonte_repo.listar_todos()
    cidades = cidade_repo.listar_todos()
    
    if not fontes or not cidades:
        print("❌ Necessário ter fontes e cidades cadastradas para continuar")
        return []
    
    fonte_id = fontes[0].id
    cidade_id = cidades[0].id
    
    print(f"📍 Usando fonte: {fontes[0].name}")
    print(f"🏙️ Usando cidade: {cidades[0].nome}")
    
    # 1. CRIAR dados meteorológicos
    print("\n1️⃣ Criando dados meteorológicos...")
    
    dados_exemplo = []
    base_date = date.today() - timedelta(days=30)
    
    for i in range(10):
        dados = MeteorologicalData(
            meteorological_data_source_id=fonte_id,
            cidade_id=cidade_id,
            data=base_date + timedelta(days=i*3),
            altura_captura=10.0 + (i % 3) * 10,  # 10m, 20m, 30m
            velocidade_vento=5.5 + (i % 5) * 2.0,  # Variação de vento
            temperatura=22.0 + (i % 8) * 3.0,  # Variação de temperatura
            umidade=60.0 + (i % 4) * 10.0  # Variação de umidade
        )
        
        try:
            dados_id = dados_repo.salvar(dados)
            dados_exemplo.append(dados_id)
            print(f"   ✅ Criado: {dados} (ID: {dados_id})")
        except Exception as e:
            print(f"   ⚠️ Erro ao criar dados: {e}")
    
    # 2. BUSCAR por ID
    print("\n2️⃣ Buscando dados por ID...")
    if dados_exemplo:
        primeiro_id = dados_exemplo[0]
        dados_encontrados = dados_repo.buscar_por_id(primeiro_id)
        if dados_encontrados:
            print(f"   🔍 Encontrado: {dados_encontrados}")
    
    # 3. BUSCAR por cidade
    print("\n3️⃣ Buscando dados por cidade...")
    dados_cidade = dados_repo.buscar_por_cidade(cidade_id, limite=5)
    print(f"   📊 Encontrados {len(dados_cidade)} registros para a cidade")
    for dados in dados_cidade[:3]:  # Mostrar apenas os 3 primeiros
        print(f"   🌤️ {dados}")
    
    # 4. BUSCAR por período
    print("\n4️⃣ Buscando dados por período...")
    data_inicio = base_date
    data_fim = base_date + timedelta(days=20)
    dados_periodo = dados_repo.buscar_por_periodo(data_inicio, data_fim, cidade_id)
    print(f"   📅 Encontrados {len(dados_periodo)} registros no período")
    
    # 5. ATUALIZAR dados
    print("\n5️⃣ Atualizando dados meteorológicos...")
    if dados_exemplo:
        dados_para_atualizar = dados_repo.buscar_por_id(dados_exemplo[0])
        if dados_para_atualizar:
            dados_para_atualizar.velocidade_vento = 12.5
            dados_para_atualizar.temperatura = 28.0
            sucesso = dados_repo.atualizar(dados_para_atualizar)
            print(f"   {'✅' if sucesso else '❌'} Atualização: {sucesso}")
    
    return dados_exemplo


def exemplo_consultas_relacionais():
    """Demonstra consultas relacionais avançadas"""
    print("\n🔗 === CONSULTAS RELACIONAIS AVANÇADAS ===")
    
    dados_repo = MeteorologicalDataRepository()
    cidade_repo = CidadeRepository()
    
    # 1. Dados meteorológicos com detalhes completos da cidade
    print("\n1️⃣ Dados meteorológicos com informações geográficas...")
    dados_completos = dados_repo.buscar_com_detalhes_cidade(limite=5)
    
    for dados in dados_completos:
        print(f"   🌍 {dados['data']} | {dados['cidade_nome']}, {dados['regiao_nome']}, {dados['pais_nome']}")
        print(f"      📍 Lat: {dados['latitude']}, Lon: {dados['longitude']}")
        print(f"      🌤️ Vento: {dados['velocidade_vento']}m/s, Temp: {dados['temperatura']}°C")
        print(f"      📊 Fonte: {dados['fonte_nome']}")
        print()
    
    # 2. Estatísticas de vento por cidade
    print("\n2️⃣ Estatísticas de vento por cidade...")
    cidades = cidade_repo.listar_todos()
    
    for cidade in cidades[:3]:  # Apenas primeiras 3 cidades
        stats = dados_repo.buscar_estatisticas_vento_por_cidade(cidade.id)
        if stats and stats.get('total_registros', 0) > 0:
            print(f"   🏙️ {cidade.nome}:")
            print(f"      📊 Total de registros: {stats['total_registros']}")
            print(f"      💨 Vento médio: {stats['velocidade_media']:.2f} m/s")
            print(f"      📈 Vento máximo: {stats['velocidade_maxima']:.2f} m/s")
            print(f"      🌡️ Temperatura média: {stats['temperatura_media']:.1f} °C")
            print()
    
    # 3. Dados recentes por região
    print("\n3️⃣ Dados meteorológicos recentes por região...")
    regiao_repo = RegiaoRepository()
    regioes = regiao_repo.listar_todos()
    
    for regiao in regioes[:2]:  # Apenas primeiras 2 regiões
        dados_recentes = dados_repo.buscar_dados_recentes_por_regiao(regiao.id, dias=30)
        if dados_recentes:
            print(f"   🗺️ {regiao.nome} ({len(dados_recentes)} registros nos últimos 30 dias):")
            for dados in dados_recentes[:3]:  # Mostrar apenas os 3 mais recentes
                print(f"      📅 {dados['data']} | {dados['cidade_nome']}: "
                      f"Vento {dados['velocidade_vento']}m/s, {dados['temperatura']}°C")
            print()


def exemplo_validacoes_e_classificacoes():
    """Demonstra validações e classificações dos dados"""
    print("\n✅ === VALIDAÇÕES E CLASSIFICAÇÕES ===")
    
    # 1. Teste de validações
    print("\n1️⃣ Testando validações...")
    
    # Dados válidos
    dados_validos = MeteorologicalData(
        meteorological_data_source_id=1,
        cidade_id=1,
        data=date.today(),
        velocidade_vento=8.5,
        temperatura=25.0,
        umidade=65.0
    )
    print(f"   ✅ Dados válidos: {dados_validos.validar()}")
    
    # Dados inválidos - sem IDs
    dados_invalidos = MeteorologicalData(
        meteorological_data_source_id=0,  # Inválido
        cidade_id=0,  # Inválido
        data=date.today()
    )
    print(f"   ❌ Dados sem IDs válidos: {dados_invalidos.validar()}")
    
    # Dados inválidos - valores fora de range
    dados_invalidos2 = MeteorologicalData(
        meteorological_data_source_id=1,
        cidade_id=1,
        data=date.today(),
        velocidade_vento=-5.0,  # Inválido
        temperatura=100.0,  # Inválido
        umidade=150.0  # Inválido
    )
    print(f"   ❌ Dados com valores inválidos: {dados_invalidos2.validar()}")
    
    # 2. Classificações de vento
    print("\n2️⃣ Classificações de vento...")
    
    velocidades_teste = [0.5, 2.0, 5.0, 8.0, 12.0, 18.0, 25.0, 30.0]
    
    for velocidade in velocidades_teste:
        dados_teste = MeteorologicalData(
            meteorological_data_source_id=1,
            cidade_id=1,
            data=date.today(),
            velocidade_vento=velocidade
        )
        classificacao = dados_teste.classificar_vento()
        print(f"   💨 {velocidade:5.1f} m/s = {classificacao}")
    
    # 3. Verificações de dados disponíveis
    print("\n3️⃣ Verificando dados disponíveis...")
    
    dados_completos = MeteorologicalData(
        meteorological_data_source_id=1,
        cidade_id=1,
        data=date.today(),
        velocidade_vento=7.2,
        temperatura=23.5,
        umidade=72.0
    )
    
    print(f"   🌪️ Tem dados de vento: {dados_completos.tem_dados_vento()}")
    print(f"   🌡️ Tem dados de temperatura: {dados_completos.tem_dados_temperatura()}")
    print(f"   💧 Tem dados de umidade: {dados_completos.tem_dados_umidade()}")
    print(f"   📊 String completa: {dados_completos}")


def exemplo_operacoes_limpeza():
    """Demonstra operações de limpeza e manutenção"""
    print("\n🧹 === OPERAÇÕES DE LIMPEZA E MANUTENÇÃO ===")
    
    dados_repo = MeteorologicalDataRepository()
    fonte_repo = MeteorologicalDataSourceRepository()
    
    # 1. Contagem inicial
    print("\n1️⃣ Contagem de registros...")
    todos_dados = dados_repo.listar_todos()
    todas_fontes = fonte_repo.listar_todos()
    print(f"   📊 Total de dados meteorológicos: {len(todos_dados)}")
    print(f"   📁 Total de fontes de dados: {len(todas_fontes)}")
    
    # 2. Limpeza por período (dados de teste mais antigos)
    print("\n2️⃣ Limpeza de dados antigos...")
    if todos_dados:
        # Buscar dados de teste antigos para limpeza
        data_limite = date.today() - timedelta(days=45)
        cidades = []
        for dados in todos_dados:
            if dados.data and dados.data < data_limite:
                cidades.append(dados.cidade_id)
        
        cidades_unicas = list(set(cidades))
        total_removidos = 0
        
        for cidade_id in cidades_unicas[:2]:  # Limpar apenas 2 cidades para demonstração
            data_inicio = date.today() - timedelta(days=60)
            data_fim = data_limite
            removidos = dados_repo.excluir_por_cidade_e_periodo(cidade_id, data_inicio, data_fim)
            total_removidos += removidos
            if removidos > 0:
                print(f"   🗑️ Removidos {removidos} registros antigos da cidade {cidade_id}")
        
        print(f"   ✅ Total de registros removidos: {total_removidos}")
    
    # 3. Contagem final
    print("\n3️⃣ Contagem final...")
    todos_dados_final = dados_repo.listar_todos()
    print(f"   📊 Total de dados meteorológicos restantes: {len(todos_dados_final)}")


def main():
    """Função principal que executa todos os exemplos"""
    print("🌪️ === EXEMPLO COMPLETO DO MÓDULO METEOROLÓGICO ===")
    print("Sistema de Simulação de Turbinas Eólicas")
    print("Demonstração de funcionalidades meteorológicas\n")
    
    try:
        # Configurar base de dados
        configurar_base_de_dados()
        
        # Executar exemplos
        ids_fontes = exemplo_crud_fontes_dados()
        ids_dados = exemplo_crud_dados_meteorologicos()
        exemplo_consultas_relacionais()
        exemplo_validacoes_e_classificacoes()
        exemplo_operacoes_limpeza()
        
        print("\n✅ === DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO ===")
        print(f"📊 Fontes criadas: {len(ids_fontes)}")
        print(f"🌤️ Dados meteorológicos criados: {len(ids_dados)}")
        print("\n🎯 Todas as funcionalidades do módulo meteorológico foram demonstradas!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
