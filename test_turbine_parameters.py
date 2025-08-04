#!/usr/bin/env python3
"""
Script de teste para verificar se todas as tabelas dos parâmetros de turbina são criadas corretamente
"""

import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from turbine_parameters import (
    ManufacturerRepository,
    TurbineTypeRepository, 
    GeneratorTypeRepository,
    ControlTypeRepository,
    AerogeneratorRepository
)

def test_tables():
    """Teste das tabelas dos parâmetros de turbina"""
    print("🔧 Testando criação das tabelas...")
    
    try:
        # Manufacturers
        print("📋 Criando tabela manufacturers...")
        manufacturer_repo = ManufacturerRepository()
        manufacturer_repo.criar_tabela()
        print("✅ Tabela manufacturers criada com sucesso!")
        
        # Turbine Types
        print("📋 Criando tabela turbine_types...")
        turbine_type_repo = TurbineTypeRepository()
        turbine_type_repo.criar_tabela()
        print("✅ Tabela turbine_types criada com sucesso!")
        
        # Generator Types
        print("📋 Criando tabela generator_types...")
        generator_type_repo = GeneratorTypeRepository()
        generator_type_repo.criar_tabela()
        print("✅ Tabela generator_types criada com sucesso!")
        
        # Control Types
        print("📋 Criando tabela control_types...")
        control_type_repo = ControlTypeRepository()
        control_type_repo.criar_tabela()
        print("✅ Tabela control_types criada com sucesso!")
        
        # Aerogenerators
        print("📋 Criando tabela aerogenerators...")
        aerogenerator_repo = AerogeneratorRepository()
        aerogenerator_repo.criar_tabela()
        print("✅ Tabela aerogenerators criada com sucesso!")
        
        print("\n🎉 Todas as tabelas foram criadas com sucesso!")
        
        # Contar registros existentes
        print("\n📊 Verificando registros existentes:")
        print(f"- Fabricantes: {manufacturer_repo.contar_total()}")
        print(f"- Tipos de Turbina: {turbine_type_repo.contar_total()}")
        print(f"- Tipos de Gerador: {generator_type_repo.contar_total()}")
        print(f"- Tipos de Controle: {control_type_repo.contar_total()}")
        print(f"- Aerogeradores: {aerogenerator_repo.contar_total()}")
        
        # Inicializar tipos padrão se necessário
        print("\n🛠️ Inicializando tipos padrão...")
        turbine_type_repo.inicializar_tipos_padrao()
        print("✅ Tipos padrão de turbina inicializados!")
        
        print(f"\n✅ Tipos de Turbina após inicialização: {turbine_type_repo.contar_total()}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tables()
