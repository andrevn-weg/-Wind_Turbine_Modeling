"""
Módulo Geographic - Sistema de Gerenciamento Geográfico

Este módulo contém as entidades e repositórios para gerenciamento de dados geográficos:

Entidades:
- Pais: Representa países com código ISO
- Regiao: Representa regiões/estados dentro de países  
- Cidade: Representa cidades/localidades com coordenadas geográficas

Repositórios:
- PaisRepository: Persistência de dados de países
- RegiaoRepository: Persistência de dados de regiões
- CidadeRepository: Persistência de dados de cidades

Exemplo de uso:
    from src.geographic import Pais, Regiao, Cidade
    from src.geographic import PaisRepository, RegiaoRepository, CidadeRepository
    
    # Ou imports específicos:
    from src.geographic.pais import Pais, PaisRepository
    from src.geographic.regiao import Regiao, RegiaoRepository
    from src.geographic.cidade import Cidade, CidadeRepository
"""

# Imports das entidades
from .pais import Pais, PaisRepository
from .regiao import Regiao, RegiaoRepository
from .cidade import Cidade, CidadeRepository

# Definir o que é exportado quando alguém faz "from src.geographic import *"
__all__ = [
    # Entidades
    'Pais',
    'Regiao', 
    'Cidade',
    # Repositórios
    'PaisRepository',
    'RegiaoRepository',
    'CidadeRepository'
]
