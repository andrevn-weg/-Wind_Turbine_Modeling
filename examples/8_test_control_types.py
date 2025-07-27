#!/usr/bin/env python3
"""
Exemplo 8 - Teste e Validação de ControlTypes (Tipos de Controle)

Este exemplo demonstra o uso completo da entidade ControlType e seu repositório,
incluindo operações CRUD, validações e inicialização de tipos padrão.

Funcionalidades demonstradas:
- Criação e validação de tipos de controle
- Operações CRUD (Create, Read, Update, Delete)
- Inicialização de tipos padrão (Pitch, Stall, Active Stall)
- Consultas especializadas (controles com pitch, passivos)
- Métodos de verificação específicos para cada tipo
- Tratamento de erros e validações

Autor: andrevn
Data: 2025-01-27
"""

import sys
import os

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turbine_parameters.control_types import ControlType, ControlTypeRepository


def configurar_base_de_dados():
    """Cria as tabelas necessárias se não existirem"""
    print("🔧 Configurando base de dados...")
    
    repo = ControlTypeRepository()
    repo.criar_tabela()
    
    print("✅ Tabela de tipos de controle criada/verificada com sucesso!")
    print()


def exemplo_inicializacao_tipos_padrao():
    """Demonstra a inicialização dos tipos padrão"""
    print("📦 === EXEMPLO: Inicialização de Tipos Padrão ===")
    
    repo = ControlTypeRepository()
    
    print("Inicializando tipos padrão de controle...")
    repo.inicializar_tipos_padrao()
    
    # Verificar tipos criados
    tipos_criados = repo.listar_todos()
    print(f"✅ Total de tipos criados/verificados: {len(tipos_criados)}")
    
    for tipo in tipos_criados:
        print(f"   • {tipo.type}: {tipo.description}")
    
    print()
    return tipos_criados


def exemplo_validacoes():
    """Demonstra validações da entidade ControlType"""
    print("🔍 === EXEMPLO: Validações de Tipos de Controle ===")
    
    # Teste 1: Tipo obrigatório
    try:
        control_type = ControlType(type="", description="Descrição teste")
        print("❌ Deveria ter dado erro para tipo vazio")
    except ValueError as e:
        print(f"✅ Validação tipo vazio: {e}")
    
    # Teste 2: Tipo muito longo
    try:
        control_type = ControlType(type="A" * 150, description="Descrição")
        print("❌ Deveria ter dado erro para tipo muito longo")
    except ValueError as e:
        print(f"✅ Validação tipo longo: {e}")
    
    # Teste 3: Tipo inválido
    try:
        control_type = ControlType(type="AutoPilot", description="Tipo inválido")
        print("❌ Deveria ter dado erro para tipo inválido")
    except ValueError as e:
        print(f"✅ Validação tipo inválido: {e}")
    
    # Teste 4: Descrição muito longa
    try:
        control_type = ControlType(
            type="Pitch",
            description="A" * 1200  # Mais de 1000 caracteres
        )
        print("❌ Deveria ter dado erro para descrição muito longa")
    except ValueError as e:
        print(f"✅ Validação descrição longa: {e}")
    
    # Teste 5: Tipos válidos
    tipos_validos = ["Pitch", "Stall", "Active Stall"]
    for tipo in tipos_validos:
        try:
            control_type = ControlType(
                type=tipo,
                description=f"Descrição para {tipo}"
            )
            print(f"✅ Tipo válido criado: {control_type.type}")
        except ValueError as e:
            print(f"❌ Erro inesperado para {tipo}: {e}")
    
    print()


def exemplo_metodos_verificacao():
    """Demonstra os métodos de verificação da entidade"""
    print("🔍 === EXEMPLO: Métodos de Verificação e Características ===")
    
    tipos_para_testar = [
        ("Pitch", "Controle ativo através do ângulo das pás"),
        ("Stall", "Controle passivo através do stall aerodinâmico"),
        ("Active Stall", "Controle ativo do stall através do ângulo das pás")
    ]
    
    for tipo_nome, descricao in tipos_para_testar:
        print(f"\\n{tipos_para_testar.index((tipo_nome, descricao)) + 1}. Testando tipo {tipo_nome}:")
        
        control_type = ControlType(type=tipo_nome, description=descricao)
        
        print(f"   • is_pitch(): {control_type.is_pitch()}")
        print(f"   • is_stall(): {control_type.is_stall()}")
        print(f"   • is_active_stall(): {control_type.is_active_stall()}")
        print(f"   • requires_pitch_actuators(): {control_type.requires_pitch_actuators()}")
        print(f"   • is_passive_control(): {control_type.is_passive_control()}")
        print(f"   • get_control_mechanism(): {control_type.get_control_mechanism()}")
    
    print()


def exemplo_operacoes_crud():
    """Demonstra operações CRUD completas"""
    print("🔄 === EXEMPLO: Operações CRUD ===")
    
    repo = ControlTypeRepository()
    
    # CREATE - Criar um tipo de teste personalizado
    print("1. CREATE - Criando tipo de teste...")
    tipo_teste = ControlType(
        type="Pitch",
        description="Tipo de teste para demonstração CRUD - Pitch Control Avançado"
    )
    
    try:
        # Verificar se já existe
        tipo_existente = repo.buscar_por_tipo("Pitch")
        if not tipo_existente:
            type_id = repo.salvar(tipo_teste)
            print(f"✅ Tipo criado com ID: {type_id}")
            tipo_para_teste = tipo_teste
        else:
            type_id = tipo_existente.id
            print(f"✅ Usando tipo existente com ID: {type_id}")
            tipo_para_teste = tipo_existente
            
    except ValueError as e:
        print(f"❌ Erro ao criar: {e}")
        return
    
    # READ - Ler o tipo
    print("\\n2. READ - Buscando tipo...")
    tipo_encontrado = repo.buscar_por_id(type_id)
    if tipo_encontrado:
        print(f"✅ Tipo encontrado: {tipo_encontrado.type}")
        print(f"   Descrição: {tipo_encontrado.description}")
        print(f"   Mecanismo: {tipo_encontrado.get_control_mechanism()}")
        print(f"   Requer atuadores: {tipo_encontrado.requires_pitch_actuators()}")
    else:
        print("❌ Tipo não encontrado")
        return
    
    # UPDATE - Atualizar o tipo (apenas se for específico de teste)
    if "teste" in tipo_encontrado.description.lower():
        print("\\n3. UPDATE - Atualizando tipo...")
        tipo_encontrado.description = "Controle de pitch de alta precisão - Atualizado"
        
        try:
            sucesso = repo.atualizar(tipo_encontrado)
            if sucesso:
                print("✅ Tipo atualizado com sucesso")
                # Verificar a atualização
                tipo_atualizado = repo.buscar_por_id(type_id)
                print(f"   Descrição atualizada: {tipo_atualizado.description}")
            else:
                print("❌ Falha ao atualizar tipo")
        except ValueError as e:
            print(f"❌ Erro ao atualizar: {e}")
        
        # DELETE - Pergunta ao usuário se deseja excluir
        print("\\n4. DELETE - Excluindo tipo de teste...")
        resposta = input("Deseja excluir o tipo de teste? (s/N): ").strip().lower()
        
        if resposta == 's':
            sucesso = repo.excluir(type_id)
            if sucesso:
                print("✅ Tipo excluído com sucesso")
            else:
                print("❌ Falha ao excluir tipo")
        else:
            print("⚠️  Tipo de teste mantido no banco")
    else:
        print("\\n3. UPDATE/DELETE - Pulando para tipos padrão (preservação)")
        print("   ⚠️  Tipos padrão não são modificados neste exemplo")
    
    print()


def exemplo_consultas_especializadas():
    """Demonstra consultas especializadas"""
    print("🔍 === EXEMPLO: Consultas Especializadas ===")
    
    repo = ControlTypeRepository()
    
    # Listar todos os tipos
    print("1. Listando todos os tipos de controle:")
    todos_tipos = repo.listar_todos()
    for tipo in todos_tipos:
        print(f"   • {tipo.type}: {tipo.description}")
    
    # Buscar por tipo específico
    print("\\n2. Buscando tipo 'Pitch':")
    tipo_pitch = repo.buscar_por_tipo("Pitch")
    if tipo_pitch:
        print(f"   ✅ Encontrado: {tipo_pitch.type}")
        print(f"      Descrição: {tipo_pitch.description}")
        print(f"      Mecanismo: {tipo_pitch.get_control_mechanism()}")
    else:
        print("   ❌ Tipo 'Pitch' não encontrado")
    
    # Consultas especializadas
    print("\\n3. Tipos que requerem atuadores de pitch:")
    tipos_com_pitch = repo.listar_que_requerem_pitch()
    for tipo in tipos_com_pitch:
        control_obj = ControlType(type=tipo.type, description=tipo.description)
        print(f"   • {tipo.type} - Requer atuadores: {control_obj.requires_pitch_actuators()}")
    
    print("\\n4. Tipos de controle passivo:")
    tipos_passivos = repo.listar_controles_passivos()
    for tipo in tipos_passivos:
        control_obj = ControlType(type=tipo.type, description=tipo.description)
        print(f"   • {tipo.type} - Passivo: {control_obj.is_passive_control()}")
    
    # Buscar por termo
    print("\\n5. Buscando tipos com 'Stall' no nome ou descrição:")
    tipos_stall = repo.buscar_por_termo("Stall")
    for tipo in tipos_stall:
        print(f"   • {tipo.type}: {tipo.description}")
    
    # Verificar existência
    print("\\n6. Verificando existência de tipos:")
    tipos_para_verificar = ["Pitch", "Stall", "Active Stall", "Manual"]
    for tipo_nome in tipos_para_verificar:
        existe = repo.existe_tipo(tipo_nome)
        status = "✅ Existe" if existe else "❌ Não existe"
        print(f"   • {tipo_nome}: {status}")
    
    # Estatísticas
    print("\\n7. Estatísticas:")
    total = repo.contar_total()
    print(f"   • Total de tipos cadastrados: {total}")
    
    print()


def exemplo_conversao_dados():
    """Demonstra conversão de dados (to_dict/from_dict)"""
    print("🔄 === EXEMPLO: Conversão de Dados ===")
    
    # Criar um tipo de controle
    control_type = ControlType(
        type="Active Stall",
        description="Controle ativo do stall através do ângulo das pás"
    )
    
    # Converter para dicionário
    print("1. Convertendo entidade para dicionário:")
    type_dict = control_type.to_dict()
    for key, value in type_dict.items():
        print(f"   {key}: {value}")
    
    # Converter de volta para entidade
    print("\\n2. Convertendo dicionário de volta para entidade:")
    type_from_dict = ControlType.from_dict(type_dict)
    print(f"   Tipo: {type_from_dict.type}")
    print(f"   Descrição: {type_from_dict.description}")
    print(f"   Mecanismo: {type_from_dict.get_control_mechanism()}")
    print(f"   É Active Stall: {type_from_dict.is_active_stall()}")
    print(f"   Requer atuadores: {type_from_dict.requires_pitch_actuators()}")
    
    print()


def exemplo_comparacao_tipos():
    """Demonstra comparação entre diferentes tipos de controle"""
    print("⚖️  === EXEMPLO: Comparação de Tipos de Controle ===")
    
    # Criar diferentes tipos
    tipos = [
        ControlType(type="Pitch", description="Controle ativo através do ângulo das pás"),
        ControlType(type="Stall", description="Controle passivo através do stall aerodinâmico"),
        ControlType(type="Active Stall", description="Controle ativo do stall")
    ]
    
    print("Características dos diferentes tipos de controle:")
    print()
    
    for tipo in tipos:
        print(f"🔹 {tipo.type}:")
        print(f"   • Descrição: {tipo.description}")
        print(f"   • Mecanismo: {tipo.get_control_mechanism()}")
        print(f"   • Requer atuadores de pitch: {'Sim' if tipo.requires_pitch_actuators() else 'Não'}")
        print(f"   • É controle passivo: {'Sim' if tipo.is_passive_control() else 'Não'}")
        
        # Características específicas
        if tipo.is_pitch():
            print("   • Vantagens: Máximo controle, alta eficiência")
            print("   • Complexidade: Alta (requer sistema hidráulico/elétrico)")
        elif tipo.is_stall():
            print("   • Vantagens: Simplicidade, robustez, baixo custo")
            print("   • Complexidade: Baixa (sem partes móveis no rotor)")
        elif tipo.is_active_stall():
            print("   • Vantagens: Combina eficiência e robustez")
            print("   • Complexidade: Média (atuadores + design aerodinâmico)")
        
        print()


def exemplo_tratamento_erros():
    """Demonstra tratamento de erros e situações especiais"""
    print("⚠️  === EXEMPLO: Tratamento de Erros ===")
    
    repo = ControlTypeRepository()
    
    # Tentativa de salvar tipo duplicado
    print("1. Tentando salvar tipo com nome duplicado:")
    try:
        # Primeiro, garantir que existe um tipo
        if not repo.existe_tipo("Pitch"):
            repo.inicializar_tipos_padrao()
        
        # Tentar salvar duplicado
        tipo_duplicado = ControlType(
            type="Pitch",
            description="Tentativa de duplicação"
        )
        repo.salvar(tipo_duplicado)
        print("   ❌ Deveria ter dado erro para tipo duplicado")
    except ValueError as e:
        print(f"   ✅ Erro capturado corretamente: {e}")
    
    # Buscar tipo inexistente
    print("\\n2. Buscando tipo inexistente:")
    tipo_inexistente = repo.buscar_por_id(99999)
    if tipo_inexistente is None:
        print("   ✅ Retornou None para tipo inexistente")
    else:
        print("   ❌ Deveria ter retornado None")
    
    # Buscar por nome inexistente
    print("\\n3. Buscando por nome inexistente:")
    tipo_nome_inexistente = repo.buscar_por_tipo("AutoPilot")
    if tipo_nome_inexistente is None:
        print("   ✅ Retornou None para nome inexistente")
    else:
        print("   ❌ Deveria ter retornado None")
    
    # Testar exclusão de tipo inexistente
    print("\\n4. Tentando excluir tipo inexistente:")
    sucesso = repo.excluir(99999)
    if not sucesso:
        print("   ✅ Retornou False para ID inexistente")
    else:
        print("   ❌ Deveria ter retornado False")
    
    print()


def exemplo_cenarios_aplicacao():
    """Demonstra cenários de aplicação dos diferentes tipos de controle"""
    print("🎯 === EXEMPLO: Cenários de Aplicação ===")
    
    repo = ControlTypeRepository()
    tipos = repo.listar_todos()
    
    if not tipos:
        repo.inicializar_tipos_padrao()
        tipos = repo.listar_todos()
    
    print("Cenários recomendados para cada tipo de controle:")
    print()
    
    for tipo in tipos:
        control_obj = ControlType(type=tipo.type, description=tipo.description)
        print(f"🔹 {tipo.type}:")
        
        if control_obj.is_pitch():
            print("   • Cenário ideal: Turbinas grandes (>1MW), ventos variáveis")
            print("   • Aplicação: Parques eólicos comerciais, offshore")
            print("   • Benefícios: Máxima captação de energia, proteção contra sobrecarga")
            
        elif control_obj.is_stall():
            print("   • Cenário ideal: Turbinas pequenas/médias, ventos constantes")
            print("   • Aplicação: Sistemas distribuídos, áreas remotas")
            print("   • Benefícios: Baixa manutenção, alta confiabilidade")
            
        elif control_obj.is_active_stall():
            print("   • Cenário ideal: Turbinas médias, ventos moderadamente variáveis")
            print("   • Aplicação: Parques onshore, sistemas híbridos")
            print("   • Benefícios: Equilíbrio entre eficiência e simplicidade")
        
        print()


def main():
    """Função principal que executa todos os exemplos"""
    print("🌪️  === SISTEMA DE VALIDAÇÃO: CONTROL TYPES ===")
    print("Testando entidade ControlType e ControlTypeRepository")
    print("=" * 60)
    print()
    
    try:
        # Configurar base de dados
        configurar_base_de_dados()
        
        # Executar exemplos
        exemplo_validacoes()
        tipos_salvos = exemplo_inicializacao_tipos_padrao()
        exemplo_metodos_verificacao()
        exemplo_operacoes_crud()
        exemplo_consultas_especializadas()
        exemplo_conversao_dados()
        exemplo_comparacao_tipos()
        exemplo_cenarios_aplicacao()
        exemplo_tratamento_erros()
        
        print("🎉 === VALIDAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Todos os testes de ControlTypes foram executados.")
        print("Verifique os resultados acima para confirmar o funcionamento.")
        
    except Exception as e:
        print(f"💥 Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
