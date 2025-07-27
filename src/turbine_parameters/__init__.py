"""
Módulo Turbine Parameters - Sistema de Simulação de Turbinas Eólicas

Este módulo contém as entidades e repositórios para gerenciamento de parâmetros de turbinas eólicas:

Entidades:
- Manufacturer: Representa fabricantes de turbinas eólicas
- TurbineType: Representa tipos de turbinas (Horizontal, Vertical)
- GeneratorType: Representa tipos de geradores (Synchronous, Asynchronous, PMSG, DFIG)
- ControlType: Representa tipos de controle (Pitch, Stall, Active Stall)
- Aerogenerator: Representa aerogeradores completos com especificações técnicas

Repositórios:
- ManufacturerRepository: Persistência de dados de fabricantes
- TurbineTypeRepository: Persistência de dados de tipos de turbinas
- GeneratorTypeRepository: Persistência de dados de tipos de geradores
- ControlTypeRepository: Persistência de dados de tipos de controle
- AerogeneratorRepository: Persistência de dados de aerogeradores

Exemplo de uso:
    from src.turbine_parameters import Manufacturer, TurbineType, GeneratorType
    from src.turbine_parameters import ManufacturerRepository, TurbineTypeRepository
    
    # Ou imports específicos:
    from src.turbine_parameters.manufacturers import Manufacturer, ManufacturerRepository
    from src.turbine_parameters.aerogenerators import Aerogenerator, AerogeneratorRepository
"""

# Imports das entidades
from .manufacturers import Manufacturer, ManufacturerRepository
from .turbine_types import TurbineType, TurbineTypeRepository
from .generator_types import GeneratorType, GeneratorTypeRepository
from .control_types import ControlType, ControlTypeRepository
from .aerogenerators import Aerogenerator, AerogeneratorRepository

# Definir o que é exportado quando alguém faz "from src.turbine_parameters import *"
__all__ = [
    # Entidades
    'Manufacturer',
    'TurbineType', 
    'GeneratorType',
    'ControlType',
    'Aerogenerator',
    # Repositórios
    'ManufacturerRepository',
    'TurbineTypeRepository',
    'GeneratorTypeRepository',
    'ControlTypeRepository',
    'AerogeneratorRepository'
]
