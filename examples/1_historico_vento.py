"""
Exemplo de como obter dados históricos de vento para uma localização específica.
Coordenadas: -26.4986085, -49.1928379 (Região de Jaraguá do Sul)

Este script utiliza a API Open-Meteo para obter dados históricos de vento do último ano.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys

# Adicionar o diretório raiz ao path para poder importar módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dados da localização -26.5165263,-49.0559004
# LATITUDE = -26.4986085
# LONGITUDE = -49.1928379
# CIDADE = "Jaraguá do Sul"
LATITUDE = -26.5165263
LONGITUDE = -49.0559004
CIDADE = "Jaraguá do Sul - Morro das Antenas"

class DadosClimaticos:
    def __init__(self, cidade, latitude, longitude, temperatura, umidade, velocidade_vento, altura_vento, data=None):
        self.cidade = cidade
        self.latitude = latitude
        self.longitude = longitude
        self.temperatura = temperatura
        self.umidade = umidade
        self.velocidade_vento = velocidade_vento
        self.altura_vento = altura_vento
        self.data = data

    def __repr__(self):
        return f"DadosClimaticos(cidade={self.cidade}, latitude={self.latitude}, longitude={self.longitude}, temperatura={self.temperatura}, umidade={self.umidade}, velocidade_vento={self.velocidade_vento}, altura_vento={self.altura_vento}, data={self.data})"

def obter_dados_eolicos_historicos(latitude, longitude, start_date, end_date, altura_vento=10):
    """
    Obtém dados eólicos históricos usando a API Open-Meteo.
    
    Parâmetros:
    latitude (float): Latitude do local
    longitude (float): Longitude do local
    start_date (str): Data inicial no formato 'YYYY-MM-DD'
    end_date (str): Data final no formato 'YYYY-MM-DD'
    altura_vento (int): Altura em metros para medição do vento (padrão: 10m)
    
    Retorna:
    Lista de objetos DadosClimaticos
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", 
                  "relative_humidity_2m_mean", "windspeed_10m_max", "windspeed_10m_mean", 
                  "winddirection_10m_dominant"],
        "windspeed_unit": "ms",
        "timezone": "America/Sao_Paulo"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Verifica se houve erro na requisição
        data = response.json()
        
        # Lista para armazenar os dados climáticos
        dados_climaticos_list = []
        
        # Processa os dados
        for i, date_str in enumerate(data["daily"]["time"]):
            temperatura_media = data["daily"]["temperature_2m_mean"][i]
            umidade_media = data["daily"]["relative_humidity_2m_mean"][i]
            velocidade_vento_media = data["daily"]["windspeed_10m_mean"][i]
            
            # Cria um objeto DadosClimaticos
            dados = DadosClimaticos(
                cidade=CIDADE,
                latitude=latitude,
                longitude=longitude,
                temperatura=temperatura_media,
                umidade=umidade_media,
                velocidade_vento=velocidade_vento_media,
                altura_vento=altura_vento,
                data=datetime.strptime(date_str, '%Y-%m-%d')
            )
            
            dados_climaticos_list.append(dados)
        
        return dados_climaticos_list, data["daily"]["time"]
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados da API: {e}")
        return [], []

def salvar_dados_json_formato_lista(dados_list, datas, nome_arquivo):
    """
    Salva os dados climáticos em um arquivo JSON com formato de listas.
    
    Parâmetros:
    dados_list (list): Lista de objetos DadosClimaticos
    datas (list): Lista com as datas correspondentes
    nome_arquivo (str): Nome do arquivo para salvar os dados
    """
    # Extrai as informações fixas da primeira entrada válida para economizar espaço
    cidade = None
    latitude = None
    longitude = None
    altura_vento = None
    
    # Cria listas para armazenar os valores
    temperaturas = []
    umidades = []
    velocidades_vento = []
    
    # Preenche as listas com os valores
    for dado in dados_list:
        if cidade is None and dado.cidade:
            cidade = dado.cidade
            latitude = dado.latitude
            longitude = dado.longitude
            altura_vento = dado.altura_vento
            
        temperaturas.append(dado.temperatura)
        umidades.append(dado.umidade)
        velocidades_vento.append(dado.velocidade_vento)
    
    # Monta o dicionário no formato solicitado
    dados_json = {
        "metadados": {
            "cidade": cidade,
            "latitude": latitude,
            "longitude": longitude,
            "altura_vento": altura_vento
        },
        "dados": {
            "datas": datas,
            "temperatura": temperaturas,
            "umidade": umidades,
            "velocidade_vento": velocidades_vento
        }
    }
    
    # Cria o diretório database se não existir
    database_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(database_dir, exist_ok=True)
    
    # Salva os dados em um arquivo JSON
    arquivo_path = os.path.join(database_dir, nome_arquivo)
    with open(arquivo_path, 'w') as f:
        json.dump(dados_json, f, indent=4)
    
    print(f"Dados salvos em formato de listas em {arquivo_path}")
    return arquivo_path

def main():
    # Calcula as datas para o último ano
    hoje = datetime.now()
    um_ano_atras = hoje - timedelta(days=365)
    
    start_date = um_ano_atras.strftime('%Y-%m-%d')
    end_date = hoje.strftime('%Y-%m-%d')
    
    print(f"Obtendo dados históricos de vento para {CIDADE} ({LATITUDE}, {LONGITUDE})")
    print(f"Período: de {start_date} até {end_date}")
    
    # Obtém os dados
    dados_historicos, datas = obter_dados_eolicos_historicos(
        latitude=LATITUDE, 
        longitude=LONGITUDE, 
        start_date=start_date, 
        end_date=end_date
    )
    
    if dados_historicos:
        print(f"Foram obtidos dados para {len(dados_historicos)} dias")
        
        # Mostra alguns exemplos
        print("\nExemplos de dados obtidos:")
        for i, dado in enumerate(dados_historicos[:5]):
            print(f"Dia {i+1}: {dado}")
        
        # Salva os dados em um arquivo JSON com formato de listas
        nome_arquivo = f"{CIDADE.lower().replace(' ', '_')}_{LATITUDE}_{LONGITUDE}_listas.json"
        arquivo_path = salvar_dados_json_formato_lista(dados_historicos, datas, nome_arquivo)
        
        # Mostra estatísticas
        velocidades = [dado.velocidade_vento for dado in dados_historicos if dado.velocidade_vento is not None]
        if velocidades:
            media_velocidade = sum(velocidades) / len(velocidades)
            max_velocidade = max(velocidades)
            min_velocidade = min(velocidades)
            
            print("\nEstatísticas de velocidade do vento:")
            print(f"Média: {media_velocidade:.2f} m/s")
            print(f"Máxima: {max_velocidade:.2f} m/s")
            print(f"Mínima: {min_velocidade:.2f} m/s")
        else:
            print("Não há dados de velocidade do vento disponíveis.")
    else:
        print("Não foi possível obter dados históricos de vento.")

if __name__ == "__main__":
    main()