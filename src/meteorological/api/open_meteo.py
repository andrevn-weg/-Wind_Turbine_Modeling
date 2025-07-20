"""
Cliente Open-Meteo API

Este módulo implementa um cliente para a API Open-Meteo, que fornece dados meteorológicos
históricos e de previsão de forma gratuita e de código aberto.

LIMITAÇÕES DE ALTURA SUPORTADAS:
- 10m: Velocidade do vento a 10 metros de altura
- 80m: Velocidade do vento a 80 metros de altura  
- 120m: Velocidade do vento a 120 metros de altura
- 180m: Velocidade do vento a 180 metros de altura

APENAS estas alturas são suportadas pela API Open-Meteo.
Qualquer outra altura resultará em erro.

API Documentation: https://open-meteo.com/en/docs/historical-weather-api
"""

import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union
import json


class OpenMeteoClient:
    """
    Cliente para a API Open-Meteo para obtenção de dados meteorológicos históricos.
    
    A API Open-Meteo fornece dados meteorológicos históricos gratuitos,
    incluindo velocidade do vento em diferentes alturas.
    """
    
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
    ALTURAS_SUPORTADAS = [10, 80, 120, 180]  # metros
    
    def __init__(self, timeout: int = 30):
        """
        Inicializa o cliente Open-Meteo.
        
        Args:
            timeout: Timeout para requisições HTTP em segundos (padrão: 30)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Wind-Turbine-Modeling/1.0'
        })
    
    def validar_altura(self, altura: int) -> bool:
        """
        Valida se a altura solicitada é suportada pela API Open-Meteo.
        
        Args:
            altura: Altura em metros
            
        Returns:
            bool: True se a altura é suportada, False caso contrário
            
        Raises:
            ValueError: Se a altura não é suportada
        """
        if altura not in self.ALTURAS_SUPORTADAS:
            raise ValueError(
                f"Altura {altura}m não é suportada pela API Open-Meteo. "
                f"Alturas suportadas: {self.ALTURAS_SUPORTADAS}"
            )
        return True
    
    def obter_dados_historicos_vento(
        self,
        latitude: float,
        longitude: float,
        data_inicio: Union[str, date],
        data_fim: Union[str, date],
        alturas: Optional[List[int]] = None
    ) -> Dict:
        """
        Obtém dados históricos de velocidade do vento para uma localização específica.
        
        Args:
            latitude: Latitude da localização (-90 a 90)
            longitude: Longitude da localização (-180 a 180)
            data_inicio: Data de início (formato: YYYY-MM-DD ou objeto date)
            data_fim: Data de fim (formato: YYYY-MM-DD ou objeto date)
            alturas: Lista de alturas em metros. Se None, usa todas as alturas suportadas
            
        Returns:
            Dict: Dados meteorológicos organizados por altura
            
        Raises:
            ValueError: Se parâmetros inválidos
            requests.RequestException: Se erro na requisição HTTP
        """
        # Validar parâmetros
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} deve estar entre -90 e 90")
        
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} deve estar entre -180 e 180")
        
        # Converter datas para string se necessário
        if isinstance(data_inicio, date):
            data_inicio = data_inicio.strftime('%Y-%m-%d')
        if isinstance(data_fim, date):
            data_fim = data_fim.strftime('%Y-%m-%d')
        
        # Validar formato de data
        try:
            datetime.strptime(data_inicio, '%Y-%m-%d')
            datetime.strptime(data_fim, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Formato de data inválido. Use YYYY-MM-DD: {e}")
        
        # Usar todas as alturas suportadas se não especificado
        if alturas is None:
            alturas = self.ALTURAS_SUPORTADAS.copy()
        
        # Validar alturas
        for altura in alturas:
            self.validar_altura(altura)
        
        # Construir parâmetros da requisição
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': data_inicio,
            'end_date': data_fim,
            'hourly': self._construir_parametros_vento(alturas),
            'timezone': 'auto'
        }
        
        try:
            # Fazer requisição
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Processar resposta
            data = response.json()
            return self._processar_resposta(data, alturas)
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Erro na requisição Open-Meteo: {e}")
    
    def obter_dados_ano_completo(
        self,
        latitude: float,
        longitude: float,
        ano: int,
        alturas: Optional[List[int]] = None
    ) -> Dict:
        """
        Obtém dados históricos de vento para um ano completo.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            ano: Ano desejado (ex: 2024)
            alturas: Lista de alturas em metros
            
        Returns:
            Dict: Dados meteorológicos do ano completo
        """
        data_inicio = date(ano, 1, 1)
        data_fim = date(ano, 12, 31)
        
        return self.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=alturas
        )
    
    def obter_dados_ultimo_ano(
        self,
        latitude: float,
        longitude: float,
        alturas: Optional[List[int]] = None
    ) -> Dict:
        """
        Obtém dados históricos de vento do último ano (365 dias retroativos).
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            alturas: Lista de alturas em metros
            
        Returns:
            Dict: Dados meteorológicos do último ano
        """
        data_fim = date.today() - timedelta(days=1)  # Ontem
        data_inicio = data_fim - timedelta(days=364)  # 365 dias atrás
        
        return self.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=alturas
        )
    
    def _construir_parametros_vento(self, alturas: List[int]) -> str:
        """
        Constrói a string de parâmetros para velocidade do vento nas alturas especificadas.
        
        Args:
            alturas: Lista de alturas em metros
            
        Returns:
            str: Parâmetros separados por vírgula para a API
        """
        parametros = []
        for altura in alturas:
            parametros.append(f"wind_speed_{altura}m")
        
        return ','.join(parametros)
    
    def _processar_resposta(self, data: Dict, alturas: List[int]) -> Dict:
        """
        Processa a resposta da API organizando os dados por altura.
        
        Args:
            data: Dados brutos da API
            alturas: Lista de alturas solicitadas
            
        Returns:
            Dict: Dados organizados por altura e processados
        """
        if 'hourly' not in data:
            raise ValueError("Resposta da API não contém dados horários")
        
        hourly_data = data['hourly']
        timestamps = hourly_data.get('time', [])
        
        # Organizar dados por altura
        resultado = {
            'metadata': {
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone'),
                'utc_offset_seconds': data.get('utc_offset_seconds'),
                'periodo_inicio': timestamps[0] if timestamps else None,
                'periodo_fim': timestamps[-1] if timestamps else None,
                'total_registros': len(timestamps),
                'fonte': 'Open-Meteo'
            },
            'dados_por_altura': {}
        }
        
        for altura in alturas:
            parametro = f"wind_speed_{altura}m"
            velocidades = hourly_data.get(parametro, [])
            
            # Calcular estatísticas básicas
            velocidades_validas = [v for v in velocidades if v is not None]
            
            if velocidades_validas:
                estatisticas = {
                    'velocidade_media': sum(velocidades_validas) / len(velocidades_validas),
                    'velocidade_maxima': max(velocidades_validas),
                    'velocidade_minima': min(velocidades_validas),
                    'total_registros': len(velocidades_validas),
                    'registros_nulos': len(velocidades) - len(velocidades_validas)
                }
            else:
                estatisticas = {
                    'velocidade_media': 0,
                    'velocidade_maxima': 0,
                    'velocidade_minima': 0,
                    'total_registros': 0,
                    'registros_nulos': len(velocidades)
                }
            
            resultado['dados_por_altura'][f"{altura}m"] = {
                'altura_metros': altura,
                'timestamps': timestamps,
                'velocidades_vento': velocidades,
                'estatisticas': estatisticas
            }
        
        return resultado
    
    def obter_informacoes_api(self) -> Dict:
        """
        Retorna informações sobre as capacidades e limitações da API Open-Meteo.
        
        Returns:
            Dict: Informações da API
        """
        return {
            'nome': 'Open-Meteo Historical Weather API',
            'url_base': self.BASE_URL,
            'alturas_suportadas': self.ALTURAS_SUPORTADAS,
            'unidade_velocidade': 'm/s',
            'frequencia_dados': 'Horária',
            'periodo_historico': 'A partir de 1940',
            'gratuita': True,
            'limite_requisicoes': 'Sem limite oficial, mas recomenda-se uso responsável',
            'documentacao': 'https://open-meteo.com/en/docs/historical-weather-api'
        }
    
    def __str__(self) -> str:
        """Representação em string do cliente."""
        return f"OpenMeteoClient(alturas_suportadas={self.ALTURAS_SUPORTADAS})"
    
    def __repr__(self) -> str:
        """Representação técnica do cliente."""
        return f"OpenMeteoClient(timeout={self.timeout}, base_url='{self.BASE_URL}')"
