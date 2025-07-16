from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Pais:
    """
    Entidade de domínio para representar países.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único do país
        nome (str): Nome do país
        codigo (str): Código ISO do país (ex: "BR", "US")
    """
    id: Optional[int] = None
    nome: str = ""
    codigo: str = ""
    
    def __repr__(self) -> str:
        return f"Pais(id={self.id}, nome={self.nome}, codigo={self.codigo})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância em um dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pais':
        """Cria uma instância de País a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            codigo=data.get("codigo", "")
        )
    
    def validar(self) -> bool:
        """
        Valida se o país possui os dados mínimos necessários.
        
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        if not self.nome or not self.nome.strip():
            return False
        if not self.codigo or not self.codigo.strip():
            return False
        if len(self.codigo) != 2:  # Código ISO deve ter 2 caracteres
            return False
        return True
    
    def formatar_codigo(self) -> str:
        """
        Formata o código do país em maiúsculas.
        
        Returns:
            str: Código do país em maiúsculas
        """
        return self.codigo.upper() if self.codigo else ""
