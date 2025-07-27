"""
Debug da validação de disponibilidade dos dados
"""

import sys
import os
from datetime import date

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.nasa_power import NASAPowerClient

def debug_disponibilidade():
    client = NASAPowerClient()
    
    # Parâmetros
    latitude = -29.6842
    longitude = -53.8069
    data_inicio = date(2024, 1, 1)
    data_fim = date(2024, 1, 2)
    incluir_temperatura = True
    incluir_umidade = True
    
    # Fazer requisição direta para ver os dados brutos
    import requests
    
    params = {
        'start': data_inicio.strftime('%Y%m%d'),
        'end': data_fim.strftime('%Y%m%d'),
        'latitude': latitude,
        'longitude': longitude,
        'community': 'RE',
        'parameters': 'WS10M,WS50M,T2M,RH2M',
        'format': 'JSON',
        'header': 'true',
        'time-standard': 'UTC'
    }
    
    response = requests.get("https://power.larc.nasa.gov/api/temporal/hourly/point", params=params)
    data = response.json()
    
    properties = data['properties']
    parameter_data = properties.get('parameter', {})
    
    print("DADOS BRUTOS DA API:")
    print(f"Parâmetros disponíveis: {list(parameter_data.keys())}")
    
    for param, param_data in parameter_data.items():
        print(f"{param}: tipo={type(param_data)}, vazio={not param_data}, len={len(param_data) if param_data else 0}")
    
    print("\nVALIDAÇÃO:")
    temperatura_disponivel = incluir_temperatura and 'T2M' in parameter_data and parameter_data['T2M']
    umidade_disponivel = incluir_umidade and 'RH2M' in parameter_data and parameter_data['RH2M']
    
    print(f"incluir_temperatura: {incluir_temperatura}")
    print(f"'T2M' in parameter_data: {'T2M' in parameter_data}")
    print(f"parameter_data['T2M']: {bool(parameter_data['T2M']) if 'T2M' in parameter_data else 'N/A'}")
    print(f"temperatura_disponivel: {temperatura_disponivel} (tipo: {type(temperatura_disponivel)})")
    
    print(f"incluir_umidade: {incluir_umidade}")
    print(f"'RH2M' in parameter_data: {'RH2M' in parameter_data}")
    print(f"parameter_data['RH2M']: {bool(parameter_data['RH2M']) if 'RH2M' in parameter_data else 'N/A'}")
    print(f"umidade_disponivel: {umidade_disponivel} (tipo: {type(umidade_disponivel)})")
    
    print("\nTESTANDO COM DIFERENTES VALORES:")
    # Testar o que acontece quando fazemos a atribuição
    dados_temperatura = parameter_data.get('T2M', {}) if temperatura_disponivel else {}
    dados_umidade = parameter_data.get('RH2M', {}) if umidade_disponivel else {}
    
    print(f"dados_temperatura: tipo={type(dados_temperatura)}, len={len(dados_temperatura)}")
    print(f"dados_umidade: tipo={type(dados_umidade)}, len={len(dados_umidade)}")

if __name__ == "__main__":
    debug_disponibilidade()
