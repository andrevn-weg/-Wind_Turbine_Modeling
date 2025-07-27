"""
Cliente NASA POWER API

Este módulo implementa um cliente para a API NASA POWER (Prediction of Worldwide Energy Resources),
que fornece dados meteorológicos e de energia solar baseados em dados satellitais.

LIMITAÇÕES DE ALTURA SUPORTADAS:
- 10m: Velocidade do vento a 10 metros de altura
- 50m: Velocidade do vento a 50 metros de altura

APENAS estas duas alturas (10m e 50m) são suportadas pela API NASA POWER.
Qualquer outra altura resultará em erro.

API Documentation: https://power.larc.nasa.gov/docs/
"""

import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Union
import json


class NASAPowerClient:
    """
    Cliente para a API NASA POWER para obtenção de dados meteorológicos históricos.
    
    A API NASA POWER fornece dados meteorológicos baseados em satélites da NASA,
    incluindo velocidade do vento em alturas de 10m e 50m.
    """
    
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    ALTURAS_SUPORTADAS = [10, 50]  # metros
    
    def __init__(self, timeout: int = 60):
        """
        Inicializa o cliente NASA POWER.
        
        Args:
            timeout: Timeout para requisições HTTP em segundos (padrão: 60)
                    NASA POWER pode ser mais lenta que outras APIs
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Wind-Turbine-Modeling/1.0'
        })
    
    def validar_altura(self, altura: int) -> bool:
        """
        Valida se a altura solicitada é suportada pela API NASA POWER.
        
        Args:
            altura: Altura em metros
            
        Returns:
            bool: True se a altura é suportada, False caso contrário
            
        Raises:
            ValueError: Se a altura não é suportada
        """
        if altura not in self.ALTURAS_SUPORTADAS:
            raise ValueError(
                f"Altura {altura}m não é suportada pela API NASA POWER. "
                f"Alturas suportadas: {self.ALTURAS_SUPORTADAS} (apenas 10m e 50m)"
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
            data_inicio: Data de início (formato: YYYYMMDD ou objeto date)
            data_fim: Data de fim (formato: YYYYMMDD ou objeto date)
            alturas: Lista de alturas em metros. Se None, usa todas as alturas suportadas
            incluir_temperatura: Se deve incluir dados de temperatura a 2m (padrão: True)
            incluir_umidade: Se deve incluir dados de umidade relativa a 2m (padrão: True)
            
        Returns:
            Dict: Dados meteorológicos organizados por altura, incluindo temperatura e umidade
            
        Raises:
            ValueError: Se parâmetros inválidos
            requests.RequestException: Se erro na requisição HTTP
            
        Note:
            - Velocidade do vento: obtida nas alturas especificadas (10m, 50m)
            - Temperatura: sempre obtida a 2 metros de altura
            - Umidade relativa: sempre obtida a 2 metros de altura
        """
        # Validar parâmetros
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} deve estar entre -90 e 90")
        
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} deve estar entre -180 e 180")
        
        # Converter datas para formato NASA POWER (YYYYMMDD)
        if isinstance(data_inicio, date):
            data_inicio_str = data_inicio.strftime('%Y%m%d')
        else:
            data_inicio_str = self._validar_formato_data_nasa(data_inicio)
        
        if isinstance(data_fim, date):
            data_fim_str = data_fim.strftime('%Y%m%d')
        else:
            data_fim_str = self._validar_formato_data_nasa(data_fim)
        
        # Usar todas as alturas suportadas se não especificado
        if alturas is None:
            alturas = self.ALTURAS_SUPORTADAS.copy()
        
        # Validar alturas
        for altura in alturas:
            self.validar_altura(altura)
        
        # Construir parâmetros da requisição
        params = {
            'start': data_inicio_str,
            'end': data_fim_str,
            'latitude': latitude,
            'longitude': longitude,
            'community': 'RE',  # Renewable Energy community
            'parameters': self._construir_parametros_meteorologicos(alturas, incluir_temperatura, incluir_umidade),
            'format': 'JSON',
            'header': 'true',
            'time-standard': 'UTC'
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
            return self._processar_resposta(data, alturas, latitude, longitude, incluir_temperatura, incluir_umidade)
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Erro na requisição NASA POWER: {e}")
    
    def obter_dados_ano_completo(
        self,
        latitude: float,
        longitude: float,
        ano: int,
        alturas: Optional[List[int]] = None,
        incluir_temperatura: bool = True,
        incluir_umidade: bool = True
    ) -> Dict:
        """
        Obtém dados históricos de vento, temperatura e umidade para um ano completo.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            ano: Ano desejado (ex: 2024)
            alturas: Lista de alturas em metros
            incluir_temperatura: Se deve incluir dados de temperatura
            incluir_umidade: Se deve incluir dados de umidade
            
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
            alturas=alturas,
            incluir_temperatura=incluir_temperatura,
            incluir_umidade=incluir_umidade
        )
    
    def obter_dados_ultimo_ano(
        self,
        latitude: float,
        longitude: float,
        alturas: Optional[List[int]] = None
    ) -> Dict:
        """
        Obtém dados históricos de vento do último ano (365 dias retroativos).
        
        Note: NASA POWER pode ter atraso de alguns dias nos dados mais recentes.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            alturas: Lista de alturas em metros
            
        Returns:
            Dict: Dados meteorológicos do último ano
        """
        # NASA POWER pode ter atraso, usar dados até 1 semana atrás
        data_fim = date.today() - timedelta(days=7)
        data_inicio = data_fim - timedelta(days=364)  # 365 dias atrás
        
        return self.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=alturas
        )
    
    def _validar_formato_data_nasa(self, data_str: str) -> str:
        """
        Valida e converte formato de data para NASA POWER (YYYYMMDD).
        
        Args:
            data_str: Data em formato string
            
        Returns:
            str: Data no formato YYYYMMDD
            
        Raises:
            ValueError: Se formato inválido
        """
        # Tentar diferentes formatos
        formatos = ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d']
        
        for formato in formatos:
            try:
                data_obj = datetime.strptime(data_str, formato)
                return data_obj.strftime('%Y%m%d')
            except ValueError:
                continue
        
        raise ValueError(
            f"Formato de data inválido: {data_str}. "
            f"Use YYYYMMDD, YYYY-MM-DD ou YYYY/MM/DD"
        )
    
    def _construir_parametros_vento(self, alturas: List[int]) -> str:
        """
        Constrói a string de parâmetros para velocidade do vento nas alturas especificadas.
        
        Args:
            alturas: Lista de alturas em metros
            
        Returns:
            str: Parâmetros separados por vírgula para a API NASA
        """
        parametros = []
        for altura in alturas:
            if altura == 10:
                parametros.append("WS10M")  # Wind Speed at 10 Meters
            elif altura == 50:
                parametros.append("WS50M")  # Wind Speed at 50 Meters
        
        return ','.join(parametros)
    
    def _construir_parametros_meteorologicos(self, alturas: List[int], incluir_temperatura: bool = True, incluir_umidade: bool = True) -> str:
        """
        Constrói a string de parâmetros completa incluindo vento, temperatura e umidade.
        
        Args:
            alturas: Lista de alturas em metros para velocidade do vento
            incluir_temperatura: Se deve incluir temperatura
            incluir_umidade: Se deve incluir umidade relativa
            
        Returns:
            str: Parâmetros separados por vírgula para a API NASA POWER
        """
        parametros = []
        
        # Adicionar parâmetros de vento
        for altura in alturas:
            if altura == 10:
                parametros.append("WS10M")  # Wind Speed at 10 Meters
            elif altura == 50:
                parametros.append("WS50M")  # Wind Speed at 50 Meters
        
        # Adicionar temperatura se solicitada
        if incluir_temperatura:
            parametros.append("T2M")  # Temperature at 2 Meters
        
        # Adicionar umidade relativa se solicitada
        if incluir_umidade:
            parametros.append("RH2M")  # Relative Humidity at 2 Meters
        
        return ','.join(parametros)
    
    def _processar_resposta(self, data: Dict, alturas: List[int], lat: float, lon: float, 
                           incluir_temperatura: bool = True, incluir_umidade: bool = True) -> Dict:
        """
        Processa a resposta da API organizando os dados por altura, incluindo temperatura e umidade.
        
        Args:
            data: Dados brutos da API
            alturas: Lista de alturas solicitadas
            lat: Latitude da requisição
            lon: Longitude da requisição
            incluir_temperatura: Se dados de temperatura foram solicitados
            incluir_umidade: Se dados de umidade foram solicitados
            
        Returns:
            Dict: Dados organizados por altura e processados
        """
        if 'properties' not in data:
            raise ValueError("Resposta da API não contém dados de propriedades")
        
        properties = data['properties']
        parameter_data = properties.get('parameter', {})
        
        # Verificar se há dados válidos
        if not parameter_data:
            raise ValueError("API NASA POWER retornou dados vazios para os parâmetros solicitados")
        
        # Verificar disponibilidade de dados por parâmetro
        temperatura_disponivel = incluir_temperatura and 'T2M' in parameter_data and bool(parameter_data['T2M'])
        umidade_disponivel = incluir_umidade and 'RH2M' in parameter_data and bool(parameter_data['RH2M'])
        
        # Extrair dados de temperatura e umidade
        dados_temperatura = parameter_data.get('T2M', {}) if temperatura_disponivel else {}
        dados_umidade = parameter_data.get('RH2M', {}) if umidade_disponivel else {}
        
        # Inicializar estrutura de resultado
        resultado = {
            'metadata': {
                'fonte': 'NASA POWER',
                'latitude': lat,
                'longitude': lon,
                'dados_incluidos': {
                    'velocidade_vento': True,
                    'temperatura': temperatura_disponivel,
                    'umidade': umidade_disponivel
                },
                'alturas_dados': {
                    'velocidade_vento': f"{', '.join([str(h) for h in alturas])}m",
                    'temperatura': "2m" if temperatura_disponivel else "N/A",
                    'umidade': "2m" if umidade_disponivel else "N/A"
                },
                'header': data.get('header', {}),
                'mensagens': data.get('messages', [])
            },
            'dados_por_altura': {},
            'dados': []
        }
        
        # Coletar todos os timestamps únicos de todos os parâmetros
        todos_timestamps = set()
        
        # Processar dados por altura de vento
        alturas_com_dados = []
        
        for altura in alturas:
            # Determinar parâmetro NASA POWER baseado na altura
            if altura == 10:
                parametro_vento = "WS10M"
            elif altura == 50:
                parametro_vento = "WS50M"
            else:
                continue  # Altura não suportada pela NASA POWER
            
            # Verificar se dados estão disponíveis para esta altura
            if parametro_vento not in parameter_data or not parameter_data[parametro_vento]:
                print(f"⚠️ Dados não disponíveis para altura {altura}m (parâmetro {parametro_vento})")
                continue
            
            dados_vento = parameter_data[parametro_vento]
            alturas_com_dados.append(altura)
            
            # Coletar timestamps deste parâmetro
            todos_timestamps.update(dados_vento.keys())
            
            # Processar dados de vento para esta altura
            timestamps_ordenados = sorted(dados_vento.keys())
            velocidades = []
            
            for timestamp in timestamps_ordenados:
                velocidade = dados_vento[timestamp]
                # Converter -999 (valor faltante NASA) para None
                velocidades.append(velocidade if velocidade != -999 else None)
            
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
            
            # Adicionar dados organizados por altura
            resultado['dados_por_altura'][f"{altura}m"] = {
                'altura_metros': altura,
                'parametro_nasa': parametro_vento,
                'timestamps': timestamps_ordenados,
                'velocidades_vento': velocidades,
                'estatisticas': estatisticas
            }
        
        # Verificar se conseguimos dados de pelo menos uma altura
        if not alturas_com_dados:
            raise ValueError(f"Nenhum dado de vento disponível para as alturas solicitadas: {alturas}")
        
        # Processar registros individuais combinando dados de todas as alturas
        todos_timestamps_ordenados = sorted(todos_timestamps)
        
        for timestamp in todos_timestamps_ordenados:
            try:
                # Converter timestamp NASA POWER para datetime
                # Formato pode ser YYYYMMDDHH ou YYYYMMDD
                if len(timestamp) >= 10:  # Com hora
                    data_hora_registro = datetime.strptime(timestamp, '%Y%m%d%H')
                else:  # Apenas data
                    data_hora_registro = datetime.strptime(timestamp, '%Y%m%d').replace(hour=12)
                
                # Para cada altura que tem dados neste timestamp
                for altura in alturas_com_dados:
                    parametro_vento = "WS10M" if altura == 10 else "WS50M"
                    dados_vento = parameter_data[parametro_vento]
                    
                    if timestamp in dados_vento:
                        velocidade = dados_vento[timestamp]
                        if velocidade != -999:  # Apenas incluir valores válidos
                            
                            # Obter temperatura para este timestamp (se disponível)
                            temperatura = None
                            if temperatura_disponivel and timestamp in dados_temperatura:
                                temp_val = dados_temperatura[timestamp]
                                temperatura = temp_val if temp_val != -999 else None
                            
                            # Obter umidade para este timestamp (se disponível)
                            umidade = None
                            if umidade_disponivel and timestamp in dados_umidade:
                                umid_val = dados_umidade[timestamp]
                                umidade = umid_val if umid_val != -999 else None
                            
                            # Adicionar registro
                            resultado['dados'].append({
                                'data_hora': data_hora_registro,
                                'temperatura': temperatura,
                                'umidade': umidade,
                                'velocidade_vento': velocidade,
                                'altura_captura': altura
                            })
                            
            except ValueError as e:
                print(f"⚠️ Erro ao processar timestamp {timestamp}: {e}")
                continue
        
        # Adicionar informações de período aos metadados
        if resultado['dados']:
            resultado['metadata']['periodo_inicio'] = min(d['data_hora'] for d in resultado['dados']).strftime('%Y-%m-%d %H:%M:%S')
            resultado['metadata']['periodo_fim'] = max(d['data_hora'] for d in resultado['dados']).strftime('%Y-%m-%d %H:%M:%S')
            resultado['metadata']['total_registros'] = len(resultado['dados'])
        else:
            resultado['metadata']['periodo_inicio'] = None
            resultado['metadata']['periodo_fim'] = None
            resultado['metadata']['total_registros'] = 0
        
        return resultado
    
    def obter_parametros_disponiveis(self) -> Dict:
        """
        Retorna informações sobre os parâmetros disponíveis na NASA POWER para vento.
        
        Returns:
            Dict: Parâmetros e suas descrições
        """
        return {
            'WS10M': {
                'nome': 'Wind Speed at 10 Meters',
                'descricao': 'Velocidade do vento a 10 metros de altura',
                'unidade': 'm/s',
                'altura': 10
            },
            'WS50M': {
                'nome': 'Wind Speed at 50 Meters', 
                'descricao': 'Velocidade do vento a 50 metros de altura',
                'unidade': 'm/s',
                'altura': 50
            }
        }
    
    def obter_informacoes_api(self) -> Dict:
        """
        Retorna informações sobre as capacidades e limitações da API NASA POWER.
        
        Returns:
            Dict: Informações da API
        """
        return {
            'nome': 'NASA POWER API',
            'url_base': self.BASE_URL,
            'alturas_suportadas': self.ALTURAS_SUPORTADAS,
            'unidade_velocidade': 'm/s',
            'frequencia_dados': 'Horária',
            'periodo_historico': 'A partir de 1981',
            'resolucao_espacial': '0.5° x 0.625°',
            'atraso_dados': '7-10 dias para dados mais recentes',
            'gratuita': True,
            'limite_requisicoes': 'Sem limite oficial, mas recomenda-se uso responsável',
            'documentacao': 'https://power.larc.nasa.gov/docs/',
            'fonte_dados': 'Dados de satélite e modelos de reanalise'
        }
    
    def verificar_disponibilidade_periodo(self, data_inicio: Union[str, date], data_fim: Union[str, date]) -> Dict:
        """
        Verifica se o período solicitado está disponível na NASA POWER.
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            Dict: Informações sobre disponibilidade
        """
        # Converter para date se necessário
        if isinstance(data_inicio, str):
            if len(data_inicio) == 8:  # YYYYMMDD
                data_inicio = datetime.strptime(data_inicio, '%Y%m%d').date()
            else:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        
        if isinstance(data_fim, str):
            if len(data_fim) == 8:  # YYYYMMDD
                data_fim = datetime.strptime(data_fim, '%Y%m%d').date()
            else:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        # Verificar limites
        data_minima = date(1981, 1, 1)
        data_maxima = date.today() - timedelta(days=7)  # Atraso típico
        
        disponivel = data_inicio >= data_minima and data_fim <= data_maxima
        
        return {
            'disponivel': disponivel,
            'data_inicio_solicitada': data_inicio,
            'data_fim_solicitada': data_fim,
            'data_minima_disponivel': data_minima,
            'data_maxima_disponivel': data_maxima,
            'periodo_dias': (data_fim - data_inicio).days + 1,
            'avisos': self._gerar_avisos_periodo(data_inicio, data_fim, data_minima, data_maxima)
        }
    
    def _gerar_avisos_periodo(self, inicio, fim, min_disp, max_disp) -> List[str]:
        """Gera avisos sobre o período solicitado."""
        avisos = []
        
        if inicio < min_disp:
            avisos.append(f"Data de início ({inicio}) é anterior ao período disponível (desde {min_disp})")
        
        if fim > max_disp:
            avisos.append(f"Data de fim ({fim}) pode não ter dados disponíveis (últimos dados: {max_disp})")
        
        duracao = (fim - inicio).days
        if duracao > 365:
            avisos.append(f"Período longo ({duracao} dias) pode resultar em requisição demorada")
        
        return avisos
    
    def __str__(self) -> str:
        """Representação em string do cliente."""
        return f"NASAPowerClient(alturas_suportadas={self.ALTURAS_SUPORTADAS})"
    
    def __repr__(self) -> str:
        """Representação técnica do cliente."""
        return f"NASAPowerClient(timeout={self.timeout}, base_url='{self.BASE_URL}')"
