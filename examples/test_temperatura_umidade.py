#!/usr/bin/env python3
"""
Exemplo de Uso das APIs Meteorológicas com Temperatura e Umidade

Este script demonstra como usar as APIs Open-Meteo e NASA POWER para coletar
dados de velocidade do vento, temperatura e umidade relativa.
"""

from datetime import date, datetime
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.api.open_meteo import OpenMeteoClient
from meteorological.api.nasa_power import NASAPowerClient
from meteorological.meteorological_data.entity import MeteorologicalData


def exemplo_open_meteo():
    """Exemplo de uso da API Open-Meteo com temperatura e umidade"""
    print("🌍 Testando Open-Meteo API com temperatura e umidade...")
    
    client = OpenMeteoClient()
    
    # Coordenadas de Blumenau, SC
    latitude = -26.4869
    longitude = -49.0679
    
    try:
        # Coletar dados com todos os parâmetros
        dados = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 1, 7),  # Uma semana de dados
            alturas=[10],  # Apenas 10m para o exemplo
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        print("✅ Dados coletados com sucesso!")
        
        # Exibir metadados
        metadata = dados.get('metadata', {})
        print(f"📍 Localização: {metadata.get('latitude')}, {metadata.get('longitude')}")
        print(f"📊 Total de registros: {metadata.get('total_registros')}")
        print(f"📅 Período: {metadata.get('periodo_inicio')} a {metadata.get('periodo_fim')}")
        
        # Informações sobre dados incluídos
        dados_incluidos = metadata.get('dados_incluidos', {})
        alturas_dados = metadata.get('alturas_dados', {})
        
        print("\n📡 Dados coletados:")
        print(f"  🌪️ Velocidade do vento: {dados_incluidos.get('velocidade_vento')} - Alturas: {alturas_dados.get('velocidade_vento')}")
        print(f"  🌡️ Temperatura: {dados_incluidos.get('temperatura')} - Altura: {alturas_dados.get('temperatura')}")
        print(f"  💧 Umidade: {dados_incluidos.get('umidade')} - Altura: {alturas_dados.get('umidade')}")
        
        # Exibir alguns registros de exemplo
        print("\n📋 Primeiros 5 registros:")
        for i, registro in enumerate(dados.get('dados', [])[:5]):
            print(f"  {i+1}. {registro['data_hora'].strftime('%Y-%m-%d %H:%M')} | "
                  f"Vento: {registro['velocidade_vento']:.1f}m/s | "
                  f"Temp: {registro['temperatura']:.1f}°C | "
                  f"Umidade: {registro['umidade']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados Open-Meteo: {e}")
        return False


def exemplo_nasa_power():
    """Exemplo de uso da API NASA POWER com temperatura e umidade"""
    print("\n\n🛰️ Testando NASA POWER API com temperatura e umidade...")
    
    client = NASAPowerClient()
    
    # Coordenadas de Blumenau, SC
    latitude = -26.4869
    longitude = -49.0679
    
    try:
        # Coletar dados com todos os parâmetros
        dados = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio='20240101',  # NASA usa formato YYYYMMDD
            data_fim='20240107',
            alturas=[10],  # Apenas 10m para o exemplo
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        print("✅ Dados coletados com sucesso!")
        
        # Exibir metadados
        metadata = dados.get('metadata', {})
        print(f"📍 Localização: {metadata.get('latitude')}, {metadata.get('longitude')}")
        print(f"📊 Total de registros: {metadata.get('total_registros')}")
        print(f"📅 Período: {metadata.get('periodo_inicio')} a {metadata.get('periodo_fim')}")
        
        # Informações sobre dados incluídos
        dados_incluidos = metadata.get('dados_incluidos', {})
        alturas_dados = metadata.get('alturas_dados', {})
        
        print("\n📡 Dados coletados:")
        print(f"  🌪️ Velocidade do vento: {dados_incluidos.get('velocidade_vento')} - Alturas: {alturas_dados.get('velocidade_vento')}")
        print(f"  🌡️ Temperatura: {dados_incluidos.get('temperatura')} - Altura: {alturas_dados.get('temperatura')}")
        print(f"  💧 Umidade: {dados_incluidos.get('umidade')} - Altura: {alturas_dados.get('umidade')}")
        
        # Exibir alguns registros de exemplo
        print("\n📋 Primeiros 5 registros:")
        for i, registro in enumerate(dados.get('dados', [])[:5]):
            temp_str = f"{registro['temperatura']:.1f}°C" if registro['temperatura'] is not None else "N/A"
            umid_str = f"{registro['umidade']:.1f}%" if registro['umidade'] is not None else "N/A"
            
            print(f"  {i+1}. {registro['data_hora'].strftime('%Y-%m-%d %H:%M')} | "
                  f"Vento: {registro['velocidade_vento']:.1f}m/s | "
                  f"Temp: {temp_str} | "
                  f"Umidade: {umid_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados NASA POWER: {e}")
        return False


def exemplo_entidade_meteorologica():
    """Exemplo de uso da entidade MeteorologicalData com novos campos"""
    print("\n\n🏗️ Testando entidade MeteorologicalData com temperatura e umidade...")
    
    # Criar um dado meteorológico completo
    dado = MeteorologicalData(
        meteorological_data_source_id=1,
        cidade_id=1,
        data_hora=datetime.now(),
        altura_captura=10.0,
        velocidade_vento=5.5,
        temperatura=22.3,
        umidade=65.2
    )
    
    print("✅ Entidade criada com sucesso!")
    print(f"📊 Dados: {dado}")
    
    # Testar validação
    if dado.validar():
        print("✅ Dados válidos!")
    else:
        print("❌ Dados inválidos!")
    
    # Testar métodos de verificação
    print(f"🌪️ Tem dados de vento: {dado.tem_dados_vento()}")
    print(f"🌡️ Tem dados de temperatura: {dado.tem_dados_temperatura()}")
    print(f"💧 Tem dados de umidade: {dado.tem_dados_umidade()}")
    print(f"📊 Classificação do vento: {dado.classificar_vento()}")
    
    # Testar conversão para dicionário
    dados_dict = dado.to_dict()
    print(f"📋 Dados em formato dict: {dados_dict}")
    
    return True


def exemplo_somente_vento():
    """Exemplo mostrando compatibilidade com código antigo (só vento)"""
    print("\n\n🔄 Testando compatibilidade com código antigo (apenas vento)...")
    
    client = OpenMeteoClient()
    
    try:
        # Usar a API como antes, sem temperatura e umidade
        dados = client.obter_dados_historicos_vento(
            latitude=-26.4869,
            longitude=-49.0679,
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 1, 2),
            alturas=[10],
            incluir_temperatura=False,
            incluir_umidade=False
        )
        
        print("✅ Compatibilidade mantida! Código antigo funciona normalmente.")
        
        # Verificar que apenas vento foi coletado
        metadata = dados.get('metadata', {})
        dados_incluidos = metadata.get('dados_incluidos', {})
        
        print(f"🌪️ Vento incluído: {dados_incluidos.get('velocidade_vento')}")
        print(f"🌡️ Temperatura incluída: {dados_incluidos.get('temperatura')}")
        print(f"💧 Umidade incluída: {dados_incluidos.get('umidade')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de compatibilidade: {e}")
        return False


def main():
    """Função principal dos exemplos"""
    print("🌤️ Exemplos de Uso - Dados Meteorológicos com Temperatura e Umidade")
    print("=" * 70)
    
    sucessos = 0
    total_testes = 4
    
    # Teste 1: Open-Meteo
    if exemplo_open_meteo():
        sucessos += 1
    
    # Teste 2: NASA POWER
    if exemplo_nasa_power():
        sucessos += 1
    
    # Teste 3: Entidade
    if exemplo_entidade_meteorologica():
        sucessos += 1
    
    # Teste 4: Compatibilidade
    if exemplo_somente_vento():
        sucessos += 1
    
    # Resumo final
    print("\n" + "=" * 70)
    print(f"📊 Resumo: {sucessos}/{total_testes} testes executados com sucesso")
    
    if sucessos == total_testes:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique as mensagens de erro acima.")


if __name__ == "__main__":
    main()
