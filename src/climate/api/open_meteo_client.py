"""
Cliente para API Open-Meteo.

Este módulo contém o cliente para obter dados meteorológicos
da API Open-Meteo, incluindo dados históricos e atuais.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import time

from ..models.entity import DadosEolicos, LocalizacaoClimatica


class OpenMeteoClient:
    """
    Cliente para API Open-Meteo.
    
    Fornece métodos para obter dados meteorológicos históricos
    e atuais da API Open-Meteo.
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Inicializa o cliente.
        
        Args:
            timeout: Timeout para requisições em segundos
            max_retries: Número máximo de tentativas em caso de erro
        """
        self.base_url_historical = "https://archive-api.open-meteo.com/v1/archive"
        self.base_url_forecast = "https://api.open-meteo.com/v1/forecast"
        self.timeout = timeout
        self.max_retries = max_retries
    
    def obter_dados_historicos(self, latitude: float, longitude: float,
                             inicio: datetime, fim: datetime,
                             altura_vento: int = 10,
                             nome_cidade: str = "") -> List[DadosEolicos]:
        """
        Obtém dados meteorológicos históricos.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            inicio: Data de início
            fim: Data de fim
            altura_vento: Altura de medição do vento (10, 80, 120, 180m)
            nome_cidade: Nome da cidade para identificação
        
        Returns:
            Lista de dados eólicos históricos
        
        Raises:
            APIError: Erro na comunicação com a API
            ValueError: Parâmetros inválidos
        """
        # Validação de parâmetros
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude deve estar entre -90 e 90 graus")
        
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude deve estar entre -180 e 180 graus")
        
        if altura_vento not in [10, 80, 120, 180]:
            altura_vento = 10  # Valor padrão
        
        if inicio >= fim:
            raise ValueError("Data de início deve ser anterior à data de fim")
        
        # Preparação dos parâmetros
        start_date = inicio.strftime('%Y-%m-%d')
        end_date = fim.strftime('%Y-%m-%d')
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min", 
                "temperature_2m_mean",
                "relative_humidity_2m_mean",
                f"windspeed_{altura_vento}m_max",
                f"windspeed_{altura_vento}m_mean",
                f"winddirection_{altura_vento}m_dominant"
            ],
            "windspeed_unit": "ms",
            "timezone": "America/Sao_Paulo"
        }
        
        # Requisição à API
        data = self._fazer_requisicao(self.base_url_historical, params)
        
        # Processamento dos dados
        return self._processar_dados_historicos(
            data, latitude, longitude, altura_vento, nome_cidade
        )
    
    def obter_dados_atuais(self, latitude: float, longitude: float,
                          altura_vento: int = 10,
                          nome_cidade: str = "") -> Optional[DadosEolicos]:
        """
        Obtém dados meteorológicos atuais.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            altura_vento: Altura de medição do vento
            nome_cidade: Nome da cidade para identificação
        
        Returns:
            Dados eólicos atuais ou None
        """
        # Obtém dados para hoje
        hoje = datetime.now()
        dados_historicos = self.obter_dados_historicos(
            latitude, longitude, hoje, hoje, altura_vento, nome_cidade
        )
        
        return dados_historicos[0] if dados_historicos else None
    
    def obter_previsao(self, latitude: float, longitude: float,
                      dias: int = 7, altura_vento: int = 10,
                      nome_cidade: str = "") -> List[DadosEolicos]:
        """
        Obtém previsão meteorológica.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            dias: Número de dias de previsão (1-16)
            altura_vento: Altura de medição do vento
            nome_cidade: Nome da cidade para identificação
        
        Returns:
            Lista de dados eólicos previstos
        """
        if not (1 <= dias <= 16):
            raise ValueError("Número de dias deve estar entre 1 e 16")
        
        if altura_vento not in [10, 80, 120, 180]:
            altura_vento = 10
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "relative_humidity_2m_mean",
                f"windspeed_{altura_vento}m_max",
                f"windspeed_{altura_vento}m_mean",
                f"winddirection_{altura_vento}m_dominant"
            ],
            "windspeed_unit": "ms",
            "timezone": "America/Sao_Paulo",
            "forecast_days": dias
        }
        
        data = self._fazer_requisicao(self.base_url_forecast, params)
        
        return self._processar_dados_historicos(
            data, latitude, longitude, altura_vento, nome_cidade
        )
    
    def obter_ano_completo(self, latitude: float, longitude: float,
                          ano: int, altura_vento: int = 10,
                          nome_cidade: str = "") -> List[DadosEolicos]:
        """
        Obtém dados de um ano completo.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            ano: Ano desejado
            altura_vento: Altura de medição do vento
            nome_cidade: Nome da cidade para identificação
        
        Returns:
            Lista de dados eólicos do ano
        """
        inicio = datetime(ano, 1, 1)
        fim = datetime(ano, 12, 31)
        
        return self.obter_dados_historicos(
            latitude, longitude, inicio, fim, altura_vento, nome_cidade
        )
    
    def obter_ultimo_ano(self, latitude: float, longitude: float,
                        altura_vento: int = 10,
                        nome_cidade: str = "") -> List[DadosEolicos]:
        """
        Obtém dados do último ano.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            altura_vento: Altura de medição do vento
            nome_cidade: Nome da cidade para identificação
        
        Returns:
            Lista de dados eólicos do último ano
        """
        hoje = datetime.now()
        um_ano_atras = hoje - timedelta(days=365)
        
        return self.obter_dados_historicos(
            latitude, longitude, um_ano_atras, hoje, altura_vento, nome_cidade
        )
    
    def verificar_disponibilidade(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Verifica a disponibilidade de dados para uma localização.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
        
        Returns:
            Informações sobre disponibilidade
        """
        # Tenta obter dados dos últimos 7 dias
        hoje = datetime.now()
        uma_semana_atras = hoje - timedelta(days=7)
        
        try:
            dados = self.obter_dados_historicos(
                latitude, longitude, uma_semana_atras, hoje
            )
            
            return {
                "disponivel": True,
                "dados_recentes": len(dados),
                "ultima_atualizacao": dados[-1].data if dados else None,
                "qualidade": "boa" if len(dados) >= 6 else "limitada"
            }
        
        except Exception as e:
            return {
                "disponivel": False,
                "erro": str(e),
                "dados_recentes": 0,
                "qualidade": "indisponivel"
            }
    
    def _fazer_requisicao(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição HTTP com retry automático.
        
        Args:
            url: URL da API
            params: Parâmetros da requisição
        
        Returns:
            Resposta da API em formato JSON
        
        Raises:
            APIError: Erro na comunicação com a API
        """
        last_exception = None
        
        for tentativa in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                # Verifica se há erro na resposta
                if "error" in data:
                    raise APIError(f"Erro da API: {data['error']}")
                
                return data
            
            except requests.exceptions.RequestException as e:
                last_exception = e
                if tentativa < self.max_retries - 1:
                    # Aguarda antes de tentar novamente
                    time.sleep(2 ** tentativa)  # Backoff exponencial
                continue
        
        # Se chegou aqui, todas as tentativas falharam
        raise APIError(f"Falha após {self.max_retries} tentativas: {last_exception}")
    
    def _processar_dados_historicos(self, data: Dict[str, Any],
                                  latitude: float, longitude: float,
                                  altura_vento: int,
                                  nome_cidade: str) -> List[DadosEolicos]:
        """
        Processa dados históricos da API.
        
        Args:
            data: Resposta da API
            latitude: Latitude da localização
            longitude: Longitude da localização
            altura_vento: Altura de medição
            nome_cidade: Nome da cidade
        
        Returns:
            Lista de dados eólicos processados
        """
        if "daily" not in data:
            raise APIError("Formato de resposta da API inválido")
        
        daily_data = data["daily"]
        dados_eolicos = []
        
        # Mapeia os nomes dos campos baseado na altura
        campo_vento_medio = f"windspeed_{altura_vento}m_mean"
        campo_vento_max = f"windspeed_{altura_vento}m_max"
        campo_direcao = f"winddirection_{altura_vento}m_dominant"
        
        for i, date_str in enumerate(daily_data.get("time", [])):
            try:
                # Extrai dados com tratamento de valores nulos
                temperatura = self._obter_valor_seguro(daily_data.get("temperature_2m_mean"), i)
                umidade = self._obter_valor_seguro(daily_data.get("relative_humidity_2m_mean"), i)
                velocidade_vento = self._obter_valor_seguro(daily_data.get(campo_vento_medio), i)
                velocidade_vento_max = self._obter_valor_seguro(daily_data.get(campo_vento_max), i)
                direcao_vento = self._obter_valor_seguro(daily_data.get(campo_direcao), i)
                
                # Pula se dados essenciais estão ausentes
                if temperatura is None or umidade is None or velocidade_vento is None:
                    continue
                
                dados_eolico = DadosEolicos(
                    cidade=nome_cidade,
                    latitude=latitude,
                    longitude=longitude,
                    temperatura=temperatura,
                    umidade=umidade,
                    velocidade_vento=velocidade_vento,
                    direcao_vento=direcao_vento,
                    velocidade_vento_max=velocidade_vento_max,
                    data=datetime.strptime(date_str, '%Y-%m-%d'),
                    altura_medicao=altura_vento
                )
                
                dados_eolicos.append(dados_eolico)
            
            except (ValueError, TypeError) as e:
                # Log do erro e continua com próximo registro
                print(f"Erro ao processar dados do dia {date_str}: {e}")
                continue
        
        return dados_eolicos
    
    def _obter_valor_seguro(self, lista: Optional[List], indice: int) -> Optional[float]:
        """
        Obtém valor de uma lista de forma segura.
        
        Args:
            lista: Lista de valores
            indice: Índice do valor
        
        Returns:
            Valor convertido para float ou None
        """
        if not lista or indice >= len(lista):
            return None
        
        valor = lista[indice]
        if valor is None:
            return None
        
        try:
            return float(valor)
        except (ValueError, TypeError):
            return None


class APIError(Exception):
    """Exceção para erros da API Open-Meteo."""
    pass


# Instância global do cliente para facilitar uso
client = OpenMeteoClient()


def obter_dados_historicos_simples(latitude: float, longitude: float,
                                 dias: int = 365,
                                 nome_cidade: str = "") -> List[DadosEolicos]:
    """
    Função de conveniência para obter dados históricos.
    
    Args:
        latitude: Latitude da localização
        longitude: Longitude da localização
        dias: Número de dias anteriores a buscar
        nome_cidade: Nome da cidade
    
    Returns:
        Lista de dados eólicos históricos
    """
    hoje = datetime.now()
    inicio = hoje - timedelta(days=dias)
    
    return client.obter_dados_historicos(
        latitude, longitude, inicio, hoje, 10, nome_cidade
    )
