"""
Entidades do módulo climático.

Este módulo define as classes de entidades para dados climáticos e eólicos,
incluindo validação de dados e métodos auxiliares.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class DadosClimaticos:
    """
    Entidade para dados climáticos básicos.
    
    Representa informações meteorológicas para uma localização específica
    em um determinado momento.
    """
    cidade: str
    latitude: float
    longitude: float
    temperatura: float
    umidade: float
    data: datetime
    altura_medicao: int = 10
    
    def __post_init__(self):
        """Validação após inicialização."""
        self._validar_dados()
    
    def _validar_dados(self):
        """Valida os dados climáticos."""
        if not self.cidade or not self.cidade.strip():
            raise ValueError("Cidade não pode ser vazia")
        
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude deve estar entre -90 e 90 graus")
        
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude deve estar entre -180 e 180 graus")
        
        if not (-50 <= self.temperatura <= 60):
            raise ValueError("Temperatura deve estar entre -50°C e 60°C")
        
        if not (0 <= self.umidade <= 100):
            raise ValueError("Umidade deve estar entre 0% e 100%")
        
        if self.altura_medicao < 0:
            raise ValueError("Altura de medição deve ser positiva")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário."""
        return {
            'cidade': self.cidade,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'temperatura': self.temperatura,
            'umidade': self.umidade,
            'data': self.data.isoformat(),
            'altura_medicao': self.altura_medicao
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DadosClimaticos':
        """Cria uma instância a partir de dicionário."""
        data_copy = data.copy()
        data_copy['data'] = datetime.fromisoformat(data_copy['data'])
        return cls(**data_copy)


@dataclass
class DadosEolicos(DadosClimaticos):
    """
    Entidade especializada para dados eólicos.
    
    Estende DadosClimaticos com informações específicas de vento,
    essenciais para análise de potencial eólico.
    """
    velocidade_vento: float
    direcao_vento: Optional[float] = None
    velocidade_vento_max: Optional[float] = None
    rajada_vento: Optional[float] = None
    
    def __post_init__(self):
        """Validação após inicialização."""
        super().__post_init__()
        self._validar_dados_eolicos()
    
    def _validar_dados_eolicos(self):
        """Valida os dados específicos de vento."""
        if self.velocidade_vento < 0:
            raise ValueError("Velocidade do vento deve ser positiva")
        
        if self.velocidade_vento > 100:
            raise ValueError("Velocidade do vento muito alta (>100 m/s)")
        
        if self.direcao_vento is not None:
            if not (0 <= self.direcao_vento <= 360):
                raise ValueError("Direção do vento deve estar entre 0° e 360°")
        
        if self.velocidade_vento_max is not None:
            if self.velocidade_vento_max < self.velocidade_vento:
                raise ValueError("Velocidade máxima deve ser >= velocidade média")
        
        if self.rajada_vento is not None:
            if self.rajada_vento < self.velocidade_vento:
                raise ValueError("Rajada deve ser >= velocidade média")
    
    def calcular_densidade_ar(self, pressao: float = 1013.25) -> float:
        """
        Calcula a densidade do ar baseada na temperatura e pressão.
        
        Args:
            pressao: Pressão atmosférica em hPa (padrão: 1013.25 hPa)
        
        Returns:
            Densidade do ar em kg/m³
        """
        # Fórmula: ρ = P / (R * T)
        # Onde R = 287.05 J/(kg·K) para ar seco
        R = 287.05  # Constante específica do ar seco
        T_kelvin = self.temperatura + 273.15  # Conversão para Kelvin
        P_pascal = pressao * 100  # Conversão hPa para Pascal
        
        return P_pascal / (R * T_kelvin)
    
    def calcular_potencia_vento(self, area_varredura: float, 
                               eficiencia: float = 0.35) -> float:
        """
        Calcula a potência disponível do vento.
        
        Args:
            area_varredura: Área varrida pelas pás em m²
            eficiencia: Eficiência do aerogerador (padrão: 35%)
        
        Returns:
            Potência em Watts
        """
        densidade = self.calcular_densidade_ar()
        # Fórmula: P = 0.5 * ρ * A * v³ * η
        potencia = 0.5 * densidade * area_varredura * (self.velocidade_vento ** 3) * eficiencia
        return potencia
    
    def classificar_vento(self) -> str:
        """
        Classifica o vento conforme escala de Beaufort simplificada.
        
        Returns:
            Classificação do vento
        """
        v = self.velocidade_vento
        
        if v < 0.3:
            return "Calmaria"
        elif v < 1.6:
            return "Aragem"
        elif v < 3.4:
            return "Brisa leve"
        elif v < 5.5:
            return "Brisa fraca"
        elif v < 8.0:
            return "Brisa moderada"
        elif v < 10.8:
            return "Brisa forte"
        elif v < 13.9:
            return "Vento fresco"
        elif v < 17.2:
            return "Vento forte"
        elif v < 20.8:
            return "Ventania"
        elif v < 24.5:
            return "Ventania forte"
        elif v < 28.5:
            return "Tempestade"
        elif v < 32.7:
            return "Tempestade violenta"
        else:
            return "Furacão"
    
    def eh_viavel_para_turbina(self, velocidade_cut_in: float = 2.5,
                              velocidade_cut_out: float = 25.0) -> bool:
        """
        Verifica se a velocidade do vento é viável para operação de turbina.
        
        Args:
            velocidade_cut_in: Velocidade mínima de operação (m/s)
            velocidade_cut_out: Velocidade máxima de operação (m/s)
        
        Returns:
            True se viável para operação
        """
        return velocidade_cut_in <= self.velocidade_vento <= velocidade_cut_out
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário."""
        base_dict = super().to_dict()
        base_dict.update({
            'velocidade_vento': self.velocidade_vento,
            'direcao_vento': self.direcao_vento,
            'velocidade_vento_max': self.velocidade_vento_max,
            'rajada_vento': self.rajada_vento
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DadosEolicos':
        """Cria uma instância a partir de dicionário."""
        data_copy = data.copy()
        data_copy['data'] = datetime.fromisoformat(data_copy['data'])
        return cls(**data_copy)


@dataclass
class LocalizacaoClimatica:
    """
    Entidade para localização com metadados climáticos.
    
    Representa uma localização geográfica com informações
    específicas para análise climática e eólica.
    """
    nome: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    tipo_terreno: Optional[str] = None
    rugosidade: Optional[float] = None
    fuso_horario: str = "America/Sao_Paulo"
    
    def __post_init__(self):
        """Validação após inicialização."""
        self._validar_localizacao()
    
    def _validar_localizacao(self):
        """Valida os dados da localização."""
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da localização não pode ser vazio")
        
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude deve estar entre -90 e 90 graus")
        
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude deve estar entre -180 e 180 graus")
        
        if self.altitude is not None and self.altitude < -500:
            raise ValueError("Altitude muito baixa")
        
        if self.rugosidade is not None and not (0 <= self.rugosidade <= 4):
            raise ValueError("Rugosidade deve estar entre 0 e 4")
    
    def calcular_fator_altura(self, altura_turbina: float, 
                             altura_referencia: float = 10.0,
                             alpha: Optional[float] = None) -> float:
        """
        Calcula o fator de correção de velocidade por altura.
        
        Args:
            altura_turbina: Altura da turbina em metros
            altura_referencia: Altura de referência em metros
            alpha: Expoente de rugosidade (calculado automaticamente se None)
        
        Returns:
            Fator de correção
        """
        if alpha is None:
            # Estima alpha baseado no tipo de terreno
            alpha_terreno = {
                'mar': 0.10,
                'campo_aberto': 0.15,
                'rural': 0.20,
                'suburbano': 0.30,
                'urbano': 0.40
            }
            alpha = alpha_terreno.get(self.tipo_terreno, 0.15)
        
        return (altura_turbina / altura_referencia) ** alpha
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário."""
        return {
            'nome': self.nome,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'tipo_terreno': self.tipo_terreno,
            'rugosidade': self.rugosidade,
            'fuso_horario': self.fuso_horario
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocalizacaoClimatica':
        """Cria uma instância a partir de dicionário."""
        return cls(**data)


@dataclass
class SerieTemporalVento:
    """
    Entidade para série temporal de dados de vento.
    
    Representa uma coleção de dados eólicos ao longo do tempo
    para análise estatística e de tendências.
    """
    localizacao: LocalizacaoClimatica
    dados: List[DadosEolicos]
    periodo_inicio: datetime
    periodo_fim: datetime
    
    def __post_init__(self):
        """Validação após inicialização."""
        self._validar_serie_temporal()
    
    def _validar_serie_temporal(self):
        """Valida a série temporal."""
        if not self.dados:
            raise ValueError("Lista de dados não pode ser vazia")
        
        if self.periodo_inicio >= self.periodo_fim:
            raise ValueError("Período de início deve ser anterior ao fim")
        
        # Verifica se todos os dados são da mesma localização
        for dado in self.dados:
            if (abs(dado.latitude - self.localizacao.latitude) > 0.01 or
                abs(dado.longitude - self.localizacao.longitude) > 0.01):
                raise ValueError("Dados contêm localizações diferentes")
    
    def calcular_estatisticas(self) -> Dict[str, float]:
        """
        Calcula estatísticas básicas da série temporal.
        
        Returns:
            Dicionário com estatísticas
        """
        velocidades = [d.velocidade_vento for d in self.dados]
        
        if not velocidades:
            return {}
        
        velocidades_sorted = sorted(velocidades)
        n = len(velocidades)
        
        return {
            'media': sum(velocidades) / n,
            'mediana': velocidades_sorted[n // 2],
            'minimo': min(velocidades),
            'maximo': max(velocidades),
            'desvio_padrao': self._calcular_desvio_padrao(velocidades),
            'percentil_90': velocidades_sorted[int(0.9 * n)],
            'dias_viaveis': sum(1 for d in self.dados if d.eh_viavel_para_turbina())
        }
    
    def _calcular_desvio_padrao(self, valores: List[float]) -> float:
        """Calcula o desvio padrão dos valores."""
        if not valores:
            return 0.0
        
        media = sum(valores) / len(valores)
        variancia = sum((v - media) ** 2 for v in valores) / len(valores)
        return variancia ** 0.5
    
    def calcular_potencial_eolico_anual(self, area_varredura: float) -> float:
        """
        Calcula o potencial eólico anual total.
        
        Args:
            area_varredura: Área varrida pelas pás em m²
        
        Returns:
            Energia anual em kWh
        """
        energia_total = 0.0
        
        for dado in self.dados:
            potencia_watts = dado.calcular_potencia_vento(area_varredura)
            energia_diaria_kwh = (potencia_watts * 24) / 1000  # Conversão para kWh
            energia_total += energia_diaria_kwh
        
        # Projeta para um ano completo se necessário
        dias_na_serie = len(self.dados)
        if dias_na_serie > 0:
            energia_anual = (energia_total * 365) / dias_na_serie
        else:
            energia_anual = 0.0
        
        return energia_anual
    
    def filtrar_por_periodo(self, inicio: datetime, fim: datetime) -> 'SerieTemporalVento':
        """
        Filtra a série temporal por período específico.
        
        Args:
            inicio: Data de início do filtro
            fim: Data de fim do filtro
        
        Returns:
            Nova série temporal filtrada
        """
        dados_filtrados = [
            d for d in self.dados 
            if inicio <= d.data <= fim
        ]
        
        return SerieTemporalVento(
            localizacao=self.localizacao,
            dados=dados_filtrados,
            periodo_inicio=inicio,
            periodo_fim=fim
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário."""
        return {
            'localizacao': self.localizacao.to_dict(),
            'dados': [d.to_dict() for d in self.dados],
            'periodo_inicio': self.periodo_inicio.isoformat(),
            'periodo_fim': self.periodo_fim.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerieTemporalVento':
        """Cria uma instância a partir de dicionário."""
        localizacao = LocalizacaoClimatica.from_dict(data['localizacao'])
        dados = [DadosEolicos.from_dict(d) for d in data['dados']]
        periodo_inicio = datetime.fromisoformat(data['periodo_inicio'])
        periodo_fim = datetime.fromisoformat(data['periodo_fim'])
        
        return cls(
            localizacao=localizacao,
            dados=dados,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim
        )
