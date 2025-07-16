"""
Serviços de coleta e gerenciamento de dados climáticos.

Este módulo contém serviços para coleta, armazenamento
e gerenciamento de dados climáticos de diferentes fontes.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.entity import DadosEolicos, LocalizacaoClimatica, SerieTemporalVento
from ..models.repository import DadosEolicosRepository, LocalizacaoClimaticaRepository
from ..api.open_meteo_client import OpenMeteoClient, APIError


class ColetaDadosService:
    """
    Serviço para coleta e armazenamento de dados climáticos.
    
    Gerencia a coleta de dados de diferentes fontes (APIs, arquivos)
    e armazenamento no banco de dados local.
    """
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        """
        Inicializa o serviço de coleta.
        
        Args:
            db_path: Caminho para o banco de dados
        """
        self.api_client = OpenMeteoClient()
        self.dados_repo = DadosEolicosRepository(db_path)
        self.localizacao_repo = LocalizacaoClimaticaRepository(db_path)
    
    def coletar_dados_historicos(self, latitude: float, longitude: float,
                                nome_cidade: str, periodo_dias: int = 365,
                                altura_vento: int = 10,
                                salvar_bd: bool = True) -> List[DadosEolicos]:
        """
        Coleta dados históricos de uma localização.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            nome_cidade: Nome da cidade/localização
            periodo_dias: Número de dias anteriores a coletar
            altura_vento: Altura de medição do vento
            salvar_bd: Se deve salvar no banco de dados
        
        Returns:
            Lista de dados eólicos coletados
        
        Raises:
            APIError: Erro na coleta de dados
        """
        # Calcula período
        fim = datetime.now()
        inicio = fim - timedelta(days=periodo_dias)
        
        try:
            # Coleta dados da API
            dados = self.api_client.obter_dados_historicos(
                latitude, longitude, inicio, fim, altura_vento, nome_cidade
            )
            
            if salvar_bd and dados:
                # Salva dados no banco
                self.dados_repo.criar_multiplos(dados)
                
                # Cria/atualiza localização
                localizacao = LocalizacaoClimatica(
                    nome=nome_cidade,
                    latitude=latitude,
                    longitude=longitude
                )
                self.localizacao_repo.criar(localizacao)
            
            return dados
        
        except APIError as e:
            raise APIError(f"Erro ao coletar dados históricos: {e}")
    
    def coletar_dados_previsao(self, latitude: float, longitude: float,
                              nome_cidade: str, dias_previsao: int = 7,
                              altura_vento: int = 10,
                              salvar_bd: bool = True) -> List[DadosEolicos]:
        """
        Coleta dados de previsão de uma localização.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            nome_cidade: Nome da cidade/localização
            dias_previsao: Número de dias de previsão
            altura_vento: Altura de medição do vento
            salvar_bd: Se deve salvar no banco de dados
        
        Returns:
            Lista de dados eólicos coletados
        """
        try:
            print(f"📡 Coletando previsão para {nome_cidade} ({latitude}, {longitude})")
            
            # Coletar dados de previsão usando a API
            dados_brutos = self.api_client.obter_previsao_tempo(
                latitude, longitude, dias_previsao
            )
            
            if not dados_brutos:
                print("❌ Nenhum dado de previsão retornado pela API")
                return []
            
            # Converter para entidades DadosEolicos
            dados_eolicos = self._converter_dados_api_para_entidade(
                dados_brutos, nome_cidade, latitude, longitude, altura_vento
            )
            
            if salvar_bd and dados_eolicos:
                # Salvar no banco de dados
                ids_salvos = self.dados_repo.criar_multiplos(dados_eolicos)
                print(f"💾 {len(ids_salvos)} registros de previsão salvos no banco")
            
            print(f"✅ Coleta de previsão concluída: {len(dados_eolicos)} registros")
            return dados_eolicos
            
        except APIError as e:
            print(f"❌ Erro da API: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Erro inesperado na coleta de previsão: {str(e)}")
            return []
    
    def coletar_dados_ano_completo(self, latitude: float, longitude: float,
                                  nome_cidade: str, ano: int,
                                  altura_vento: int = 10,
                                  salvar_bd: bool = True) -> List[DadosEolicos]:
        """
        Coleta dados de um ano completo.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            nome_cidade: Nome da cidade/localização
            ano: Ano para coleta completa
            altura_vento: Altura de medição do vento
            salvar_bd: Se deve salvar no banco de dados
        
        Returns:
            Lista de dados eólicos coletados
        """
        try:
            print(f"📡 Coletando dados do ano {ano} para {nome_cidade}")
            
            # Coletar dados do ano usando a API
            dados_brutos = self.api_client.obter_ano_completo(
                latitude, longitude, ano
            )
            
            if not dados_brutos:
                print("❌ Nenhum dado anual retornado pela API")
                return []
            
            # Converter para entidades DadosEolicos
            dados_eolicos = self._converter_dados_api_para_entidade(
                dados_brutos, nome_cidade, latitude, longitude, altura_vento
            )
            
            if salvar_bd and dados_eolicos:
                # Salvar no banco de dados
                ids_salvos = self.dados_repo.criar_multiplos(dados_eolicos)
                print(f"💾 {len(ids_salvos)} registros do ano {ano} salvos no banco")
            
            print(f"✅ Coleta anual concluída: {len(dados_eolicos)} registros")
            return dados_eolicos
            
        except APIError as e:
            print(f"❌ Erro da API: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Erro inesperado na coleta anual: {str(e)}")
            return []

    def atualizar_dados_recentes(self, latitude: float, longitude: float,
                               nome_cidade: str, dias_recentes: int = 7) -> int:
        """
        Atualiza com dados mais recentes.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            nome_cidade: Nome da cidade/localização
            dias_recentes: Número de dias recentes a atualizar
        
        Returns:
            Número de novos registros adicionados
        """
        # Verifica dados existentes
        fim = datetime.now()
        inicio = fim - timedelta(days=dias_recentes)
        
        dados_existentes = self.dados_repo.buscar_por_localizacao_periodo(
            latitude, longitude, inicio, fim
        )
        
        # Coleta novos dados
        try:
            novos_dados = self.api_client.obter_dados_historicos(
                latitude, longitude, inicio, fim, 10, nome_cidade
            )
            
            # Filtra dados que já existem
            datas_existentes = {d.data.date() for d in dados_existentes}
            dados_novos = [
                d for d in novos_dados 
                if d.data.date() not in datas_existentes
            ]
            
            if dados_novos:
                self.dados_repo.criar_multiplos(dados_novos)
            
            return len(dados_novos)
        
        except APIError as e:
            print(f"Erro ao atualizar dados: {e}")
            return 0
    
    def importar_dados_json(self, arquivo_path: str,
                          salvar_bd: bool = True) -> List[DadosEolicos]:
        """
        Importa dados de um arquivo JSON.
        
        Args:
            arquivo_path: Caminho para o arquivo JSON
            salvar_bd: Se deve salvar no banco de dados
        
        Returns:
            Lista de dados importados
        """
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dados_eolicos = []
            
            # Verifica formato do JSON
            if 'metadados' in data and 'dados' in data:
                # Formato com metadados e listas
                metadados = data['metadados']
                dados = data['dados']
                
                cidade = metadados['cidade']
                latitude = metadados['latitude']
                longitude = metadados['longitude']
                altura_vento = metadados.get('altura_vento', 10)
                
                # Processa listas de dados
                for i, data_str in enumerate(dados['datas']):
                    try:
                        dado_eolico = DadosEolicos(
                            cidade=cidade,
                            latitude=latitude,
                            longitude=longitude,
                            temperatura=dados['temperatura'][i],
                            umidade=dados['umidade'][i],
                            velocidade_vento=dados['velocidade_vento'][i],
                            data=datetime.strptime(data_str, '%Y-%m-%d'),
                            altura_medicao=altura_vento
                        )
                        dados_eolicos.append(dado_eolico)
                    except (IndexError, ValueError) as e:
                        print(f"Erro ao processar registro {i}: {e}")
                        continue
            
            elif isinstance(data, list):
                # Formato de lista de objetos
                for item in data:
                    try:
                        dado_eolico = DadosEolicos.from_dict(item)
                        dados_eolicos.append(dado_eolico)
                    except (KeyError, ValueError) as e:
                        print(f"Erro ao processar item: {e}")
                        continue
            
            # Salva no banco se solicitado
            if salvar_bd and dados_eolicos:
                self.dados_repo.criar_multiplos(dados_eolicos)
            
            return dados_eolicos
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Erro ao importar arquivo JSON: {e}")
    
    def exportar_dados_json(self, latitude: float, longitude: float,
                          inicio: Optional[datetime] = None,
                          fim: Optional[datetime] = None,
                          arquivo_path: Optional[str] = None) -> str:
        """
        Exporta dados para arquivo JSON.
        
        Args:
            latitude: Latitude da localização
            longitude: Longitude da localização
            inicio: Data de início (opcional)
            fim: Data de fim (opcional)
            arquivo_path: Caminho do arquivo (opcional)
        
        Returns:
            Caminho do arquivo criado
        """
        # Define período padrão se não especificado
        if fim is None:
            fim = datetime.now()
        if inicio is None:
            inicio = fim - timedelta(days=365)
        
        # Busca dados
        dados = self.dados_repo.buscar_por_localizacao_periodo(
            latitude, longitude, inicio, fim
        )
        
        if not dados:
            raise ValueError("Nenhum dado encontrado para os critérios especificados")
        
        # Organiza dados por formato
        primeiro_dado = dados[0]
        
        dados_exportacao = {
            "metadados": {
                "cidade": primeiro_dado.cidade,
                "latitude": primeiro_dado.latitude,
                "longitude": primeiro_dado.longitude,
                "altura_vento": primeiro_dado.altura_medicao,
                "periodo_inicio": inicio.isoformat(),
                "periodo_fim": fim.isoformat(),
                "total_registros": len(dados)
            },
            "dados": {
                "datas": [d.data.strftime('%Y-%m-%d') for d in dados],
                "temperatura": [d.temperatura for d in dados],
                "umidade": [d.umidade for d in dados],
                "velocidade_vento": [d.velocidade_vento for d in dados],
                "direcao_vento": [d.direcao_vento for d in dados],
                "velocidade_vento_max": [d.velocidade_vento_max for d in dados]
            }
        }
        
        # Define nome do arquivo se não especificado
        if arquivo_path is None:
            nome_cidade = primeiro_dado.cidade.lower().replace(' ', '_')
            data_str = datetime.now().strftime('%Y%m%d')
            arquivo_path = f"data/export_{nome_cidade}_{data_str}.json"
        
        # Cria diretório se necessário
        Path(arquivo_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Salva arquivo
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            json.dump(dados_exportacao, f, indent=2, ensure_ascii=False)
        
        return arquivo_path
    
    def verificar_qualidade_dados(self, dados: List[DadosEolicos]) -> Dict[str, Any]:
        """
        Verifica qualidade dos dados coletados.
        
        Args:
            dados: Lista de dados a verificar
        
        Returns:
            Relatório de qualidade
        """
        if not dados:
            return {
                'qualidade_geral': 'sem_dados',
                'total_registros': 0
            }
        
        total = len(dados)
        
        # Verifica valores nulos ou inválidos
        temp_invalidos = sum(1 for d in dados if d.temperatura is None or d.temperatura < -50 or d.temperatura > 60)
        umidade_invalidos = sum(1 for d in dados if d.umidade is None or d.umidade < 0 or d.umidade > 100)
        vento_invalidos = sum(1 for d in dados if d.velocidade_vento is None or d.velocidade_vento < 0 or d.velocidade_vento > 100)
        
        # Verifica sequência temporal
        dados_ordenados = sorted(dados, key=lambda x: x.data)
        lacunas = 0
        for i in range(len(dados_ordenados) - 1):
            if (dados_ordenados[i+1].data - dados_ordenados[i].data).days > 1:
                lacunas += 1
        
        # Calcula scores
        score_valores = 100 - ((temp_invalidos + umidade_invalidos + vento_invalidos) / (total * 3)) * 100
        score_continuidade = 100 - (lacunas / max(total - 1, 1)) * 100
        score_geral = (score_valores + score_continuidade) / 2
        
        # Classifica qualidade
        if score_geral >= 90:
            qualidade = 'excelente'
        elif score_geral >= 75:
            qualidade = 'boa'
        elif score_geral >= 60:
            qualidade = 'regular'
        else:
            qualidade = 'ruim'
        
        return {
            'qualidade_geral': qualidade,
            'score_geral': score_geral,
            'total_registros': total,
            'valores_invalidos': {
                'temperatura': temp_invalidos,
                'umidade': umidade_invalidos,
                'velocidade_vento': vento_invalidos
            },
            'lacunas_temporais': lacunas,
            'periodo': {
                'inicio': min(d.data for d in dados).isoformat(),
                'fim': max(d.data for d in dados).isoformat()
            }
        }


class GerenciamentoLocalizacoesService:
    """
    Serviço para gerenciamento de localizações climáticas.
    
    Gerencia cadastro, busca e atualização de localizações
    com dados climáticos.
    """
    
    def __init__(self, db_path: str = "data/wind_turbine.db"):
        """
        Inicializa o serviço.
        
        Args:
            db_path: Caminho para o banco de dados
        """
        self.localizacao_repo = LocalizacaoClimaticaRepository(db_path)
        self.dados_repo = DadosEolicosRepository(db_path)
        self.coleta_service = ColetaDadosService(db_path)
    
    def cadastrar_localizacao(self, nome: str, latitude: float, longitude: float,
                            altitude: Optional[float] = None,
                            tipo_terreno: Optional[str] = None,
                            coletar_dados: bool = True) -> LocalizacaoClimatica:
        """
        Cadastra uma nova localização climática.
        
        Args:
            nome: Nome da localização
            latitude: Latitude
            longitude: Longitude
            altitude: Altitude em metros (opcional)
            tipo_terreno: Tipo de terreno (opcional)
            coletar_dados: Se deve coletar dados históricos
        
        Returns:
            Localização criada
        """
        localizacao = LocalizacaoClimatica(
            nome=nome,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            tipo_terreno=tipo_terreno
        )
        
        # Salva no banco
        self.localizacao_repo.criar(localizacao)
        
        # Coleta dados históricos se solicitado
        if coletar_dados:
            try:
                self.coleta_service.coletar_dados_historicos(
                    latitude, longitude, nome, periodo_dias=365
                )
            except APIError as e:
                print(f"Aviso: Não foi possível coletar dados para {nome}: {e}")
        
        return localizacao
    
    def listar_localizacoes_com_dados(self) -> List[Dict[str, Any]]:
        """
        Lista localizações com resumo dos dados disponíveis.
        
        Returns:
            Lista de localizações com estatísticas
        """
        localizacoes = self.localizacao_repo.listar_todas()
        resultado = []
        
        for loc in localizacoes:
            # Busca estatísticas dos dados
            stats = self.dados_repo.calcular_estatisticas_localizacao(
                loc.latitude, loc.longitude
            )
            
            resultado.append({
                'localizacao': loc.to_dict(),
                'dados_disponiveis': stats.get('total_registros', 0),
                'media_vento': stats.get('media_vento', 0),
                'periodo_dados': self._obter_periodo_dados(loc.latitude, loc.longitude)
            })
        
        return resultado
    
    def buscar_localizacoes_proximas(self, latitude: float, longitude: float,
                                   raio_km: float = 50) -> List[LocalizacaoClimatica]:
        """
        Busca localizações próximas a um ponto.
        
        Args:
            latitude: Latitude do ponto de referência
            longitude: Longitude do ponto de referência
            raio_km: Raio de busca em quilômetros
        
        Returns:
            Lista de localizações próximas
        """
        todas_localizacoes = self.localizacao_repo.listar_todas()
        proximas = []
        
        for loc in todas_localizacoes:
            distancia = self._calcular_distancia(
                latitude, longitude, loc.latitude, loc.longitude
            )
            
            if distancia <= raio_km:
                proximas.append(loc)
        
        # Ordena por distância
        proximas.sort(key=lambda loc: self._calcular_distancia(
            latitude, longitude, loc.latitude, loc.longitude
        ))
        
        return proximas
    
    def _obter_periodo_dados(self, latitude: float, longitude: float) -> Dict[str, Optional[str]]:
        """Obtém período de dados disponíveis para uma localização."""
        dados = self.dados_repo.buscar_por_localizacao_periodo(
            latitude, longitude,
            datetime(2020, 1, 1), datetime.now()
        )
        
        if dados:
            return {
                'inicio': min(d.data for d in dados).isoformat(),
                'fim': max(d.data for d in dados).isoformat()
            }
        
        return {'inicio': None, 'fim': None}
    
    def _calcular_distancia(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """
        Calcula distância entre dois pontos em km usando fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas do primeiro ponto
            lat2, lon2: Coordenadas do segundo ponto
        
        Returns:
            Distância em quilômetros
        """
        import math
        
        # Converte para radianos
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Raio da Terra em km
        r = 6371
        
        return c * r
