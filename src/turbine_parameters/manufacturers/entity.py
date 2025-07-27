from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Manufacturer:
    """
    Entidade de domínio para representar um fabricante de turbinas eólicas.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único do fabricante no banco de dados
        name (str): Nome do fabricante
        country (Optional[str]): País de origem do fabricante
        official_website (Optional[str]): Website oficial do fabricante
        created_at (Optional[datetime]): Data de criação do registro
        updated_at (Optional[datetime]): Data da última atualização do registro
    """
    id: Optional[int] = None
    name: str = ""
    country: Optional[str] = None
    official_website: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validações após a inicialização do objeto"""
        self._validar()
    
    def _validar(self) -> None:
        """
        Valida os dados da entidade Manufacturer.
        
        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        if not self.name or not self.name.strip():
            raise ValueError("Nome do fabricante é obrigatório")
        
        if len(self.name.strip()) > 255:
            raise ValueError("Nome do fabricante não pode exceder 255 caracteres")
        
        if self.country and len(self.country.strip()) > 100:
            raise ValueError("País não pode exceder 100 caracteres")
        
        if self.official_website and len(self.official_website.strip()) > 500:
            raise ValueError("Website oficial não pode exceder 500 caracteres")
        
        # Normalizar campos
        self.name = self.name.strip()
        if self.country:
            self.country = self.country.strip()
        if self.official_website:
            self.official_website = self.official_website.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            Dict[str, Any]: Representação da entidade em formato de dicionário
        """
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'official_website': self.official_website,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Manufacturer':
        """
        Cria uma instância da entidade a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da entidade
            
        Returns:
            Manufacturer: Nova instância da entidade
        """
        # Converter strings de datetime se necessário
        created_at = None
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'])
            else:
                created_at = data['created_at']
        
        updated_at = None
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'])
            else:
                updated_at = data['updated_at']
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            country=data.get('country'),
            official_website=data.get('official_website'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def __str__(self) -> str:
        """Representação textual da entidade"""
        return f"Manufacturer(id={self.id}, name='{self.name}', country='{self.country}')"
    
    def __repr__(self) -> str:
        """Representação detalhada da entidade"""
        return (f"Manufacturer(id={self.id}, name='{self.name}', "
                f"country='{self.country}', official_website='{self.official_website}')")
