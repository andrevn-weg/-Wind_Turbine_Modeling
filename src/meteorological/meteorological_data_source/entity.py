from dataclasses import dataclass
from typing import Optional


@dataclass
class MeteorologicalDataSource:
    """
    Entidade de domínio para representar uma fonte de dados meteorológicos.
    
    Esta classe representa apenas o objeto de negócio, sem responsabilidades de persistência.
    Exemplos de fontes: NASA_POWER, OpenWeatherMap, INMET, etc.
    
    Attributes:
        id (Optional[int]): Identificador único da fonte no banco de dados
        name (str): Nome da fonte de dados meteorológicos
        description (Optional[str]): Descrição detalhada da fonte e seus dados
    """
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    
    def validar(self) -> bool:
        """
        Valida se os dados da fonte de dados meteorológicos estão corretos.
        
        Returns:
            bool: True se válido, False caso contrário
        """
        # Nome é obrigatório e deve ter pelo menos 2 caracteres
        if not self.name or len(self.name.strip()) < 2:
            return False
        
        # Evitar nomes duplicados ou muito genéricos
        nomes_invalidos = ["", "null", "none", "test", "teste"]
        if self.name.lower().strip() in nomes_invalidos:
            return False
            
        return True
    
    def formatar_nome(self) -> str:
        """
        Formatar o nome da fonte de dados para padronização.
        
        Returns:
            str: Nome formatado
        """
        if not self.name:
            return ""
        return self.name.strip().upper()
    
    def to_dict(self) -> dict:
        """
        Converte a entidade para dicionário.
        
        Returns:
            dict: Representação em dicionário da fonte
        """
        return {
            'id': self.id,
            'name': self.formatar_nome(),
            'description': self.description
        }
    
    def __str__(self) -> str:
        """
        Representação em string da fonte de dados.
        
        Returns:
            str: String descritiva da fonte
        """
        desc = f" - {self.description}" if self.description else ""
        return f"{self.formatar_nome()}{desc}"
    
    def __repr__(self) -> str:
        """
        Representação técnica da fonte de dados.
        
        Returns:
            str: String técnica da fonte
        """
        return f"MeteorologicalDataSource(id={self.id}, name='{self.name}', description='{self.description}')"
