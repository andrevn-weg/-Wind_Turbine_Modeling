from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TurbineType:
    """
    Entidade de domínio para representar um tipo de turbina eólica.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único do tipo de turbina no banco de dados
        type (str): Tipo da turbina ('Horizontal', 'Vertical')
        description (Optional[str]): Descrição detalhada do tipo de turbina
    """
    id: Optional[int] = None
    type: str = ""
    description: Optional[str] = None

    def __post_init__(self):
        """Validações após a inicialização do objeto"""
        self._validar()
    
    def _validar(self) -> None:
        """
        Valida os dados da entidade TurbineType.
        
        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        if not self.type or not self.type.strip():
            raise ValueError("Tipo de turbina é obrigatório")
        
        if len(self.type.strip()) > 100:
            raise ValueError("Tipo de turbina não pode exceder 100 caracteres")
        
        if self.description and len(self.description.strip()) > 1000:
            raise ValueError("Descrição não pode exceder 1000 caracteres")
        
        # Validar tipos conhecidos
        tipos_validos = ['Horizontal', 'Vertical']
        if self.type.strip() not in tipos_validos:
            raise ValueError(f"Tipo deve ser um dos seguintes: {', '.join(tipos_validos)}")
        
        # Normalizar campos
        self.type = self.type.strip()
        if self.description:
            self.description = self.description.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            Dict[str, Any]: Representação da entidade em formato de dicionário
        """
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TurbineType':
        """
        Cria uma instância da entidade a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da entidade
            
        Returns:
            TurbineType: Nova instância da entidade
        """
        return cls(
            id=data.get('id'),
            type=data.get('type', ''),
            description=data.get('description')
        )
    
    def is_horizontal(self) -> bool:
        """
        Verifica se o tipo é horizontal.
        
        Returns:
            bool: True se for horizontal, False caso contrário
        """
        return self.type == 'Horizontal'
    
    def is_vertical(self) -> bool:
        """
        Verifica se o tipo é vertical.
        
        Returns:
            bool: True se for vertical, False caso contrário
        """
        return self.type == 'Vertical'
    
    def __str__(self) -> str:
        """Representação textual da entidade"""
        return f"TurbineType(id={self.id}, type='{self.type}')"
    
    def __repr__(self) -> str:
        """Representação detalhada da entidade"""
        return (f"TurbineType(id={self.id}, type='{self.type}', "
                f"description='{self.description}')")
