from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Cidade:
    """
    Entidade de domínio para representar uma cidade/localidade com suas coordenadas geográficas.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único da cidade no banco de dados
        nome (str): Nome da cidade/localidade
        regiao_id (Optional[int]): Referência à região/estado (chave estrangeira)
        pais_id (Optional[int]): Referência direta ao país (chave estrangeira)
        latitude (float): Latitude geográfica
        longitude (float): Longitude geográfica
        populacao (Optional[int]): População estimada da cidade
        altitude (Optional[float]): Altitude média em metros
        notes (Optional[str]): Notas adicionais sobre a cidade/localidade
    """
    id: Optional[int] = None
    nome: str = ""
    regiao_id: Optional[int] = None
    pais_id: Optional[int] = None
    latitude: float = 0.0
    longitude: float = 0.0
    populacao: Optional[int] = None
    altitude: Optional[float] = None
    notes: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Cidade(id={self.id}, nome={self.nome}, lat={self.latitude}, long={self.longitude})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância em um dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "regiao_id": self.regiao_id,
            "pais_id": self.pais_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "populacao": self.populacao,
            "altitude": self.altitude,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cidade':
        """Cria uma instância de Cidade a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            regiao_id=data.get("regiao_id"),
            pais_id=data.get("pais_id"),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            populacao=data.get("populacao"),
            altitude=data.get("altitude"),
            notes=data.get("notes")
        )
        
    def validar(self) -> bool:
        """
        Valida se a cidade possui os dados mínimos necessários.
        
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        if not self.nome or not self.nome.strip():
            return False
        if self.latitude < -90 or self.latitude > 90:
            return False
        if self.longitude < -180 or self.longitude > 180:
            return False
        return True
    
    def distancia_aproximada(self, outra_cidade: 'Cidade') -> float:
        """
        Calcula a distância aproximada entre duas cidades em quilômetros.
        Usa a fórmula de distância euclidiana simples (não é geodésica).
        
        Args:
            outra_cidade: Outra instância de Cidade
            
        Returns:
            float: Distância aproximada em quilômetros
        """
        from math import sqrt
        
        # 1 grau de latitude ≈ 111 km
        # 1 grau de longitude varia com a latitude
        lat_diff = abs(self.latitude - outra_cidade.latitude) * 111
        lon_diff = abs(self.longitude - outra_cidade.longitude) * 111
        
        return sqrt(lat_diff**2 + lon_diff**2)
