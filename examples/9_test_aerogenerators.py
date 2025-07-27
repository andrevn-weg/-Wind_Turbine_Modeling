#!/usr/bin/env python3
"""
Exemplo 9 - Teste e Validação de Aerogenerators (Aerogeradores Completos)

Este exemplo demonstra o uso completo da entidade Aerogenerator e seu repositório,
incluindo operações CRUD, validações, consultas relacionais e cálculos técnicos.

Funcionalidades demonstradas:
- Criação e validação de aerogeradores completos
- Operações CRUD (Create, Read, Update, Delete)
- Consultas relacionais com informações completas
- Consultas especializadas (por fabricante, faixa de potência, etc.)
- Cálculos técnicos (área varrida, densidade de potência, TSR)
- Estatísticas por fabricante
- Tratamento de erros e validações

Autor: andrevn
Data: 2025-01-27
"""

import sys
import os
from decimal import Decimal

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turbine_parameters.aerogenerators import Aerogenerator, AerogeneratorRepository
from turbine_parameters.manufacturers import Manufacturer, ManufacturerRepository
from turbine_parameters.turbine_types import TurbineType, TurbineTypeRepository
from turbine_parameters.generator_types import GeneratorType, GeneratorTypeRepository
from turbine_parameters.control_types import ControlType, ControlTypeRepository


def configurar_base_de_dados():
    """Cria as tabelas necessárias se não existirem"""
    print("🔧 Configurando base de dados...")
    
    # Criar todas as tabelas necessárias
    repos = [
        ManufacturerRepository(),
        TurbineTypeRepository(),
        GeneratorTypeRepository(),
        ControlTypeRepository(),
        AerogeneratorRepository()
    ]
    
    for repo in repos:
        repo.criar_tabela()
    
    print("✅ Todas as tabelas criadas/verificadas com sucesso!")
    print()


def configurar_dados_base():
    """Configura dados base necessários para os testes"""
    print("📋 === CONFIGURAÇÃO: Dados Base ===")
    
    # Configurar fabricantes
    manufacturer_repo = ManufacturerRepository()
    if manufacturer_repo.contar_total() == 0:
        print("Criando fabricantes base...")
        fabricantes = [
            Manufacturer(name="Vestas", country="Denmark", official_website="https://www.vestas.com"),
            Manufacturer(name="GE Renewable Energy", country="United States", official_website="https://www.ge.com"),
            Manufacturer(name="Siemens Gamesa", country="Spain", official_website="https://www.siemensgamesa.com")
        ]
        for fabricante in fabricantes:
            try:
                manufacturer_repo.salvar(fabricante)
                print(f"   ✅ {fabricante.name}")
            except ValueError:
                print(f"   ⚠️  {fabricante.name} (já existe)")
    
    # Configurar tipos de turbina
    turbine_repo = TurbineTypeRepository()
    turbine_repo.inicializar_tipos_padrao()
    
    # Configurar tipos de gerador
    generator_repo = GeneratorTypeRepository()
    generator_repo.inicializar_tipos_padrao()
    
    # Configurar tipos de controle
    control_repo = ControlTypeRepository()
    control_repo.inicializar_tipos_padrao()
    
    print("✅ Dados base configurados!")
    print()


def exemplo_validacoes():
    """Demonstra validações da entidade Aerogenerator"""
    print("🔍 === EXEMPLO: Validações de Aerogeradores ===")
    
    # Teste 1: Código do modelo obrigatório
    try:
        aerogenerator = Aerogenerator(
            model_code="",
            manufacturer_id=1,
            model="Teste",
            rated_power_kw=Decimal('1000'),
            rated_voltage_kv=Decimal('0.69'),
            cut_in_speed=Decimal('3'),
            cut_out_speed=Decimal('25'),
            rotor_diameter_m=Decimal('80'),
            turbine_type_id=1,
            generator_type_id=1,
            control_type_id=1
        )
        print("❌ Deveria ter dado erro para código vazio")
    except ValueError as e:
        print(f"✅ Validação código vazio: {e}")
    
    # Teste 2: Modelo obrigatório
    try:
        aerogenerator = Aerogenerator(
            model_code="TEST-001",
            manufacturer_id=1,
            model="",
            rated_power_kw=Decimal('1000'),
            rated_voltage_kv=Decimal('0.69'),
            cut_in_speed=Decimal('3'),
            cut_out_speed=Decimal('25'),
            rotor_diameter_m=Decimal('80'),
            turbine_type_id=1,
            generator_type_id=1,
            control_type_id=1
        )
        print("❌ Deveria ter dado erro para modelo vazio")
    except ValueError as e:
        print(f"✅ Validação modelo vazio: {e}")
    
    # Teste 3: Potência deve ser positiva
    try:
        aerogenerator = Aerogenerator(
            model_code="TEST-002",
            manufacturer_id=1,
            model="Teste",
            rated_power_kw=Decimal('0'),
            rated_voltage_kv=Decimal('0.69'),
            cut_in_speed=Decimal('3'),
            cut_out_speed=Decimal('25'),
            rotor_diameter_m=Decimal('80'),
            turbine_type_id=1,
            generator_type_id=1,
            control_type_id=1
        )
        print("❌ Deveria ter dado erro para potência zero")
    except ValueError as e:
        print(f"✅ Validação potência zero: {e}")
    
    # Teste 4: Cut-in deve ser menor que cut-out
    try:
        aerogenerator = Aerogenerator(
            model_code="TEST-003",
            manufacturer_id=1,
            model="Teste",
            rated_power_kw=Decimal('1000'),
            rated_voltage_kv=Decimal('0.69'),
            cut_in_speed=Decimal('25'),
            cut_out_speed=Decimal('3'),
            rotor_diameter_m=Decimal('80'),
            turbine_type_id=1,
            generator_type_id=1,
            control_type_id=1
        )
        print("❌ Deveria ter dado erro para cut-in > cut-out")
    except ValueError as e:
        print(f"✅ Validação velocidades: {e}")
    
    # Teste 5: Fator de potência deve estar entre 0 e 1
    try:
        aerogenerator = Aerogenerator(
            model_code="TEST-004",
            manufacturer_id=1,
            model="Teste",
            rated_power_kw=Decimal('1000'),
            rated_voltage_kv=Decimal('0.69'),
            cut_in_speed=Decimal('3'),
            cut_out_speed=Decimal('25'),
            rotor_diameter_m=Decimal('80'),
            power_factor=Decimal('1.5'),
            turbine_type_id=1,
            generator_type_id=1,
            control_type_id=1
        )
        print("❌ Deveria ter dado erro para fator de potência > 1")
    except ValueError as e:
        print(f"✅ Validação fator de potência: {e}")
    
    # Teste 6: Aerogerador válido
    try:
        aerogenerator = Aerogenerator(
            model_code="V90-2.0MW",
            manufacturer_id=1,
            model="V90-2.0MW",
            manufacture_year=2020,
            rated_power_kw=Decimal('2000'),
            rated_voltage_kv=Decimal('0.69'),
            cut_in_speed=Decimal('4'),
            cut_out_speed=Decimal('25'),
            rated_wind_speed=Decimal('15'),
            rotor_diameter_m=Decimal('90'),
            blade_count=3,
            rated_rotor_speed_rpm=Decimal('19'),
            variable_speed=True,
            pitch_control=True,
            pitch_min_deg=Decimal('-5'),
            pitch_max_deg=Decimal('90'),
            turbine_type_id=1,
            generator_type_id=1,
            control_type_id=1
        )
        print(f"✅ Aerogerador válido criado: {aerogenerator.model}")
    except ValueError as e:
        print(f"❌ Erro inesperado: {e}")
    
    print()


def exemplo_calculos_tecnicos():
    """Demonstra cálculos técnicos dos aerogeradores"""
    print("🧮 === EXEMPLO: Cálculos Técnicos ===")
    
    # Criar um aerogerador de exemplo
    aerogenerator = Aerogenerator(
        model_code="V90-2.0MW",
        manufacturer_id=1,
        model="V90-2.0MW",
        rated_power_kw=Decimal('2000'),
        rated_voltage_kv=Decimal('0.69'),
        cut_in_speed=Decimal('4'),
        cut_out_speed=Decimal('25'),
        rated_wind_speed=Decimal('15'),
        rotor_diameter_m=Decimal('90'),
        rated_rotor_speed_rpm=Decimal('19'),
        turbine_type_id=1,
        generator_type_id=1,
        control_type_id=1
    )
    
    print(f"📊 Cálculos para {aerogenerator.model}:")
    print(f"   • Diâmetro do rotor: {aerogenerator.rotor_diameter_m} m")
    print(f"   • Potência nominal: {aerogenerator.rated_power_kw} kW")
    
    # Área varrida
    area_varrida = aerogenerator.get_swept_area()
    print(f"   • Área varrida: {area_varrida:.2f} m²")
    
    # Densidade de potência
    densidade_potencia = aerogenerator.get_power_density()
    print(f"   • Densidade de potência: {densidade_potencia:.2f} kW/m²")
    
    # TSR para diferentes velocidades de vento
    print("   • Tip Speed Ratio (TSR) para diferentes ventos:")
    velocidades_teste = [Decimal('8'), Decimal('12'), Decimal('15'), Decimal('20')]
    for vel in velocidades_teste:
        tsr = aerogenerator.get_tip_speed_ratio(vel)
        if tsr:
            print(f"     - {vel} m/s: TSR = {tsr:.2f}")
        else:
            print(f"     - {vel} m/s: TSR não calculável")
    
    # Faixa operacional
    print("   • Teste de faixa operacional:")
    velocidades_teste = [Decimal('2'), Decimal('5'), Decimal('15'), Decimal('30')]
    for vel in velocidades_teste:
        operacional = aerogenerator.is_in_operational_range(vel)
        status = "✅ Operacional" if operacional else "❌ Fora da faixa"
        print(f"     - {vel} m/s: {status}")
    
    # Controle de pitch
    print(f"   • Controle de pitch disponível: {aerogenerator.has_pitch_control_capability()}")
    if aerogenerator.pitch_min_deg and aerogenerator.pitch_max_deg:
        print(f"     - Faixa de pitch: {aerogenerator.pitch_min_deg}° a {aerogenerator.pitch_max_deg}°")
    
    print()


def exemplo_operacoes_crud():
    """Demonstra operações CRUD completas"""
    print("🔄 === EXEMPLO: Operações CRUD ===")
    
    repo = AerogeneratorRepository()
    
    # Buscar IDs necessários
    manufacturer_repo = ManufacturerRepository()
    turbine_repo = TurbineTypeRepository()
    generator_repo = GeneratorTypeRepository()
    control_repo = ControlTypeRepository()
    
    vestas = manufacturer_repo.buscar_por_nome("Vestas")
    horizontal = turbine_repo.buscar_por_tipo("Horizontal")
    pmsg = generator_repo.buscar_por_tipo("PMSG")
    pitch = control_repo.buscar_por_tipo("Pitch")
    
    if not all([vestas, horizontal, pmsg, pitch]):
        print("❌ Dados base não encontrados. Execute configurar_dados_base() primeiro.")
        return
    
    # CREATE - Criar um aerogerador de teste
    print("1. CREATE - Criando aerogerador de teste...")
    aerogenerator_teste = Aerogenerator(
        model_code="TEST-V90-2MW",
        manufacturer_id=vestas.id,
        model="V90-2.0MW Test Edition",
        manufacture_year=2023,
        rated_power_kw=Decimal('2000'),
        apparent_power_kva=Decimal('2200'),
        power_factor=Decimal('0.95'),
        rated_voltage_kv=Decimal('0.69'),
        cut_in_speed=Decimal('4'),
        cut_out_speed=Decimal('25'),
        rated_wind_speed=Decimal('15'),
        rotor_diameter_m=Decimal('90'),
        blade_count=3,
        rated_rotor_speed_rpm=Decimal('19'),
        variable_speed=True,
        pitch_control=True,
        pitch_min_deg=Decimal('-5'),
        pitch_max_deg=Decimal('90'),
        turbine_type_id=horizontal.id,
        generator_type_id=pmsg.id,
        control_type_id=pitch.id
    )
    
    try:
        if not repo.existe_model_code(aerogenerator_teste.model_code):
            aerogenerator_id = repo.salvar(aerogenerator_teste)
            print(f"✅ Aerogerador criado com ID: {aerogenerator_id}")
        else:
            # Se já existe, buscar o existente
            aerogenerator_teste = repo.buscar_por_model_code(aerogenerator_teste.model_code)
            aerogenerator_id = aerogenerator_teste.id
            print(f"⚠️  Aerogerador já existe com ID: {aerogenerator_id}")
    except ValueError as e:
        print(f"❌ Erro ao criar: {e}")
        return
    
    # READ - Ler o aerogerador
    print("\\n2. READ - Buscando aerogerador...")
    aerogenerator_encontrado = repo.buscar_por_id(aerogenerator_id)
    if aerogenerator_encontrado:
        print(f"✅ Aerogerador encontrado: {aerogenerator_encontrado.model}")
        print(f"   Código: {aerogenerator_encontrado.model_code}")
        print(f"   Potência: {aerogenerator_encontrado.rated_power_kw} kW")
        print(f"   Diâmetro: {aerogenerator_encontrado.rotor_diameter_m} m")
        print(f"   Área varrida: {aerogenerator_encontrado.get_swept_area():.2f} m²")
    else:
        print("❌ Aerogerador não encontrado")
        return
    
    # UPDATE - Atualizar o aerogerador
    print("\\n3. UPDATE - Atualizando aerogerador...")
    aerogenerator_encontrado.manufacture_year = 2024
    aerogenerator_encontrado.power_factor = Decimal('0.97')
    
    try:
        sucesso = repo.atualizar(aerogenerator_encontrado)
        if sucesso:
            print("✅ Aerogerador atualizado com sucesso")
            # Verificar a atualização
            aerogenerator_atualizado = repo.buscar_por_id(aerogenerator_id)
            print(f"   Ano atualizado: {aerogenerator_atualizado.manufacture_year}")
            print(f"   Fator de potência: {aerogenerator_atualizado.power_factor}")
        else:
            print("❌ Falha ao atualizar aerogerador")
    except ValueError as e:
        print(f"❌ Erro ao atualizar: {e}")
    
    # DELETE - Pergunta ao usuário se deseja excluir
    print("\\n4. DELETE - Excluindo aerogerador de teste...")
    resposta = input("Deseja excluir o aerogerador de teste? (s/N): ").strip().lower()
    
    if resposta == 's':
        sucesso = repo.excluir(aerogenerator_id)
        if sucesso:
            print("✅ Aerogerador excluído com sucesso")
        else:
            print("❌ Falha ao excluir aerogerador")
    else:
        print("⚠️  Aerogerador de teste mantido no banco")
    
    print()


def exemplo_consultas_relacionais():
    """Demonstra consultas relacionais avançadas"""
    print("🔍 === EXEMPLO: Consultas Relacionais ===")
    
    repo = AerogeneratorRepository()
    
    # Listar aerogeradores com detalhes completos
    print("1. Aerogeradores com informações completas:")
    aerogeradores_detalhados = repo.buscar_com_detalhes_completos(limite=5)
    
    if not aerogeradores_detalhados:
        print("   ⚠️  Nenhum aerogerador encontrado. Criando exemplo...")
        exemplo_criacao_aerogeradores()
        aerogeradores_detalhados = repo.buscar_com_detalhes_completos(limite=5)
    
    for aerogen in aerogeradores_detalhados:
        print(f"   🔹 {aerogen['model']} ({aerogen['model_code']})")
        print(f"      Fabricante: {aerogen['manufacturer_name']} ({aerogen['manufacturer_country']})")
        print(f"      Tipo: {aerogen['turbine_type']} | Gerador: {aerogen['generator_type']} | Controle: {aerogen['control_type']}")
        print(f"      Potência: {aerogen['rated_power_kw']} kW | Diâmetro: {aerogen['rotor_diameter_m']} m")
        print()
    
    # Estatísticas por fabricante
    print("2. Estatísticas por fabricante:")
    estatisticas = repo.buscar_estatisticas_por_fabricante()
    for stat in estatisticas:
        print(f"   🏭 {stat['manufacturer_name']}:")
        print(f"      • Total de modelos: {stat['total_models']}")
        print(f"      • Potência média: {stat['avg_power_kw']:.1f} kW")
        print(f"      • Faixa de potência: {stat['min_power_kw']:.0f} - {stat['max_power_kw']:.0f} kW")
        print(f"      • Diâmetro médio: {stat['avg_diameter_m']:.1f} m")
        print()
    
    print()


def exemplo_consultas_especializadas():
    """Demonstra consultas especializadas"""
    print("🎯 === EXEMPLO: Consultas Especializadas ===")
    
    repo = AerogeneratorRepository()
    manufacturer_repo = ManufacturerRepository()
    
    # Buscar por fabricante
    vestas = manufacturer_repo.buscar_por_nome("Vestas")
    if vestas:
        print(f"1. Aerogeradores da {vestas.name}:")
        aerogeradores_vestas = repo.buscar_por_fabricante(vestas.id)
        for aerogen in aerogeradores_vestas:
            print(f"   • {aerogen.model} - {aerogen.rated_power_kw} kW")
    
    # Buscar por faixa de potência
    print("\\n2. Aerogeradores entre 1.5MW e 3.0MW:")
    aerogeradores_potencia = repo.buscar_por_faixa_potencia(
        Decimal('1500'), Decimal('3000')
    )
    for aerogen in aerogeradores_potencia:
        print(f"   • {aerogen.model} - {aerogen.rated_power_kw} kW")
    
    # Buscar por faixa de diâmetro
    print("\\n3. Aerogeradores com diâmetro entre 80m e 100m:")
    aerogeradores_diametro = repo.buscar_por_diametro_rotor(
        Decimal('80'), Decimal('100')
    )
    for aerogen in aerogeradores_diametro:
        print(f"   • {aerogen.model} - Ø {aerogen.rotor_diameter_m} m")
    
    # Estatísticas gerais
    print("\\n4. Estatísticas gerais:")
    total_aerogeradores = repo.contar_total()
    print(f"   • Total de aerogeradores cadastrados: {total_aerogeradores}")
    
    print()


def exemplo_criacao_aerogeradores():
    """Cria alguns aerogeradores de exemplo se não existirem"""
    print("📦 === CRIANDO: Aerogeradores de Exemplo ===")
    
    repo = AerogeneratorRepository()
    manufacturer_repo = ManufacturerRepository()
    turbine_repo = TurbineTypeRepository()
    generator_repo = GeneratorTypeRepository()
    control_repo = ControlTypeRepository()
    
    # Buscar dados necessários
    vestas = manufacturer_repo.buscar_por_nome("Vestas")
    ge = manufacturer_repo.buscar_por_nome("GE Renewable Energy")
    horizontal = turbine_repo.buscar_por_tipo("Horizontal")
    pmsg = generator_repo.buscar_por_tipo("PMSG")
    dfig = generator_repo.buscar_por_tipo("DFIG")
    pitch = control_repo.buscar_por_tipo("Pitch")
    
    if not all([vestas, ge, horizontal, pmsg, dfig, pitch]):
        print("❌ Dados base não encontrados")
        return
    
    # Aerogeradores de exemplo
    aerogeradores_exemplo = [
        {
            "model_code": "V90-2.0MW",
            "manufacturer_id": vestas.id,
            "model": "V90-2.0MW",
            "manufacture_year": 2020,
            "rated_power_kw": Decimal('2000'),
            "rated_voltage_kv": Decimal('0.69'),
            "cut_in_speed": Decimal('4'),
            "cut_out_speed": Decimal('25'),
            "rated_wind_speed": Decimal('15'),
            "rotor_diameter_m": Decimal('90'),
            "rated_rotor_speed_rpm": Decimal('19'),
            "turbine_type_id": horizontal.id,
            "generator_type_id": pmsg.id,
            "control_type_id": pitch.id
        },
        {
            "model_code": "GE-1.5MW",
            "manufacturer_id": ge.id,
            "model": "GE 1.5MW",
            "manufacture_year": 2019,
            "rated_power_kw": Decimal('1500'),
            "rated_voltage_kv": Decimal('0.69'),
            "cut_in_speed": Decimal('3.5'),
            "cut_out_speed": Decimal('25'),
            "rated_wind_speed": Decimal('12'),
            "rotor_diameter_m": Decimal('82.5'),
            "rated_rotor_speed_rpm": Decimal('22.5'),
            "turbine_type_id": horizontal.id,
            "generator_type_id": dfig.id,
            "control_type_id": pitch.id
        }
    ]
    
    aerogeradores_criados = 0
    for dados in aerogeradores_exemplo:
        try:
            if not repo.existe_model_code(dados["model_code"]):
                aerogenerator = Aerogenerator(**dados)
                repo.salvar(aerogenerator)
                print(f"✅ {aerogenerator.model} criado")
                aerogeradores_criados += 1
            else:
                print(f"⚠️  {dados['model']} já existe")
        except ValueError as e:
            print(f"❌ Erro ao criar {dados['model']}: {e}")
    
    print(f"📊 Total criados: {aerogeradores_criados}")
    print()


def exemplo_conversao_dados():
    """Demonstra conversão de dados (to_dict/from_dict)"""
    print("🔄 === EXEMPLO: Conversão de Dados ===")
    
    # Criar um aerogerador
    aerogenerator = Aerogenerator(
        model_code="V112-3.45MW",
        manufacturer_id=1,
        model="V112-3.45MW",
        manufacture_year=2021,
        rated_power_kw=Decimal('3450'),
        apparent_power_kva=Decimal('3600'),
        power_factor=Decimal('0.96'),
        rated_voltage_kv=Decimal('0.69'),
        cut_in_speed=Decimal('3'),
        cut_out_speed=Decimal('25'),
        rated_wind_speed=Decimal('15'),
        rotor_diameter_m=Decimal('112'),
        blade_count=3,
        rated_rotor_speed_rpm=Decimal('17.1'),
        variable_speed=True,
        pitch_control=True,
        pitch_min_deg=Decimal('-8'),
        pitch_max_deg=Decimal('90'),
        turbine_type_id=1,
        generator_type_id=1,
        control_type_id=1
    )
    
    # Converter para dicionário
    print("1. Convertendo entidade para dicionário:")
    aerogen_dict = aerogenerator.to_dict()
    print(f"   • Modelo: {aerogen_dict['model']}")
    print(f"   • Potência: {aerogen_dict['rated_power_kw']} kW")
    print(f"   • Diâmetro: {aerogen_dict['rotor_diameter_m']} m")
    print(f"   • Controle de pitch: {aerogen_dict['pitch_control']}")
    
    # Converter de volta para entidade
    print("\\n2. Convertendo dicionário de volta para entidade:")
    aerogen_from_dict = Aerogenerator.from_dict(aerogen_dict)
    print(f"   • Modelo: {aerogen_from_dict.model}")
    print(f"   • Área varrida: {aerogen_from_dict.get_swept_area():.2f} m²")
    print(f"   • Densidade de potência: {aerogen_from_dict.get_power_density():.2f} kW/m²")
    
    print()


def main():
    """Função principal que executa todos os exemplos"""
    print("🌪️  === SISTEMA DE VALIDAÇÃO: AEROGENERATORS ===")
    print("Testando entidade Aerogenerator e AerogeneratorRepository")
    print("=" * 60)
    print()
    
    try:
        # Configurar base de dados e dados necessários
        configurar_base_de_dados()
        configurar_dados_base()
        
        # Executar exemplos
        exemplo_validacoes()
        exemplo_calculos_tecnicos()
        exemplo_criacao_aerogeradores()
        exemplo_operacoes_crud()
        exemplo_consultas_relacionais()
        exemplo_consultas_especializadas()
        exemplo_conversao_dados()
        
        print("🎉 === VALIDAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Todos os testes de Aerogenerators foram executados.")
        print("Verifique os resultados acima para confirmar o funcionamento.")
        
    except Exception as e:
        print(f"💥 Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
