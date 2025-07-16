"""
Módulo cidade - Gerenciamento de entidades Cidade

Este módulo contém:
- Cidade: Entidade de domínio representando uma cidade/localidade
- CidadeRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.geographic.cidade import Cidade, CidadeRepository
    
    # Criar uma nova cidade
    cidade = Cidade(
        nome="São Paulo",
        latitude=-23.5505,
        longitude=-46.6333,
        populacao=12_000_000
    )
    
    # Salvar no banco
    repo = CidadeRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    cidade_id = repo.salvar(cidade)
    
    # Buscar cidade
    cidade_encontrada = repo.buscar_por_id(cidade_id)
"""

from .entity import Cidade
from .repository import CidadeRepository

__all__ = ['Cidade', 'CidadeRepository']
