"""
Teste final completo da NASA POWER API

Este exemplo demonstra o uso completo da API NASA POWER corrigida,
incluindo testes de diferentes cenários e validações.
"""

import sys
import os
from datetime import datetime, date, timedelta
import json

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.nasa_power import NASAPowerClient


def teste_basico():
    """Teste básico da funcionalidade principal."""
    print("=" * 60)
    print("TESTE BÁSICO - NASA POWER API")
    print("=" * 60)
    
    client = NASAPowerClient()
    
    # Parâmetros de teste
    latitude = -29.6842  # Santa Maria, RS
    longitude = -53.8069
    data_inicio = date(2024, 6, 1)
    data_fim = date(2024, 6, 3)
    
    print(f"Local: Santa Maria, RS ({latitude}, {longitude})")
    print(f"Período: {data_inicio} a {data_fim}")
    print()
    
    try:
        resultado = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10, 50],
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        # Verificar metadata
        metadata = resultado['metadata']
        print("METADATA:")
        print(f"  Fonte: {metadata['fonte']}")
        print(f"  Dados incluídos:")
        for tipo, incluido in metadata['dados_incluidos'].items():
            print(f"    {tipo.replace('_', ' ').title()}: {incluido}")
        print(f"  Alturas de captura:")
        for tipo, alturas in metadata['alturas_dados'].items():
            print(f"    {tipo.replace('_', ' ').title()}: {alturas}")
        print(f"  Total de registros: {metadata['total_registros']}")
        print(f"  Período: {metadata['periodo_inicio']} até {metadata['periodo_fim']}")
        print()
        
        # Verificar dados por altura
        print("DADOS POR ALTURA:")
        for altura_str, dados_altura in resultado['dados_por_altura'].items():
            stats = dados_altura['estatisticas']
            print(f"  {altura_str}:")
            print(f"    Registros válidos: {stats['total_registros']}")
            print(f"    Velocidade média: {stats['velocidade_media']:.2f} m/s")
            print(f"    Velocidade máxima: {stats['velocidade_maxima']:.2f} m/s")
            print(f"    Velocidade mínima: {stats['velocidade_minima']:.2f} m/s")
        print()
        
        # Verificar registros individuais
        total_registros = len(resultado['dados'])
        dados_completos = sum(1 for r in resultado['dados'] 
                             if r['velocidade_vento'] is not None 
                             and r['temperatura'] is not None 
                             and r['umidade'] is not None)
        
        print("QUALIDADE DOS DADOS:")
        print(f"  Total de registros: {total_registros}")
        print(f"  Registros completos: {dados_completos} ({dados_completos/total_registros*100:.1f}%)")
        
        # Mostrar exemplos
        print(f"\nPrimeiros 5 registros:")
        for i, registro in enumerate(resultado['dados'][:5]):
            print(f"  {i+1}: {registro['data_hora']} | "
                  f"Vel: {registro['velocidade_vento']:.2f}m/s | "
                  f"Temp: {registro['temperatura']:.1f}°C | "
                  f"Umid: {registro['umidade']:.1f}% | "
                  f"Alt: {registro['altura_captura']}m")
        
        print("\n✅ TESTE BÁSICO: SUCESSO")
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste básico: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_sem_temperatura_umidade():
    """Teste sem incluir temperatura e umidade."""
    print("\n" + "=" * 60)
    print("TESTE SEM TEMPERATURA E UMIDADE")
    print("=" * 60)
    
    client = NASAPowerClient()
    
    try:
        resultado = client.obter_dados_historicos_vento(
            latitude=-23.5505,  # São Paulo
            longitude=-46.6333,
            data_inicio=date(2024, 3, 1),
            data_fim=date(2024, 3, 2),
            alturas=[10, 50],
            incluir_temperatura=False,
            incluir_umidade=False
        )
        
        metadata = resultado['metadata']
        dados_incluidos = metadata['dados_incluidos']
        
        print("VERIFICAÇÃO DE CONFIGURAÇÃO:")
        print(f"  Velocidade vento incluída: {dados_incluidos['velocidade_vento']}")
        print(f"  Temperatura incluída: {dados_incluidos['temperatura']}")
        print(f"  Umidade incluída: {dados_incluidos['umidade']}")
        
        # Verificar se os dados realmente não incluem temperatura/umidade
        tem_temp = any(r['temperatura'] is not None for r in resultado['dados'])
        tem_umid = any(r['umidade'] is not None for r in resultado['dados'])
        
        print(f"  Dados com temperatura: {tem_temp}")
        print(f"  Dados com umidade: {tem_umid}")
        
        if not tem_temp and not tem_umid:
            print("\n✅ TESTE SEM TEMP/UMIDADE: SUCESSO")
            return True
        else:
            print("\n❌ TESTE SEM TEMP/UMIDADE: FALHOU - dados ainda contêm temp/umidade")
            return False
            
    except Exception as e:
        print(f"❌ ERRO no teste sem temp/umidade: {e}")
        return False


def teste_periodo_sem_dados():
    """Teste com período que pode não ter dados."""
    print("\n" + "=" * 60)
    print("TESTE PERÍODO FUTURO (SEM DADOS)")
    print("=" * 60)
    
    client = NASAPowerClient()
    
    # Tentar período futuro (sem dados)
    data_futura = date.today() + timedelta(days=30)
    
    try:
        resultado = client.obter_dados_historicos_vento(
            latitude=0,  # Equador
            longitude=0,  # Greenwich
            data_inicio=data_futura,
            data_fim=data_futura,
            alturas=[10, 50]
        )
        
        print("⚠️  INESPERADO: Conseguiu dados para período futuro")
        print(f"   Total de registros: {len(resultado['dados'])}")
        return False
        
    except Exception as e:
        print(f"✅ ESPERADO: Erro ao tentar período futuro - {e}")
        return True


def teste_validacao_parametros():
    """Teste de validação de parâmetros."""
    print("\n" + "=" * 60)
    print("TESTE VALIDAÇÃO DE PARÂMETROS")
    print("=" * 60)
    
    client = NASAPowerClient()
    
    testes_validacao = [
        {
            'nome': 'Latitude inválida',
            'params': {'latitude': 95, 'longitude': 0, 'data_inicio': date(2024, 1, 1), 'data_fim': date(2024, 1, 2)},
            'deve_falhar': True
        },
        {
            'nome': 'Longitude inválida', 
            'params': {'latitude': 0, 'longitude': 200, 'data_inicio': date(2024, 1, 1), 'data_fim': date(2024, 1, 2)},
            'deve_falhar': True
        },
        {
            'nome': 'Altura inválida',
            'params': {'latitude': 0, 'longitude': 0, 'data_inicio': date(2024, 1, 1), 'data_fim': date(2024, 1, 2), 'alturas': [100]},
            'deve_falhar': True
        },
        {
            'nome': 'Parâmetros válidos',
            'params': {'latitude': -29.68, 'longitude': -53.81, 'data_inicio': date(2024, 1, 1), 'data_fim': date(2024, 1, 1), 'alturas': [10]},
            'deve_falhar': False
        }
    ]
    
    sucessos = 0
    for teste in testes_validacao:
        try:
            resultado = client.obter_dados_historicos_vento(**teste['params'])
            
            if teste['deve_falhar']:
                print(f"  ❌ {teste['nome']}: Deveria ter falhado mas passou")
            else:
                print(f"  ✅ {teste['nome']}: Passou corretamente")
                sucessos += 1
                
        except Exception as e:
            if teste['deve_falhar']:
                print(f"  ✅ {teste['nome']}: Falhou como esperado - {str(e)[:50]}...")
                sucessos += 1
            else:
                print(f"  ❌ {teste['nome']}: Não deveria ter falhado - {e}")
    
    print(f"\nResultado da validação: {sucessos}/{len(testes_validacao)} sucessos")
    return sucessos == len(testes_validacao)


def main():
    """Executa todos os testes."""
    print("TESTE COMPLETO - NASA POWER API CORRIGIDA")
    print(f"Data/Hora: {datetime.now()}")
    print(f"Versão Python: {sys.version}")
    print()
    
    # Executar testes
    resultados = []
    
    resultados.append(("Teste Básico", teste_basico()))
    resultados.append(("Teste Sem Temp/Umidade", teste_sem_temperatura_umidade()))
    resultados.append(("Teste Período Sem Dados", teste_periodo_sem_dados()))
    resultados.append(("Teste Validação Parâmetros", teste_validacao_parametros()))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"  {nome}: {status}")
        if sucesso:
            sucessos += 1
    
    print(f"\nResultado Final: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM - NASA POWER API FUNCIONANDO CORRETAMENTE!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM - Verifique os problemas acima")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)


if __name__ == "__main__":
    main()
