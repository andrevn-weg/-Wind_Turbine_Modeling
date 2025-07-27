"""
Teste de diagnóstico para NASA POWER API

Este script testa diferentes aspectos da NASA POWER API para identificar
problemas com a obtenção de dados de vento, temperatura e umidade.
"""

import sys
import os
from datetime import datetime, date, timedelta
import json
import requests

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.nasa_power import NASAPowerClient


def testar_requisicao_direta():
    """Testa uma requisição direta à API NASA POWER para debugging."""
    print("=" * 60)
    print("TESTE 1: REQUISIÇÃO DIRETA À API NASA POWER")
    print("=" * 60)
    
    # Parâmetros de teste (Santa Maria, RS)
    latitude = -29.6842
    longitude = -53.8069
    data_inicio = "20240101"
    data_fim = "20240105"  # Apenas alguns dias para teste
    
    # URL da API
    base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    
    # Parâmetros da requisição
    params = {
        'start': data_inicio,
        'end': data_fim,
        'latitude': latitude,
        'longitude': longitude,
        'community': 'RE',
        'parameters': 'WS10M,WS50M,T2M,RH2M',
        'format': 'JSON',
        'header': 'true',
        'time-standard': 'UTC'
    }
    
    print(f"URL: {base_url}")
    print(f"Parâmetros: {params}")
    print()
    
    try:
        response = requests.get(base_url, params=params, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"URL Final: {response.url}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            # Mostrar estrutura da resposta
            print("ESTRUTURA DA RESPOSTA:")
            print(f"Keys principais: {list(data.keys())}")
            
            if 'properties' in data:
                properties = data['properties']
                print(f"Properties keys: {list(properties.keys())}")
                
                if 'parameter' in properties:
                    parameter_data = properties['parameter']
                    print(f"Parâmetros disponíveis: {list(parameter_data.keys())}")
                    
                    for param, param_data in parameter_data.items():
                        if param_data:
                            total_valores = len(param_data)
                            valores_validos = sum(1 for v in param_data.values() if v is not None and v != -999)
                            print(f"  {param}: {valores_validos}/{total_valores} valores válidos")
                            
                            # Mostrar alguns valores de exemplo
                            if valores_validos > 0:
                                primeiros_valores = list(param_data.items())[:3]
                                print(f"    Exemplos: {primeiros_valores}")
                        else:
                            print(f"  {param}: SEM DADOS")
            
            # Salvar resposta completa para análise
            with open('nasa_power_resposta_completa.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\nResposta completa salva em: nasa_power_resposta_completa.json")
            
        else:
            print(f"ERRO HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"ERRO na requisição: {e}")
        import traceback
        traceback.print_exc()


def testar_cliente_nasa():
    """Testa o cliente NASA POWER implementado."""
    print("\n" + "=" * 60)
    print("TESTE 2: CLIENTE NASA POWER IMPLEMENTADO")
    print("=" * 60)
    
    client = NASAPowerClient()
    
    # Testar informações da API
    print("INFORMAÇÕES DA API:")
    info = client.obter_informacoes_api()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Testar parâmetros disponíveis
    print("PARÂMETROS DISPONÍVEIS:")
    parametros = client.obter_parametros_disponiveis()
    for param, info in parametros.items():
        print(f"  {param}: {info['descricao']} ({info['unidade']})")
    print()
    
    # Testar obtenção de dados
    try:
        print("TESTANDO OBTENÇÃO DE DADOS...")
        latitude = -29.6842  # Santa Maria, RS
        longitude = -53.8069
        data_inicio = date(2024, 1, 1)
        data_fim = date(2024, 1, 5)
        
        print(f"Local: {latitude}, {longitude}")
        print(f"Período: {data_inicio} a {data_fim}")
        
        # Verificar disponibilidade do período
        disponibilidade = client.verificar_disponibilidade_periodo(data_inicio, data_fim)
        print(f"Período disponível: {disponibilidade['disponivel']}")
        if disponibilidade['avisos']:
            print("Avisos:")
            for aviso in disponibilidade['avisos']:
                print(f"  - {aviso}")
        print()
        
        # Obter dados
        resultado = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10, 50],
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        print("RESULTADO:")
        print(f"Metadata: {resultado['metadata']}")
        print(f"Alturas com dados: {list(resultado['dados_por_altura'].keys())}")
        print(f"Total de registros: {len(resultado['dados'])}")
        
        # Mostrar estatísticas por altura
        for altura, dados_altura in resultado['dados_por_altura'].items():
            print(f"\nAltura {altura}:")
            print(f"  Estatísticas: {dados_altura['estatisticas']}")
            
        # Mostrar primeiros registros
        if resultado['dados']:
            print(f"\nPrimeiros 5 registros:")
            for i, registro in enumerate(resultado['dados'][:5]):
                print(f"  {i+1}: {registro}")
        
        # Salvar resultado para análise
        # Converter datetime para string para JSON
        resultado_json = resultado.copy()
        for registro in resultado_json['dados']:
            if 'data_hora' in registro and isinstance(registro['data_hora'], datetime):
                registro['data_hora'] = registro['data_hora'].isoformat()
        
        with open('nasa_power_resultado_processado.json', 'w', encoding='utf-8') as f:
            json.dump(resultado_json, f, indent=2, ensure_ascii=False)
        print(f"\nResultado processado salvo em: nasa_power_resultado_processado.json")
        
    except Exception as e:
        print(f"ERRO no cliente: {e}")
        import traceback
        traceback.print_exc()


def testar_diferentes_localizacoes():
    """Testa diferentes localizações para ver se o problema é regional."""
    print("\n" + "=" * 60)
    print("TESTE 3: DIFERENTES LOCALIZAÇÕES")
    print("=" * 60)
    
    localizacoes = [
        {"nome": "Santa Maria, RS", "lat": -29.6842, "lon": -53.8069},
        {"nome": "São Paulo, SP", "lat": -23.5505, "lon": -46.6333},
        {"nome": "Brasília, DF", "lat": -15.7942, "lon": -47.8822},
        {"nome": "Miami, FL (EUA)", "lat": 25.7617, "lon": -80.1918},
        {"nome": "Londres, Reino Unido", "lat": 51.5074, "lon": -0.1278}
    ]
    
    client = NASAPowerClient()
    data_inicio = date(2024, 1, 1)
    data_fim = date(2024, 1, 2)  # Apenas 1 dia para teste rápido
    
    for local in localizacoes:
        print(f"\nTestando: {local['nome']} ({local['lat']}, {local['lon']})")
        
        try:
            resultado = client.obter_dados_historicos_vento(
                latitude=local['lat'],
                longitude=local['lon'],
                data_inicio=data_inicio,
                data_fim=data_fim,
                alturas=[10, 50],
                incluir_temperatura=True,
                incluir_umidade=True
            )
            
            total_registros = len(resultado['dados'])
            alturas_com_dados = list(resultado['dados_por_altura'].keys())
            
            print(f"  ✓ Sucesso: {total_registros} registros, alturas: {alturas_com_dados}")
            
            # Verificar se há dados válidos
            dados_validos = sum(1 for r in resultado['dados'] if r['velocidade_vento'] is not None)
            print(f"  Dados válidos: {dados_validos}/{total_registros}")
            
        except Exception as e:
            print(f"  ✗ Erro: {e}")


def testar_diferentes_periodos():
    """Testa diferentes períodos para identificar problemas temporais."""
    print("\n" + "=" * 60)
    print("TESTE 4: DIFERENTES PERÍODOS")
    print("=" * 60)
    
    periodos = [
        {"nome": "Janeiro 2024", "inicio": date(2024, 1, 1), "fim": date(2024, 1, 3)},
        {"nome": "Julho 2024", "inicio": date(2024, 7, 1), "fim": date(2024, 7, 3)},
        {"nome": "Dezembro 2023", "inicio": date(2023, 12, 1), "fim": date(2023, 12, 3)},
        {"nome": "Janeiro 2023", "inicio": date(2023, 1, 1), "fim": date(2023, 1, 3)},
        {"nome": "Recente (1 semana atrás)", "inicio": date.today() - timedelta(days=14), "fim": date.today() - timedelta(days=12)}
    ]
    
    client = NASAPowerClient()
    latitude = -29.6842  # Santa Maria, RS
    longitude = -53.8069
    
    for periodo in periodos:
        print(f"\nTestando período: {periodo['nome']}")
        print(f"  {periodo['inicio']} a {periodo['fim']}")
        
        try:
            resultado = client.obter_dados_historicos_vento(
                latitude=latitude,
                longitude=longitude,
                data_inicio=periodo['inicio'],
                data_fim=periodo['fim'],
                alturas=[10, 50],
                incluir_temperatura=True,
                incluir_umidade=True
            )
            
            total_registros = len(resultado['dados'])
            alturas_com_dados = list(resultado['dados_por_altura'].keys())
            
            print(f"  ✓ Sucesso: {total_registros} registros, alturas: {alturas_com_dados}")
            
            # Mostrar estatísticas básicas
            if resultado['dados']:
                velocidades_validas = [r['velocidade_vento'] for r in resultado['dados'] if r['velocidade_vento'] is not None]
                if velocidades_validas:
                    print(f"  Velocidade média: {sum(velocidades_validas)/len(velocidades_validas):.2f} m/s")
                    print(f"  Velocidade máxima: {max(velocidades_validas):.2f} m/s")
                else:
                    print("  ⚠️ Nenhum dado de velocidade válido")
            
        except Exception as e:
            print(f"  ✗ Erro: {e}")


def main():
    """Executa todos os testes de diagnóstico."""
    print("DIAGNÓSTICO NASA POWER API")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now()}")
    print()
    
    # Executar testes
    testar_requisicao_direta()
    testar_cliente_nasa()
    testar_diferentes_localizacoes()
    testar_diferentes_periodos()
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)
    print("Arquivos gerados:")
    print("- nasa_power_resposta_completa.json: Resposta bruta da API")
    print("- nasa_power_resultado_processado.json: Dados processados pelo cliente")
    print()
    print("Analise os arquivos gerados para identificar problemas na API ou no processamento.")


if __name__ == "__main__":
    main()
