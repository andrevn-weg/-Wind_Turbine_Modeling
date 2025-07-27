"""
Módulo aerogenerators - Gerenciamento de entidades Aerogerador

Este módulo contém:
- Aerogenerator: Entidade de domínio representando um aerogerador completo
- AerogeneratorRepository: Classe responsável pela persistência de dados

Exemplo de uso:
    from src.turbine_parameters.aerogenerators import Aerogenerator, AerogeneratorRepository
    from decimal import Decimal
    
    # Criar um novo aerogerador
    aerogenerator = Aerogenerator(
        model_code="V90-2.0MW",
        manufacturer_id=1,  # ID do fabricante Vestas
        model="V90-2.0MW",
        manufacture_year=2020,
        rated_power_kw=Decimal('2000'),
        rated_voltage_kv=Decimal('0.69'),
        cut_in_speed=Decimal('4'),
        cut_out_speed=Decimal('25'),
        rotor_diameter_m=Decimal('90'),
        turbine_type_id=1,  # Horizontal
        generator_type_id=1,  # PMSG
        control_type_id=1   # Pitch
    )
    
    # Salvar no banco
    repo = AerogeneratorRepository()
    repo.criar_tabela()  # Cria tabela se não existir
    aerogenerator_id = repo.salvar(aerogenerator)
    
    # Buscar aerogerador
    aerogenerator_encontrado = repo.buscar_por_model_code("V90-2.0MW")
"""

from .entity import Aerogenerator
from .repository import AerogeneratorRepository

__all__ = ['Aerogenerator', 'AerogeneratorRepository']
