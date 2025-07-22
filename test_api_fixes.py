"""
Script de teste para verificar as correções nas APIs e repository
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.api.nasa_power import NASAPowerClient
from meteorological.api.open_meteo import OpenMeteoClient
from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from meteorological.meteorological_data.entity import MeteorologicalData

def test_nasa_power_api():
    """Testa a API NASA POWER"""
    print("=== Testando NASA POWER API ===")
    
    try:
        client = NASAPowerClient()
        
        # Coordenadas de exemplo (São Paulo)
        latitude = -23.5505
        longitude = -46.6333
        data_inicio = date(2024, 1, 1)
        data_fim = date(2024, 1, 3)
        
        result = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10]
        )
        
        print(f"✅ Sucesso! Retornou {len(result.get('dados', []))} registros")
        
        # Verificar estrutura do retorno
        if 'dados' in result:
            primeiro_registro = result['dados'][0] if result['dados'] else None
            if primeiro_registro:
                print(f"📊 Primeiro registro: {primeiro_registro}")
                return True
        
        print("❌ Estrutura de retorno inválida")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_open_meteo_api():
    """Testa a API Open-Meteo"""
    print("\n=== Testando Open-Meteo API ===")
    
    try:
        client = OpenMeteoClient()
        
        # Coordenadas de exemplo (São Paulo)
        latitude = -23.5505
        longitude = -46.6333
        data_inicio = date(2024, 1, 1)
        data_fim = date(2024, 1, 3)
        
        result = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10]
        )
        
        print(f"✅ Sucesso! Retornou {len(result.get('dados', []))} registros")
        
        # Verificar estrutura do retorno
        if 'dados' in result:
            primeiro_registro = result['dados'][0] if result['dados'] else None
            if primeiro_registro:
                print(f"📊 Primeiro registro: {primeiro_registro}")
                return True
        
        print("❌ Estrutura de retorno inválida")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_repository():
    """Testa o repository"""
    print("\n=== Testando Repository ===")
    
    try:
        repo = MeteorologicalDataRepository()
        
        # Verificar se os métodos existem
        if not hasattr(repo, 'salvar'):
            print("❌ Método 'salvar' não encontrado")
            return False
        
        if not hasattr(repo, 'buscar_por_periodo'):
            print("❌ Método 'buscar_por_periodo' não encontrado")
            return False
        
        print("✅ Métodos 'salvar' e 'buscar_por_periodo' encontrados")
        
        # Criar tabela
        repo.criar_tabela()
        print("✅ Tabela criada/verificada")
        
        # Testar dados de exemplo
        dados_teste = MeteorologicalData(
            cidade_id=1,
            meteorological_data_source_id=1,
            data=date(2024, 1, 1),
            temperatura=25.0,
            umidade=60.0,
            velocidade_vento=5.5,
            altura_captura=10
        )
        
        # Verificar validação
        if dados_teste.validar():
            print("✅ Validação de dados funcionando")
        else:
            print("❌ Validação de dados falhou")
            return False
        
        print("✅ Repository está funcionando corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro no repository: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 Iniciando testes de correção das APIs e Repository...")
    
    tests = [
        test_repository,
        test_nasa_power_api,
        test_open_meteo_api
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Resumo dos testes:")
    print(f"✅ Sucessos: {sum(results)}")
    print(f"❌ Falhas: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 Todos os testes passaram! As correções foram bem-sucedidas.")
    else:
        print("\n⚠️ Alguns testes falharam. Verificar logs acima.")

if __name__ == "__main__":
    main()
