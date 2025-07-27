#!/usr/bin/env python3
"""
Exemplo 7 - Teste e Validação de GeneratorTypes (Tipos de Gerador)

Este exemplo demonstra o uso completo da entidade GeneratorType e seu repositório,
incluindo operações CRUD, validações e inicialização de tipos padrão.

Funcionalidades demonstradas:
- Criação e validação de tipos de gerador
- Operações CRUD (Create, Read, Update, Delete)
- Inicialização de tipos padrão (Synchronous, Asynchronous, PMSG, DFIG)
- Consultas por tipo e termo
- Métodos de verificação específicos para cada tipo
- Tratamento de erros e validações

Autor: andrevn
Data: 2025-01-27
"""

import sys
import os

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turbine_parameters.generator_types import GeneratorType, GeneratorTypeRepository


def configurar_base_de_dados():
    """Cria as tabelas necessárias se não existirem"""
    print("🔧 Configurando base de dados...")
    
    repo = GeneratorTypeRepository()
    repo.criar_tabela()
    
    print("✅ Tabela de tipos de gerador criada/verificada com sucesso!")
    print()


def exemplo_inicializacao_tipos_padrao():
    """Demonstra a inicialização dos tipos padrão"""
    print("📦 === EXEMPLO: Inicialização de Tipos Padrão ===")
    
    repo = GeneratorTypeRepository()
    
    print("Inicializando tipos padrão de gerador...")
    repo.inicializar_tipos_padrao()
    
    # Verificar tipos criados
    tipos_criados = repo.listar_todos()
    print(f"✅ Total de tipos criados/verificados: {len(tipos_criados)}")
    
    for tipo in tipos_criados:
        print(f"   • {tipo.type}: {tipo.description}")
    
    print()
    return tipos_criados


def exemplo_validacoes():
    """Demonstra validações da entidade GeneratorType"""
    print("🔍 === EXEMPLO: Validações de Tipos de Gerador ===")
    
    # Teste 1: Tipo obrigatório
    try:
        generator_type = GeneratorType(type="", description="Descrição teste")
        print("❌ Deveria ter dado erro para tipo vazio")
    except ValueError as e:
        print(f"✅ Validação tipo vazio: {e}")
    
    # Teste 2: Tipo muito longo
    try:
        generator_type = GeneratorType(type="A" * 150, description="Descrição")
        print("❌ Deveria ter dado erro para tipo muito longo")
    except ValueError as e:
        print(f"✅ Validação tipo longo: {e}")
    
    # Teste 3: Tipo inválido
    try:
        generator_type = GeneratorType(type="UnknownType", description="Tipo inválido")
        print("❌ Deveria ter dado erro para tipo inválido")
    except ValueError as e:
        print(f"✅ Validação tipo inválido: {e}")
    
    # Teste 4: Descrição muito longa
    try:
        generator_type = GeneratorType(
            type="PMSG",
            description="A" * 1200  # Mais de 1000 caracteres
        )
        print("❌ Deveria ter dado erro para descrição muito longa")
    except ValueError as e:
        print(f"✅ Validação descrição longa: {e}")
    
    # Teste 5: Tipos válidos
    tipos_validos = ["Synchronous", "Asynchronous", "PMSG", "DFIG"]
    for tipo in tipos_validos:
        try:
            generator_type = GeneratorType(
                type=tipo,
                description=f"Descrição para {tipo}"
            )
            print(f"✅ Tipo válido criado: {generator_type.type}")
        except ValueError as e:
            print(f"❌ Erro inesperado para {tipo}: {e}")
    
    print()


def exemplo_metodos_verificacao():
    """Demonstra os métodos de verificação da entidade"""
    print("🔍 === EXEMPLO: Métodos de Verificação ===")
    
    tipos_para_testar = [
        ("Synchronous", "Gerador síncrono"),
        ("Asynchronous", "Gerador assíncrono"),
        ("PMSG", "Permanent Magnet Synchronous Generator"),
        ("DFIG", "Doubly Fed Induction Generator")
    ]
    
    for tipo_nome, descricao in tipos_para_testar:
        print(f"\\n{len(tipos_para_testar) - tipos_para_testar.index((tipo_nome, descricao)) + 1}. Testando tipo {tipo_nome}:")
        
        generator_type = GeneratorType(type=tipo_nome, description=descricao)
        
        print(f"   • is_synchronous(): {generator_type.is_synchronous()}")
        print(f"   • is_asynchronous(): {generator_type.is_asynchronous()}")
        print(f"   • is_pmsg(): {generator_type.is_pmsg()}")
        print(f"   • is_dfig(): {generator_type.is_dfig()}")
        print(f"   • get_full_name(): {generator_type.get_full_name()}")
    
    print()


def exemplo_operacoes_crud():
    """Demonstra operações CRUD completas"""
    print("🔄 === EXEMPLO: Operações CRUD ===")
    
    repo = GeneratorTypeRepository()
    
    # CREATE - Criar um tipo de teste personalizado
    print("1. CREATE - Criando tipo de teste...")
    tipo_teste = GeneratorType(
        type="PMSG",  # Usar um tipo padrão para teste
        description="Tipo de teste para demonstração CRUD - PMSG Personalizado"
    )
    
    try:
        # Verificar se já existe
        tipo_existente = repo.buscar_por_tipo("PMSG")
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
        print(f"   Nome completo: {tipo_encontrado.get_full_name()}")
    else:
        print("❌ Tipo não encontrado")
        return
    
    # UPDATE - Atualizar o tipo (apenas se for específico de teste)
    if "teste" in tipo_encontrado.description.lower():
        print("\\n3. UPDATE - Atualizando tipo...")
        tipo_encontrado.description = "Descrição atualizada - PMSG de alta eficiência"
        
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
    
    repo = GeneratorTypeRepository()
    
    # Listar todos os tipos
    print("1. Listando todos os tipos de gerador:")
    todos_tipos = repo.listar_todos()
    for tipo in todos_tipos:
        print(f"   • {tipo.type}: {tipo.description}")
    
    # Buscar por tipo específico
    print("\\n2. Buscando tipo 'PMSG':")
    tipo_pmsg = repo.buscar_por_tipo("PMSG")
    if tipo_pmsg:
        print(f"   ✅ Encontrado: {tipo_pmsg.type}")
        print(f"      Descrição: {tipo_pmsg.description}")
        print(f"      Nome completo: {tipo_pmsg.get_full_name()}")
    else:
        print("   ❌ Tipo 'PMSG' não encontrado")
    
    # Buscar por termo
    print("\\n3. Buscando tipos com 'Synchronous' no nome ou descrição:")
    tipos_synchronous = repo.buscar_por_termo("Synchronous")
    for tipo in tipos_synchronous:
        print(f"   • {tipo.type}: {tipo.get_full_name()}")
    
    # Verificar existência
    print("\\n4. Verificando existência de tipos:")
    tipos_para_verificar = ["PMSG", "DFIG", "DC", "AC"]
    for tipo_nome in tipos_para_verificar:
        existe = repo.existe_tipo(tipo_nome)
        status = "✅ Existe" if existe else "❌ Não existe"
        print(f"   • {tipo_nome}: {status}")
    
    # Estatísticas
    print("\\n5. Estatísticas:")
    total = repo.contar_total()
    print(f"   • Total de tipos cadastrados: {total}")
    
    print()


def exemplo_conversao_dados():
    """Demonstra conversão de dados (to_dict/from_dict)"""
    print("🔄 === EXEMPLO: Conversão de Dados ===")
    
    # Criar um tipo de gerador
    generator_type = GeneratorType(
        type="DFIG",
        description="Doubly Fed Induction Generator - controle independente de potências"
    )
    
    # Converter para dicionário
    print("1. Convertendo entidade para dicionário:")
    type_dict = generator_type.to_dict()
    for key, value in type_dict.items():
        print(f"   {key}: {value}")
    
    # Converter de volta para entidade
    print("\\n2. Convertendo dicionário de volta para entidade:")
    type_from_dict = GeneratorType.from_dict(type_dict)
    print(f"   Tipo: {type_from_dict.type}")
    print(f"   Descrição: {type_from_dict.description}")
    print(f"   Nome completo: {type_from_dict.get_full_name()}")
    print(f"   É DFIG: {type_from_dict.is_dfig()}")
    print(f"   É PMSG: {type_from_dict.is_pmsg()}")
    
    print()


def exemplo_comparacao_tipos():
    """Demonstra comparação entre diferentes tipos de geradores"""
    print("⚖️  === EXEMPLO: Comparação de Tipos ===")
    
    # Criar diferentes tipos
    tipos = [
        GeneratorType(type="Synchronous", description="Gerador síncrono tradicional"),
        GeneratorType(type="Asynchronous", description="Gerador de indução"),
        GeneratorType(type="PMSG", description="Gerador síncrono com ímãs permanentes"),
        GeneratorType(type="DFIG", description="Gerador de indução duplamente alimentado")
    ]
    
    print("Características dos diferentes tipos de geradores:")
    print()
    
    for tipo in tipos:
        print(f"🔹 {tipo.type} ({tipo.get_full_name()}):")
        print(f"   • Descrição: {tipo.description}")
        
        # Características específicas
        if tipo.is_synchronous():
            print("   • Características: Velocidade constante, conexão direta à rede")
        elif tipo.is_asynchronous():
            print("   • Características: Mais simples, robusto, velocidade variável")
        elif tipo.is_pmsg():
            print("   • Características: Alta eficiência, sem escovas, manutenção reduzida")
        elif tipo.is_dfig():
            print("   • Características: Controle independente, eficiência variável")
        
        print()


def exemplo_tratamento_erros():
    """Demonstra tratamento de erros e situações especiais"""
    print("⚠️  === EXEMPLO: Tratamento de Erros ===")
    
    repo = GeneratorTypeRepository()
    
    # Tentativa de salvar tipo duplicado
    print("1. Tentando salvar tipo com nome duplicado:")
    try:
        # Primeiro, garantir que existe um tipo
        if not repo.existe_tipo("PMSG"):
            repo.inicializar_tipos_padrao()
        
        # Tentar salvar duplicado
        tipo_duplicado = GeneratorType(
            type="PMSG",
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
    tipo_nome_inexistente = repo.buscar_por_tipo("UnknownGenerator")
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


def main():
    """Função principal que executa todos os exemplos"""
    print("🌪️  === SISTEMA DE VALIDAÇÃO: GENERATOR TYPES ===")
    print("Testando entidade GeneratorType e GeneratorTypeRepository")
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
        exemplo_tratamento_erros()
        
        print("🎉 === VALIDAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Todos os testes de GeneratorTypes foram executados.")
        print("Verifique os resultados acima para confirmar o funcionamento.")
        
    except Exception as e:
        print(f"💥 Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
