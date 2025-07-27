from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ControlType:
    """
    Entidade de domínio para representar um tipo de controle de turbina eólica.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único do tipo de controle no banco de dados
        type (str): Tipo do controle ('Pitch', 'Stall', 'Active Stall')
        description (Optional[str]): Descrição detalhada do tipo de controle
    """
    id: Optional[int] = None
    type: str = ""
    description: Optional[str] = None

    def __post_init__(self):
        """Validações após a inicialização do objeto"""
        self._validar()
    
    def _validar(self) -> None:
        """
        Valida os dados da entidade ControlType.
        
        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        if not self.type or not self.type.strip():
            raise ValueError("Tipo de controle é obrigatório")
        
        if len(self.type.strip()) > 100:
            raise ValueError("Tipo de controle não pode exceder 100 caracteres")
        
        if self.description and len(self.description.strip()) > 1000:
            raise ValueError("Descrição não pode exceder 1000 caracteres")
        
        # Validar tipos conhecidos
        tipos_validos = ['Pitch', 'Stall', 'Active Stall']
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ControlType':
        """
        Cria uma instância da entidade a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da entidade
            
        Returns:
            ControlType: Nova instância da entidade
        """
        return cls(
            id=data.get('id'),
            type=data.get('type', ''),
            description=data.get('description')
        )
    
    def is_pitch(self) -> bool:
        """
        Verifica se o tipo é pitch control.
        
        Returns:
            bool: True se for pitch control, False caso contrário
        """
        return self.type == 'Pitch'
    
    def is_stall(self) -> bool:
        """
        Verifica se o tipo é stall control.
        
        Returns:
            bool: True se for stall control, False caso contrário
        """
        return self.type == 'Stall'
    
    def is_active_stall(self) -> bool:
        """
        Verifica se o tipo é active stall control.
        
        Returns:
            bool: True se for active stall control, False caso contrário
        """
        return self.type == 'Active Stall'
    
    def get_control_mechanism(self) -> str:
        """
        Retorna o mecanismo de controle detalhado.
        
        Returns:
            str: Descrição do mecanismo de controle
        """
        mechanisms = {
            'Pitch': 'Controle através do ângulo das pás (pitch angle)',
            'Stall': 'Controle passivo através do stall aerodinâmico',
            'Active Stall': 'Controle ativo do stall através do ângulo das pás'
        }
        return mechanisms.get(self.type, self.type)
    
    def requires_pitch_actuators(self) -> bool:
        """
        Verifica se o tipo de controle requer atuadores de pitch.
        
        Returns:
            bool: True se requer atuadores de pitch, False caso contrário
        """
        return self.type in ['Pitch', 'Active Stall']
    
    def is_passive_control(self) -> bool:
        """
        Verifica se é um controle passivo.
        
        Returns:
            bool: True se for controle passivo, False caso contrário
        """
        return self.type == 'Stall'
    
    def __str__(self) -> str:
        """Representação textual da entidade"""
        return f"ControlType(id={self.id}, type='{self.type}')"
    
    def __repr__(self) -> str:
        """Representação detalhada da entidade"""
        return (f"ControlType(id={self.id}, type='{self.type}', "
                f"description='{self.description}')")
