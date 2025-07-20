from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class MeteorologicalData:
    """
    Entidade de domínio para representar dados meteorológicos coletados.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    Armazena dados como velocidade do vento, temperatura, umidade, etc.
    
    Attributes:
        id (Optional[int]): Identificador único do registro no banco de dados
        meteorological_data_source_id (int): Referência à fonte dos dados (chave estrangeira)
        cidade_id (int): Referência à cidade onde foi coletado o dado (chave estrangeira)
        data (date): Data da medição meteorológica
        altura_captura (Optional[float]): Altura em metros onde foi realizada a captura do vento
        velocidade_vento (Optional[float]): Velocidade do vento em m/s
        temperatura (Optional[float]): Temperatura em graus Celsius
        umidade (Optional[float]): Umidade relativa do ar em percentual
        created_at (Optional[datetime]): Timestamp de criação do registro
    """
    id: Optional[int] = None
    meteorological_data_source_id: int = 0
    cidade_id: int = 0
    data: Optional[date] = None
    altura_captura: Optional[float] = None
    velocidade_vento: Optional[float] = None
    temperatura: Optional[float] = None
    umidade: Optional[float] = None
    created_at: Optional[datetime] = None
    
    def validar(self) -> bool:
        """
        Valida se os dados meteorológicos estão corretos.
        
        Returns:
            bool: True se válido, False caso contrário
        """
        # IDs obrigatórios
        if not self.meteorological_data_source_id or self.meteorological_data_source_id <= 0:
            return False
        if not self.cidade_id or self.cidade_id <= 0:
            return False
        
        # Data é obrigatória
        if not self.data:
            return False
        
        # Validações de dados meteorológicos opcionais, mas se fornecidos devem ser válidos
        if self.altura_captura is not None and self.altura_captura < 0:
            return False
        
        if self.velocidade_vento is not None and self.velocidade_vento < 0:
            return False
        
        if self.temperatura is not None and (self.temperatura < -100 or self.temperatura > 60):
            return False
        
        if self.umidade is not None and (self.umidade < 0 or self.umidade > 100):
            return False
            
        return True
    
    def tem_dados_vento(self) -> bool:
        """
        Verifica se o registro possui dados de vento.
        
        Returns:
            bool: True se possui dados de vento válidos
        """
        return (self.velocidade_vento is not None and self.velocidade_vento >= 0)
    
    def tem_dados_temperatura(self) -> bool:
        """
        Verifica se o registro possui dados de temperatura.
        
        Returns:
            bool: True se possui dados de temperatura válidos
        """
        return (self.temperatura is not None)
    
    def tem_dados_umidade(self) -> bool:
        """
        Verifica se o registro possui dados de umidade.
        
        Returns:
            bool: True se possui dados de umidade válidos
        """
        return (self.umidade is not None and 0 <= self.umidade <= 100)
    
    def classificar_vento(self) -> str:
        """
        Classifica a velocidade do vento segundo a escala de Beaufort.
        
        Returns:
            str: Classificação do vento
        """
        if not self.tem_dados_vento():
            return "Dados não disponíveis"
        
        v = self.velocidade_vento
        if v < 0.3:
            return "Calmo"
        elif v < 1.6:
            return "Brisa leve"
        elif v < 3.4:
            return "Brisa fraca"
        elif v < 5.5:
            return "Brisa moderada"
        elif v < 8.0:
            return "Brisa forte"
        elif v < 10.8:
            return "Vento fresco"
        elif v < 13.9:
            return "Vento forte"
        elif v < 17.2:
            return "Ventania moderada"
        elif v < 20.8:
            return "Ventania forte"
        elif v < 24.5:
            return "Ventania"
        elif v < 28.5:
            return "Tempestade"
        else:
            return "Tempestade violenta"
    
    def to_dict(self) -> dict:
        """
        Converte a entidade para dicionário.
        
        Returns:
            dict: Representação em dicionário dos dados meteorológicos
        """
        return {
            'id': self.id,
            'meteorological_data_source_id': self.meteorological_data_source_id,
            'cidade_id': self.cidade_id,
            'data': self.data.isoformat() if self.data else None,
            'altura_captura': self.altura_captura,
            'velocidade_vento': self.velocidade_vento,
            'temperatura': self.temperatura,
            'umidade': self.umidade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'classificacao_vento': self.classificar_vento()
        }
    
    def __str__(self) -> str:
        """
        Representação em string dos dados meteorológicos.
        
        Returns:
            str: String descritiva dos dados
        """
        componentes = []
        if self.tem_dados_vento():
            componentes.append(f"Vento: {self.velocidade_vento}m/s")
        if self.tem_dados_temperatura():
            componentes.append(f"Temp: {self.temperatura}°C")
        if self.tem_dados_umidade():
            componentes.append(f"Umidade: {self.umidade}%")
        
        dados_str = " | ".join(componentes) if componentes else "Sem dados"
        return f"[{self.data}] {dados_str}"
    
    def __repr__(self) -> str:
        """
        Representação técnica dos dados meteorológicos.
        
        Returns:
            str: String técnica dos dados
        """
        return (f"MeteorologicalData(id={self.id}, fonte_id={self.meteorological_data_source_id}, "
                f"cidade_id={self.cidade_id}, data={self.data}, vento={self.velocidade_vento})")
