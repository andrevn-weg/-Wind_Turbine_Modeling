"""
Teste simples para verificar se o metadata foi corrigido
"""

import sys
import os
from datetime import date

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.nasa_power import NASAPowerClient

def testar_metadata():
    client = NASAPowerClient()
    
    resultado = client.obter_dados_historicos_vento(
        latitude=-29.6842,
        longitude=-53.8069,
        data_inicio=date(2024, 1, 1),
        data_fim=date(2024, 1, 2),
        alturas=[10, 50],
        incluir_temperatura=True,
        incluir_umidade=True
    )
    
    print("METADATA:")
    dados_incluidos = resultado['metadata']['dados_incluidos']
    print(f"  Velocidade vento: {dados_incluidos['velocidade_vento']} (tipo: {type(dados_incluidos['velocidade_vento'])})")
    print(f"  Temperatura: {dados_incluidos['temperatura']} (tipo: {type(dados_incluidos['temperatura'])})")
    print(f"  Umidade: {dados_incluidos['umidade']} (tipo: {type(dados_incluidos['umidade'])})")
    
    print(f"\nTotal de registros: {len(resultado['dados'])}")
    print(f"Alturas disponíveis: {list(resultado['dados_por_altura'].keys())}")

if __name__ == "__main__":
    testar_metadata()
