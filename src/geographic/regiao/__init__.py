"""
Módulo regiao - Gerenciamento de entidades Região

Este módulo contém:
- Regiao: Entidade de domínio representando uma região/estado
- RegiaoRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.geographic.regiao import Regiao, RegiaoRepository
    
    # Criar uma nova região
    regiao = Regiao(
        nome="Santa Catarina",
        pais_id=1,  # ID do Brasil
        sigla="SC"
    )
    
    # Salvar no banco
    repo = RegiaoRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    regiao_id = repo.salvar(regiao)
    
    # Buscar regiões do país
    regioes_brasil = repo.buscar_por_pais(1)
"""

from .entity import Regiao
from .repository import RegiaoRepository

__all__ = ['Regiao', 'RegiaoRepository']
