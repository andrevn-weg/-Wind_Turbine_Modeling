#!/usr/bin/env python3
"""
Script para Re-coletar Dados Meteorológicos com Temperatura e Umidade

Este script permite re-coletar dados meteorológicos existentes para incluir
temperatura e umidade nos registros que ainda não possuem esses dados.
"""

from datetime import datetime, date
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
from meteorological.meteorological_data.entity import MeteorologicalData
from meteorological.api.open_meteo import OpenMeteoClient
from meteorological.api.nasa_power import NASAPowerClient
from geographic import CidadeRepository


def analisar_dados_existentes():
    """Analisa dados existentes para identificar quais precisam de temperatura/umidade"""
    print("🔍 Analisando dados meteorológicos existentes...")
    
    repo = MeteorologicalDataRepository()
    dados = repo.listar_todos()
    
    if not dados:
        print("❌ Nenhum dado meteorológico encontrado no banco.")
        return []
    
    # Estatísticas gerais
    total_registros = len(dados)
    registros_com_temp = sum(1 for d in dados if d.tem_dados_temperatura())
    registros_com_umid = sum(1 for d in dados if d.tem_dados_umidade())
    
    print(f"📊 Total de registros: {total_registros}")
    print(f"🌡️ Registros com temperatura: {registros_com_temp} ({registros_com_temp/total_registros*100:.1f}%)")
    print(f"💧 Registros com umidade: {registros_com_umid} ({registros_com_umid/total_registros*100:.1f}%)")
    
    # Identificar registros sem temperatura ou umidade
    registros_incompletos = []
    for dado in dados:
        if not dado.tem_dados_temperatura() or not dado.tem_dados_umidade():
            registros_incompletos.append(dado)
    
    print(f"⚠️ Registros incompletos: {len(registros_incompletos)} ({len(registros_incompletos)/total_registros*100:.1f}%)")
    
    return registros_incompletos


def agrupar_por_periodo_e_cidade(registros):
    """Agrupa registros por cidade, fonte e período para otimizar re-coleta"""
    print("📋 Agrupando registros para otimizar re-coleta...")
    
    grupos = {}
    
    for registro in registros:
        chave = (registro.cidade_id, registro.meteorological_data_source_id, registro.altura_captura)
        
        if chave not in grupos:
            grupos[chave] = {
                'cidade_id': registro.cidade_id,
                'fonte_id': registro.meteorological_data_source_id,
                'altura': registro.altura_captura,
                'registros': [],
                'data_min': registro.data_hora.date(),
                'data_max': registro.data_hora.date()
            }
        
        grupos[chave]['registros'].append(registro)
        
        # Atualizar período
        data_registro = registro.data_hora.date()
        if data_registro < grupos[chave]['data_min']:
            grupos[chave]['data_min'] = data_registro
        if data_registro > grupos[chave]['data_max']:
            grupos[chave]['data_max'] = data_registro
    
    print(f"🗂️ Criados {len(grupos)} grupos de re-coleta")
    
    return grupos


def re_coletar_grupo(grupo, cidade_repo, fonte_repo):
    """Re-coleta dados de temperatura e umidade para um grupo específico"""
    print(f"\n🔄 Re-coletando dados para grupo: Cidade {grupo['cidade_id']}, Fonte {grupo['fonte_id']}, Altura {grupo['altura']}m")
    
    # Buscar informações da cidade
    cidade = cidade_repo.buscar_por_id(grupo['cidade_id'])
    if not cidade:
        print(f"❌ Cidade {grupo['cidade_id']} não encontrada")
        return False
    
    # Buscar informações da fonte
    fonte = fonte_repo.buscar_por_id(grupo['fonte_id'])
    if not fonte:
        print(f"❌ Fonte {grupo['fonte_id']} não encontrada")
        return False
    
    print(f"📍 Cidade: {cidade.nome} ({cidade.latitude:.4f}, {cidade.longitude:.4f})")
    print(f"📡 Fonte: {fonte.name}")
    print(f"📏 Altura: {grupo['altura']}m")
    print(f"📅 Período: {grupo['data_min']} a {grupo['data_max']}")
    print(f"📊 Registros: {len(grupo['registros'])}")
    
    # Escolher cliente da API
    if fonte.name == 'OPEN_METEO':
        cliente = OpenMeteoClient()
    elif fonte.name == 'NASA_POWER':
        cliente = NASAPowerClient()
    else:
        print(f"❌ Fonte {fonte.name} não suportada para re-coleta")
        return False
    
    try:
        # Coletar apenas temperatura e umidade (vento já existe)
        print("🌡️💧 Coletando dados de temperatura e umidade...")
        
        dados_api = cliente.obter_dados_historicos_vento(
            latitude=cidade.latitude,
            longitude=cidade.longitude,
            data_inicio=grupo['data_min'],
            data_fim=grupo['data_max'],
            alturas=[grupo['altura']],
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        if not dados_api or 'dados' not in dados_api:
            print("❌ Nenhum dado retornado pela API")
            return False
        
        # Mapear dados da API por timestamp
        dados_por_timestamp = {}
        for dado_api in dados_api['dados']:
            timestamp_key = dado_api['data_hora'].replace(tzinfo=None)  # Remover timezone para comparação
            dados_por_timestamp[timestamp_key] = {
                'temperatura': dado_api.get('temperatura'),
                'umidade': dado_api.get('umidade')
            }
        
        # Atualizar registros existentes
        repo = MeteorologicalDataRepository()
        atualizados = 0
        
        for registro in grupo['registros']:
            timestamp_registro = registro.data_hora.replace(tzinfo=None)
            
            # Encontrar dados correspondentes (com tolerância de 1 hora)
            dados_correspondentes = None
            for ts, dados in dados_por_timestamp.items():
                if abs((ts - timestamp_registro).total_seconds()) <= 3600:  # 1 hora de tolerância
                    dados_correspondentes = dados
                    break
            
            if dados_correspondentes:
                # Atualizar apenas se não tem dados
                atualizar = False
                
                if not registro.tem_dados_temperatura() and dados_correspondentes['temperatura'] is not None:
                    registro.temperatura = dados_correspondentes['temperatura']
                    atualizar = True
                
                if not registro.tem_dados_umidade() and dados_correspondentes['umidade'] is not None:
                    registro.umidade = dados_correspondentes['umidade']
                    atualizar = True
                
                if atualizar:
                    repo.atualizar(registro)
                    atualizados += 1
        
        print(f"✅ {atualizados} registros atualizados com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao re-coletar dados: {e}")
        return False


def main():
    """Função principal do script de re-coleta"""
    print("🔄 Re-coleta de Dados Meteorológicos - Temperatura e Umidade")
    print("=" * 60)
    
    # Analisar dados existentes
    registros_incompletos = analisar_dados_existentes()
    
    if not registros_incompletos:
        print("\n🎉 Todos os registros já possuem dados completos!")
        return
    
    # Confirmar se deseja prosseguir
    print(f"\n⚠️ Serão re-coletados dados para {len(registros_incompletos)} registros.")
    resposta = input("Deseja prosseguir? (s/N): ").lower().strip()
    
    if resposta != 's':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Agrupar registros
    grupos = agrupar_por_periodo_e_cidade(registros_incompletos)
    
    # Inicializar repositórios
    cidade_repo = CidadeRepository()
    fonte_repo = MeteorologicalDataSourceRepository()
    
    # Processar cada grupo
    sucessos = 0
    for i, grupo in enumerate(grupos.values(), 1):
        print(f"\n📋 Processando grupo {i}/{len(grupos)}")
        
        if re_coletar_grupo(grupo, cidade_repo, fonte_repo):
            sucessos += 1
    
    # Resumo final
    print("\n" + "=" * 60)
    print(f"📊 Resumo: {sucessos}/{len(grupos)} grupos processados com sucesso")
    
    if sucessos == len(grupos):
        print("🎉 Re-coleta concluída com sucesso!")
    else:
        print("⚠️ Alguns grupos falharam. Verifique os logs acima.")
    
    # Análise final
    print("\n🔍 Análise final dos dados...")
    analisar_dados_existentes()


if __name__ == "__main__":
    main()
