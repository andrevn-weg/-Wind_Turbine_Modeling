"""
Módulo de subpáginas para gerenciamento de parâmetros de turbinas eólicas

Este módulo contém todas as subpáginas CRUD para:
- Manufacturers (Fabricantes)
- Turbine Types (Tipos de Turbina)
- Generator Types (Tipos de Gerador)
- Control Types (Tipos de Controle)
- Aerogenerators (Aerogeradores)

Estrutura organizada seguindo o padrão do projeto.
"""

# Este arquivo será usado para imports futuros quando necessário
# Por enquanto, os imports são feitos diretamente nas páginas principais

__all__ = [
    # Manufacturers
    'create_manufacturer', 'read_manufacturer', 'update_manufacturer', 'delete_manufacturer',
    # Turbine Types
    'create_turbine_type', 'read_turbine_type', 'update_turbine_type', 'delete_turbine_type',
    # Generator Types
    'create_generator_type', 'read_generator_type', 'update_generator_type', 'delete_generator_type',
    # Control Types
    'create_control_type', 'read_control_type', 'update_control_type', 'delete_control_type',
    # Aerogenerators
    'create_aerogenerator', 'read_aerogenerator', 'update_aerogenerator', 'delete_aerogenerator'
]
