from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class GeneratorType:
    """
    Entidade de domínio para representar um tipo de gerador eólico.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único do tipo de gerador no banco de dados
        type (str): Tipo do gerador ('Synchronous', 'Asynchronous', 'PMSG', 'DFIG')
        description (Optional[str]): Descrição detalhada do tipo de gerador
    """
    id: Optional[int] = None
    type: str = ""
    description: Optional[str] = None

    def __post_init__(self):
        """Validações após a inicialização do objeto"""
        self._validar()
    
    def _validar(self) -> None:
        """
        Valida os dados da entidade GeneratorType.
        
        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        if not self.type or not self.type.strip():
            raise ValueError("Tipo de gerador é obrigatório")
        
        if len(self.type.strip()) > 100:
            raise ValueError("Tipo de gerador não pode exceder 100 caracteres")
        
        if self.description and len(self.description.strip()) > 1000:
            raise ValueError("Descrição não pode exceder 1000 caracteres")
        
        # Validar tipos conhecidos
        tipos_validos = ['Synchronous', 'Asynchronous', 'PMSG', 'DFIG']
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
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratorType':
        """
        Cria uma instância da entidade a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da entidade
            
        Returns:
            GeneratorType: Nova instância da entidade
        """
        return cls(
            id=data.get('id'),
            type=data.get('type', ''),
            description=data.get('description')
        )
    
    def is_synchronous(self) -> bool:
        """
        Verifica se o tipo é síncrono.
        
        Returns:
            bool: True se for síncrono, False caso contrário
        """
        return self.type == 'Synchronous'
    
    def is_asynchronous(self) -> bool:
        """
        Verifica se o tipo é assíncrono.
        
        Returns:
            bool: True se for assíncrono, False caso contrário
        """
        return self.type == 'Asynchronous'
    
    def is_pmsg(self) -> bool:
        """
        Verifica se o tipo é PMSG (Permanent Magnet Synchronous Generator).
        
        Returns:
            bool: True se for PMSG, False caso contrário
        """
        return self.type == 'PMSG'
    
    def is_dfig(self) -> bool:
        """
        Verifica se o tipo é DFIG (Doubly Fed Induction Generator).
        
        Returns:
            bool: True se for DFIG, False caso contrário
        """
        return self.type == 'DFIG'
    
    def get_full_name(self) -> str:
        """
        Retorna o nome completo do tipo de gerador.
        
        Returns:
            str: Nome completo do tipo de gerador
        """
        full_names = {
            'Synchronous': 'Synchronous Generator',
            'Asynchronous': 'Asynchronous Generator',
            'PMSG': 'Permanent Magnet Synchronous Generator',
            'DFIG': 'Doubly Fed Induction Generator'
        }
        return full_names.get(self.type, self.type)
    
    def __str__(self) -> str:
        """Representação textual da entidade"""
        return f"GeneratorType(id={self.id}, type='{self.type}')"
    
    def __repr__(self) -> str:
        """Representação detalhada da entidade"""
        return (f"GeneratorType(id={self.id}, type='{self.type}', "
                f"description='{self.description}')")
