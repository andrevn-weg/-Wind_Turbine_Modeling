"""
Subpáginas de cadastro geográfico

Este módulo contém as subpáginas para cadastro de:
- Países (create_pais.py)
- Estados/Regiões (create_estado.py)  
- Cidades (create_cidade.py)

Cada subpágina é independente e pode ser chamada pela página principal
de cadastro de localidades.
"""

from .create_pais import create_pais
from .create_estado import create_estado
from .create_cidade import create_cidade

__all__ = ['create_pais', 'create_estado', 'create_cidade']
