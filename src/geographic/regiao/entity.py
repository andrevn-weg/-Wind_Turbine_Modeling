from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Regiao:
    """
    Entidade de domínio para representar regiões/estados.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    
    Attributes:
        id (Optional[int]): Identificador único da região
        nome (str): Nome da região ou estado
        pais_id (Optional[int]): Referência ao país (chave estrangeira)
        sigla (Optional[str]): Sigla ou abreviação da região (ex: "SC", "SP")
    """
    id: Optional[int] = None
    nome: str = ""
    pais_id: Optional[int] = None
    sigla: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Regiao(id={self.id}, nome={self.nome}, sigla={self.sigla})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância em um dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "pais_id": self.pais_id,
            "sigla": self.sigla
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Regiao':
        """Cria uma instância de Região a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            pais_id=data.get("pais_id"),
            sigla=data.get("sigla")
        )
    
    def validar(self) -> bool:
        """
        Valida se a região possui os dados mínimos necessários.
        
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        if not self.nome or not self.nome.strip():
            return False
        if self.pais_id is not None and self.pais_id <= 0:
            return False
        return True
    
    def formatar_sigla(self) -> str:
        """
        Formata a sigla da região em maiúsculas.
        
        Returns:
            str: Sigla da região em maiúsculas
        """
        return self.sigla.upper() if self.sigla else ""
    
    def nome_completo(self) -> str:
        """
        Retorna o nome completo da região com sigla, se disponível.
        
        Returns:
            str: Nome completo no formato "Nome (SIGLA)" ou apenas "Nome"
        """
        if self.sigla:
            return f"{self.nome} ({self.formatar_sigla()})"
        return self.nome
