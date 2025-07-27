"""
Cliente Open-Meteo API Otimizado

Este módulo implementa um cliente otimizado para a API Open-Meteo baseado no exemplo oficial,
com melhor performance, cache e retry automático.

LIMITAÇÕES DE ALTURA SUPORTADAS:
- 10m: Velocidade do vento a 10 metros de altura
- 80m: Velocidade do vento a 80 metros de altura  
- 120m: Velocidade do vento a 120 metros de altura
- 180m: Velocidade do vento a 180 metros de altura

API Documentation: https://open-meteo.com/en/docs/historical-weather-api
"""

import requests
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union
import json
import os

# Imports opcionais para funcionalidades avançadas
try:
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry
    CLIENTE_OTIMIZADO_DISPONIVEL = True
except ImportError:
    CLIENTE_OTIMIZADO_DISPONIVEL = False


class OpenMeteoClient:
    """
    Cliente otimizado para a API Open-Meteo.
    
    Usa o client oficial quando disponível, senão fallback para requests básico.
    """
    
    # URLs corretas baseadas no exemplo oficial
    BASE_URL_HISTORICAL = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    BASE_URL_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
    
    ALTURAS_SUPORTADAS = [10, 80, 120, 180]  # metros
    
    def __init__(self, timeout: int = 30, use_cache: bool = True):
        """
        Inicializa o cliente Open-Meteo.
        
        Args:
            timeout: Timeout para requisições HTTP em segundos (padrão: 30)
            use_cache: Se deve usar cache (apenas com cliente otimizado)
        """
        self.timeout = timeout
        self.use_cache = use_cache
        
        if CLIENTE_OTIMIZADO_DISPONIVEL and use_cache:
            # Configurar cliente otimizado com cache e retry
            self._setup_optimized_client()
            self.client_type = "optimized"
        else:
            # Fallback para requests básico
            self._setup_basic_client()
            self.client_type = "basic"
    
    def _setup_optimized_client(self):
        """Configura o cliente otimizado com cache e retry."""
        try:
            # Criar diretório de cache se não existir
            cache_dir = os.path.join(os.getcwd(), '.cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            # Setup com cache e retry
            cache_session = requests_cache.CachedSession(
                os.path.join(cache_dir, 'openmeteo_cache'), 
                expire_after=3600  # 1 hora
            )
            retry_session = retry(
                cache_session, 
                retries=5, 
                backoff_factor=0.2
            )
            self.openmeteo_client = openmeteo_requests.Client(session=retry_session)
        except Exception:
            # Se falhar, usar cliente básico
            self._setup_basic_client()
            self.client_type = "basic"
    
    def _setup_basic_client(self):
        """Configura o cliente básico usando requests."""
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
        alturas: Optional[List[int]] = None,
        incluir_temperatura: bool = True,
        incluir_umidade: bool = True
    ) -> Dict:
        """
        Obtém dados históricos de velocidade do vento, temperatura e umidade para uma localização específica.
        
        Args:
            latitude: Latitude da localização (-90 a 90)
            longitude: Longitude da localização (-180 a 180)
            data_inicio: Data de início (formato: YYYY-MM-DD ou objeto date)
            data_fim: Data de fim (formato: YYYY-MM-DD ou objeto date)
            alturas: Lista de alturas em metros. Se None, usa todas as alturas suportadas
            incluir_temperatura: Se deve incluir dados de temperatura a 2m (padrão: True)
            incluir_umidade: Se deve incluir dados de umidade relativa a 2m (padrão: True)
            
        Returns:
            Dict: Dados meteorológicos organizados por altura, incluindo temperatura e umidade
            
        Note:
            - Velocidade do vento: obtida nas alturas especificadas (10m, 80m, 120m, 180m)
            - Temperatura: sempre obtida a 2 metros de altura
            - Umidade relativa: sempre obtida a 2 metros de altura
        """
        # Validar parâmetros
        self._validar_parametros(latitude, longitude, data_inicio, data_fim)
        
        # Usar todas as alturas suportadas se não especificado
        if alturas is None:
            alturas = self.ALTURAS_SUPORTADAS.copy()
        
        # Validar alturas
        for altura in alturas:
            self.validar_altura(altura)
        
        # Usar cliente otimizado ou básico
        if self.client_type == "optimized":
            return self._obter_dados_otimizado(latitude, longitude, data_inicio, data_fim, alturas, incluir_temperatura, incluir_umidade)
        else:
            return self._obter_dados_basico(latitude, longitude, data_inicio, data_fim, alturas, incluir_temperatura, incluir_umidade)
    
    def _obter_dados_otimizado(self, latitude: float, longitude: float, 
                              data_inicio: Union[str, date], data_fim: Union[str, date], 
                              alturas: List[int], incluir_temperatura: bool = True, 
                              incluir_umidade: bool = True) -> Dict:
        """Obtém dados usando o cliente otimizado com temperatura e umidade (baseado no exemplo oficial)."""
        
        # Converter datas para string se necessário
        if isinstance(data_inicio, date):
            data_inicio = data_inicio.strftime('%Y-%m-%d')
        if isinstance(data_fim, date):
            data_fim = data_fim.strftime('%Y-%m-%d')
        
        # Construir lista de parâmetros horários
        parametros_horarios = [f"wind_speed_{altura}m" for altura in alturas]
        
        # Adicionar temperatura e umidade se solicitados
        if incluir_temperatura:
            parametros_horarios.append("temperature_2m")
        if incluir_umidade:
            parametros_horarios.append("relative_humidity_2m")
        
        # Construir parâmetros como no exemplo oficial
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": data_inicio,
            "end_date": data_fim,
            "hourly": parametros_horarios,
            "timezone": "auto",
            "wind_speed_unit": "ms"
        }
        
        try:
            # Fazer requisição usando cliente otimizado
            responses = self.openmeteo_client.weather_api(self.BASE_URL_HISTORICAL, params=params)
            
            if not responses:
                raise ValueError("Nenhuma resposta da API")
            
            # Processar primeira (e única) localização
            response = responses[0]
            
            # Extrair dados horários como no exemplo oficial
            hourly = response.Hourly()
            
            # Criar range de datas usando pandas (muito mais eficiente)
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )
            }
            
            # Extrair dados de velocidade do vento para cada altura
            variable_index = 0
            for i, altura in enumerate(alturas):
                wind_data = hourly.Variables(variable_index).ValuesAsNumpy()
                hourly_data[f"wind_speed_{altura}m"] = wind_data
                variable_index += 1
            
            # Extrair temperatura se solicitada
            if incluir_temperatura:
                try:
                    temperature_data = hourly.Variables(variable_index).ValuesAsNumpy()
                    hourly_data["temperature_2m"] = temperature_data
                    variable_index += 1
                except Exception as e:
                    # Se falhar, usar valores None
                    hourly_data["temperature_2m"] = [None] * len(hourly_data["date"])
            
            # Extrair umidade se solicitada
            if incluir_umidade:
                try:
                    humidity_data = hourly.Variables(variable_index).ValuesAsNumpy()
                    hourly_data["relative_humidity_2m"] = humidity_data
                    variable_index += 1
                except Exception as e:
                    # Se falhar, usar valores None
                    hourly_data["relative_humidity_2m"] = [None] * len(hourly_data["date"])
            
            # Criar DataFrame
            df = pd.DataFrame(data=hourly_data)
            
            # Converter para formato esperado pelo sistema
            return self._converter_dataframe_para_formato_sistema(df, alturas, response, incluir_temperatura, incluir_umidade)
            
        except Exception as e:
            raise Exception(f"Erro no cliente otimizado Open-Meteo: {e}")
    
    def _obter_dados_basico(self, latitude: float, longitude: float, 
                           data_inicio: Union[str, date], data_fim: Union[str, date], 
                           alturas: List[int], incluir_temperatura: bool = True, 
                           incluir_umidade: bool = True) -> Dict:
        """Obtém dados usando requests básico com temperatura e umidade (código melhorado)."""
        
        # Converter datas para string se necessário
        if isinstance(data_inicio, date):
            data_inicio = data_inicio.strftime('%Y-%m-%d')
        if isinstance(data_fim, date):
            data_fim = data_fim.strftime('%Y-%m-%d')
        
        # Construir lista de parâmetros horários
        parametros_horarios = [f"wind_speed_{altura}m" for altura in alturas]
        
        # Adicionar temperatura e umidade se solicitados
        if incluir_temperatura:
            parametros_horarios.append("temperature_2m")
        if incluir_umidade:
            parametros_horarios.append("relative_humidity_2m")
        
        # Construir parâmetros da requisição
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': data_inicio,
            'end_date': data_fim,
            'hourly': ','.join(parametros_horarios),
            'timezone': 'auto',
            'wind_speed_unit': 'ms'
        }
        
        try:
            # Fazer requisição
            response = self.session.get(
                self.BASE_URL_ARCHIVE,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Processar resposta
            data = response.json()
            return self._processar_resposta_basica(data, alturas, incluir_temperatura, incluir_umidade)
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Erro na requisição Open-Meteo: {e}")
    
    def _converter_dataframe_para_formato_sistema(self, df: pd.DataFrame, alturas: List[int], response, 
                                                 incluir_temperatura: bool = True, incluir_umidade: bool = True) -> Dict:
        """Converte o DataFrame otimizado para o formato esperado pelo sistema, incluindo temperatura e umidade."""
        
        resultado = {
            'metadata': {
                'latitude': response.Latitude(),
                'longitude': response.Longitude(),
                'timezone': f"{response.Timezone()}{response.TimezoneAbbreviation()}",
                'utc_offset_seconds': response.UtcOffsetSeconds(),
                'elevation': response.Elevation(),
                'periodo_inicio': df['date'].iloc[0].strftime('%Y-%m-%d %H:%M:%S') if len(df) > 0 else None,
                'periodo_fim': df['date'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S') if len(df) > 0 else None,
                'total_registros': len(df),
                'fonte': 'Open-Meteo',
                'dados_incluidos': {
                    'velocidade_vento': True,
                    'temperatura': incluir_temperatura and 'temperature_2m' in df.columns,
                    'umidade': incluir_umidade and 'relative_humidity_2m' in df.columns
                },
                'alturas_dados': {
                    'velocidade_vento': f"{', '.join([str(h) for h in alturas])}m",
                    'temperatura': "2m" if incluir_temperatura and 'temperature_2m' in df.columns else "N/A",
                    'umidade': "2m" if incluir_umidade and 'relative_humidity_2m' in df.columns else "N/A"
                }
            },
            'dados_por_altura': {},
            'dados': []
        }
        
        # Processar dados por altura
        for altura in alturas:
            col_name = f"wind_speed_{altura}m"
            if col_name in df.columns:
                velocidades = df[col_name].tolist()
                timestamps = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
                
                # Calcular estatísticas
                velocidades_validas = df[col_name].dropna()
                
                if len(velocidades_validas) > 0:
                    estatisticas = {
                        'velocidade_media': float(velocidades_validas.mean()),
                        'velocidade_maxima': float(velocidades_validas.max()),
                        'velocidade_minima': float(velocidades_validas.min()),
                        'total_registros': len(velocidades_validas),
                        'registros_nulos': len(df) - len(velocidades_validas)
                    }
                else:
                    estatisticas = {
                        'velocidade_media': 0,
                        'velocidade_maxima': 0,
                        'velocidade_minima': 0,
                        'total_registros': 0,
                        'registros_nulos': len(df)
                    }
                
                resultado['dados_por_altura'][f"{altura}m"] = {
                    'altura_metros': altura,
                    'timestamps': timestamps,
                    'velocidades_vento': velocidades,
                    'estatisticas': estatisticas
                }
                
                # Adicionar registros individuais para interface
                for i, row in df.iterrows():
                    if pd.notna(row[col_name]):
                        # Extrair temperatura se disponível
                        temperatura = None
                        if incluir_temperatura and 'temperature_2m' in df.columns:
                            temp_val = row['temperature_2m']
                            temperatura = float(temp_val) if pd.notna(temp_val) else None
                        
                        # Extrair umidade se disponível
                        umidade = None
                        if incluir_umidade and 'relative_humidity_2m' in df.columns:
                            humid_val = row['relative_humidity_2m']
                            umidade = float(humid_val) if pd.notna(humid_val) else None
                        
                        resultado['dados'].append({
                            'data_hora': row['date'].to_pydatetime(),
                            'temperatura': temperatura,
                            'umidade': umidade,
                            'velocidade_vento': float(row[col_name]),
                            'altura_captura': altura
                        })
        
        return resultado
    
    def _processar_resposta_basica(self, data: Dict, alturas: List[int], 
                                  incluir_temperatura: bool = True, incluir_umidade: bool = True) -> Dict:
        """Processa resposta do cliente básico com temperatura e umidade (código mantido para compatibilidade)."""
        if 'hourly' not in data:
            raise ValueError("Resposta da API não contém dados horários")
        
        hourly_data = data['hourly']
        timestamps = hourly_data.get('time', [])
        
        # Verificar se há dados de temperatura e umidade disponíveis
        temperatura_disponivel = incluir_temperatura and 'temperature_2m' in hourly_data
        umidade_disponivel = incluir_umidade and 'relative_humidity_2m' in hourly_data
        
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
                'fonte': 'Open-Meteo',
                'dados_incluidos': {
                    'velocidade_vento': True,
                    'temperatura': temperatura_disponivel,
                    'umidade': umidade_disponivel
                },
                'alturas_dados': {
                    'velocidade_vento': f"{', '.join([str(h) for h in alturas])}m",
                    'temperatura': "2m" if temperatura_disponivel else "N/A",
                    'umidade': "2m" if umidade_disponivel else "N/A"
                }
            },
            'dados_por_altura': {},
            'dados': []
        }
        
        # Extrair dados de temperatura e umidade
        temperaturas = hourly_data.get('temperature_2m', []) if temperatura_disponivel else []
        umidades = hourly_data.get('relative_humidity_2m', []) if umidade_disponivel else []
        
        # Processar dados por altura
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
            
            # Adicionar registros individuais
            for i, timestamp in enumerate(timestamps):
                if i < len(velocidades) and velocidades[i] is not None:
                    try:
                        data_hora_registro = datetime.fromisoformat(timestamp.replace('T', ' '))
                        
                        # Extrair temperatura se disponível
                        temperatura = None
                        if temperatura_disponivel and i < len(temperaturas):
                            temperatura = temperaturas[i] if temperaturas[i] is not None else None
                        
                        # Extrair umidade se disponível
                        umidade = None
                        if umidade_disponivel and i < len(umidades):
                            umidade = umidades[i] if umidades[i] is not None else None
                        
                        resultado['dados'].append({
                            'data_hora': data_hora_registro,
                            'temperatura': temperatura,
                            'umidade': umidade,
                            'velocidade_vento': velocidades[i],
                            'altura_captura': altura
                        })
                    except (ValueError, IndexError):
                        continue
        
        return resultado
    
    def _validar_parametros(self, latitude: float, longitude: float, 
                           data_inicio: Union[str, date], data_fim: Union[str, date]):
        """Valida os parâmetros de entrada."""
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} deve estar entre -90 e 90")
        
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} deve estar entre -180 e 180")
        
        # Converter e validar datas
        if isinstance(data_inicio, date):
            data_inicio = data_inicio.strftime('%Y-%m-%d')
        if isinstance(data_fim, date):
            data_fim = data_fim.strftime('%Y-%m-%d')
        
        try:
            datetime.strptime(data_inicio, '%Y-%m-%d')
            datetime.strptime(data_fim, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Formato de data inválido. Use YYYY-MM-DD: {e}")
    
    def obter_informacoes_api(self) -> Dict:
        """
        Retorna informações sobre as capacidades e limitações da API Open-Meteo.
        
        Returns:
            Dict: Informações da API
        """
        return {
            'nome': 'Open-Meteo Historical Weather API',
            'client_type': self.client_type,
            'url_historical': self.BASE_URL_HISTORICAL,
            'url_archive': self.BASE_URL_ARCHIVE,
            'alturas_suportadas': self.ALTURAS_SUPORTADAS,
            'unidade_velocidade': 'm/s',
            'frequencia_dados': 'Horária',
            'periodo_historico': 'A partir de 1940',
            'gratuita': True,
            'cache_ativo': self.use_cache and self.client_type == "optimized",
            'cliente_otimizado_disponivel': CLIENTE_OTIMIZADO_DISPONIVEL,
            'limite_requisicoes': 'Sem limite oficial, mas recomenda-se uso responsável',
            'documentacao': 'https://open-meteo.com/en/docs/historical-weather-api'
        }
    
    def __str__(self) -> str:
        """Representação em string do cliente."""
        return f"OpenMeteoClient(type={self.client_type}, alturas_suportadas={self.ALTURAS_SUPORTADAS})"
    
    def __repr__(self) -> str:
        """Representação técnica do cliente."""
        return f"OpenMeteoClient(timeout={self.timeout}, client_type='{self.client_type}')"
