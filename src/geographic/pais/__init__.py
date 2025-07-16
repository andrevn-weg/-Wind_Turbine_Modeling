"""
Módulo pais - Gerenciamento de entidades País

Este módulo contém:
- Pais: Entidade de domínio representando um país
- PaisRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.geographic.pais import Pais, PaisRepository
    
    # Criar um novo país
    pais = Pais(
        nome="Brasil",
        codigo="BR"
    )
    
    # Salvar no banco
    repo = PaisRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    pais_id = repo.salvar(pais)
    
    # Buscar país
    pais_encontrado = repo.buscar_por_codigo("BR")
"""

from .entity import Pais
from .repository import PaisRepository

__all__ = ['Pais', 'PaisRepository']
