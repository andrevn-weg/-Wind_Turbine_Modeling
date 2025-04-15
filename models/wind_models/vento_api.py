import os
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from models.vento import Vento

class VentoAPI(Vento):
    """
    Classe para obter dados e informações de recursos eólicos de diferentes fontes,
    incluindo APIs meteorológicas e serviços de geolocalização.
    Herda as funcionalidades básicas da classe Vento.
    """
    
    def __init__(self, local=None, altura=50, periodo=168, vento_medio=None, topologia_terreno="Gramado", 
                 latitude=None, longitude=None):
        # Inicializa a classe pai
        super().__init__(local, altura, periodo, vento_medio, topologia_terreno)
        
        # Novos atributos específicos de VentoAPI
        self.latitude = latitude
        self.longitude = longitude
        self.fonte_dados = None
        self.ultima_atualizacao = None
        self.database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database')
        
        # Garantir que o diretório database exista
        if not os.path.exists(self.database_dir):
            os.makedirs(self.database_dir)
    
    def obter_coordenadas_por_nome(self, nome_local):
        """
        Obtém as coordenadas de latitude e longitude de um local pelo nome usando a API Nominatim (OpenStreetMap).
        
        Args:
            nome_local (str): Nome do local (cidade, estado, país, etc.)
            
        Returns:
            tuple or None: (latitude, longitude) se encontrado, ou None se não encontrado
        """
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={nome_local}&format=json&limit=1"
            headers = {'User-Agent': 'WindTurbineModeling/1.0'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latitude = float(data[0]['lat'])
                    longitude = float(data[0]['lon'])
                    self.latitude = latitude
                    self.longitude = longitude
                    self.local = data[0].get('display_name', nome_local)
                    return latitude, longitude
            
            print(f"Não foi possível encontrar coordenadas para '{nome_local}'")
            return None
        except Exception as e:
            print(f"Erro ao obter coordenadas: {e}")
            return None
    
    def obter_dados_vento_reais(self, start_date=None, end_date=None, periodo_dias=30):
        """
        Obtém dados reais de vento para uma localização específica usando APIs meteorológicas.
        Tenta usar a biblioteca Meteostat se disponível, ou outros serviços meteorológicos.
        
        Args:
            start_date (datetime, optional): Data inicial para coleta de dados
            end_date (datetime, optional): Data final para coleta de dados
            periodo_dias (int, optional): Número de dias para coleta se as datas não forem especificadas
            
        Returns:
            DataFrame or None: DataFrame com os dados de vento ou None se não for possível obter os dados
        """
        # Verifica se temos coordenadas
        if not self.latitude or not self.longitude:
            print("Coordenadas não definidas. Use 'obter_coordenadas_por_nome' primeiro.")
            return None
        
        # Tenta importar a biblioteca Meteostat
        try:
            from meteostat import Point, Hourly
            
            # Se as datas não forem fornecidas, use o período de dias a partir de hoje
            if start_date is None:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=periodo_dias)
                
            # Criar um objeto Point com a localização
            location = Point(self.latitude, self.longitude)
            
            # Buscar dados horários
            data = Hourly(location, start_date, end_date)
            data = data.fetch()
            
            if data.empty:
                print(f"Não foram encontrados dados para a localização ({self.latitude}, {self.longitude}) no período especificado.")
                return None
                
            # Converter para o formato apropriado para o modelo
            serie_temporal = pd.DataFrame({
                'timestamp': data.index,
                'velocidade_vento': data['wdsp'].values if 'wdsp' in data.columns else data['wspd'].values
            })
            
            # Preencher valores faltantes, se houver
            serie_temporal['velocidade_vento'].fillna(method='ffill', inplace=True)
            
            # Calcular o potencial eólico
            rho = 1.225  # kg/m³ (densidade do ar)
            serie_temporal['potencial_eolico'] = 0.5 * rho * serie_temporal['velocidade_vento']**3
            
            # Atualizar a velocidade média do vento
            self.vento_medio = serie_temporal['velocidade_vento'].mean()
            self.fonte_dados = "Meteostat"
            self.ultima_atualizacao = datetime.now()
            
            return serie_temporal
        
        except ImportError:
            print("Biblioteca Meteostat não encontrada. Tentando API alternativa...")
        
        # Alternativa: OpenWeatherMap ou outra API
        try:
            # Aqui você pode implementar chamadas para outras APIs como OpenWeatherMap, Visual Crossing, etc.
            print("Outras APIs não implementadas ainda. Por favor instale a biblioteca Meteostat com 'pip install meteostat'")
            return None
        
        except Exception as e:
            print(f"Erro ao obter dados de vento: {e}")
            return None
    
    def salvar_localidade(self):
        """
        Salva os dados da localidade atual em um arquivo JSON no diretório database.
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        if not self.local:
            print("Local não definido. Impossível salvar.")
            return False
            
        try:
            # Prepara um nome de arquivo baseado no nome do local
            if self.latitude and self.longitude:
                filename = f"{self.local.split(',')[0].strip().replace(' ', '_').lower()}_{self.latitude:.2f}_{self.longitude:.2f}.json"
            else:
                filename = f"{self.local.replace(' ', '_').lower()}.json"
                
            filepath = os.path.join(self.database_dir, filename)
            
            # Prepara os dados para salvar
            dados = {
                "nome": self.local,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "velocidade_media": self.vento_medio,
                "altura_referencia": self.altura,
                "topologia_terreno": next((k for k, v in self.topologia.items() if v == self.topologia_terreno), None),
                "fonte_dados": self.fonte_dados,
                "ultima_atualizacao": self.ultima_atualizacao.isoformat() if self.ultima_atualizacao else None,
                "data_cadastro": datetime.now().isoformat()
            }
            
            # Salva os dados no arquivo JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
                
            print(f"Localidade '{self.local}' salva com sucesso em {filepath}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar localidade: {e}")
            return False
    
    @classmethod
    def carregar_localidade(cls, nome_arquivo):
        """
        Carrega uma localidade a partir de um arquivo JSON salvo.
        
        Args:
            nome_arquivo (str): Nome do arquivo JSON (sem caminho)
            
        Returns:
            VentoAPI: Uma nova instância de VentoAPI com os dados carregados
        """
        database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database')
        filepath = os.path.join(database_dir, nome_arquivo)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            # Cria uma nova instância com os dados carregados
            instancia = cls(
                local=dados.get("nome"),
                altura=dados.get("altura_referencia", 50),
                vento_medio=dados.get("velocidade_media"),
                topologia_terreno=dados.get("topologia_terreno", "Gramado"),
                latitude=dados.get("latitude"),
                longitude=dados.get("longitude")
            )
            
            # Complementa com outros dados
            instancia.fonte_dados = dados.get("fonte_dados")
            if dados.get("ultima_atualizacao"):
                instancia.ultima_atualizacao = datetime.fromisoformat(dados.get("ultima_atualizacao"))
                
            return instancia
            
        except Exception as e:
            print(f"Erro ao carregar localidade: {e}")
            return None
    
    @classmethod
    def listar_localidades(cls):
        """
        Lista todas as localidades salvas no diretório database.
        
        Returns:
            list: Lista de dicionários com informações resumidas das localidades
        """
        database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database')
        
        if not os.path.exists(database_dir):
            print(f"Diretório {database_dir} não existe.")
            return []
            
        try:
            localidades = []
            
            for filename in os.listdir(database_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(database_dir, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        
                    localidades.append({
                        "nome": dados.get("nome"),
                        "latitude": dados.get("latitude"),
                        "longitude": dados.get("longitude"),
                        "velocidade_media": dados.get("velocidade_media"),
                        "arquivo": filename
                    })
                    
            return localidades
            
        except Exception as e:
            print(f"Erro ao listar localidades: {e}")
            return []