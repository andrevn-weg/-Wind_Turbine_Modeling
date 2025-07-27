#!/usr/bin/env python3
"""
Exemplo 6 - Teste e Validação de TurbineTypes (Tipos de Turbina)

Este exemplo demonstra o uso completo da entidade TurbineType e seu repositório,
incluindo operações CRUD, validações e inicialização de tipos padrão.

Funcionalidades demonstradas:
- Criação e validação de tipos de turbina
- Operações CRUD (Create, Read, Update, Delete)
- Inicialização de tipos padrão (Horizontal, Vertical)
- Consultas por tipo e termo
- Métodos de verificação (is_horizontal, is_vertical)
- Tratamento de erros e validações

Autor: andrevn
Data: 2025-01-27
"""

import sys
import os

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turbine_parameters.turbine_types import TurbineType, TurbineTypeRepository


def configurar_base_de_dados():
    """Cria as tabelas necessárias se não existirem"""
    print("🔧 Configurando base de dados...")
    
    repo = TurbineTypeRepository()
    repo.criar_tabela()
    
    print("✅ Tabela de tipos de turbina criada/verificada com sucesso!")
    print()


def exemplo_inicializacao_tipos_padrao():
    """Demonstra a inicialização dos tipos padrão"""
    print("📦 === EXEMPLO: Inicialização de Tipos Padrão ===")
    
    repo = TurbineTypeRepository()
    
    print("Inicializando tipos padrão de turbina...")
    repo.inicializar_tipos_padrao()
    
    # Verificar tipos criados
    tipos_criados = repo.listar_todos()
    print(f"✅ Total de tipos criados/verificados: {len(tipos_criados)}")
    
    for tipo in tipos_criados:
        print(f"   • {tipo.type}: {tipo.description}")
    
    print()
    return tipos_criados


def exemplo_validacoes():
    """Demonstra validações da entidade TurbineType"""
    print("🔍 === EXEMPLO: Validações de Tipos de Turbina ===")
    
    # Teste 1: Tipo obrigatório
    try:
        turbine_type = TurbineType(type="", description="Descrição teste")
        print("❌ Deveria ter dado erro para tipo vazio")
    except ValueError as e:
        print(f"✅ Validação tipo vazio: {e}")
    
    # Teste 2: Tipo muito longo
    try:
        turbine_type = TurbineType(type="A" * 150, description="Descrição")
        print("❌ Deveria ter dado erro para tipo muito longo")
    except ValueError as e:
        print(f"✅ Validação tipo longo: {e}")
    
    # Teste 3: Tipo inválido
    try:
        turbine_type = TurbineType(type="Diagonal", description="Tipo inválido")
        print("❌ Deveria ter dado erro para tipo inválido")
    except ValueError as e:
        print(f"✅ Validação tipo inválido: {e}")
    
    # Teste 4: Descrição muito longa
    try:
        turbine_type = TurbineType(
            type="Horizontal",
            description="A" * 1200  # Mais de 1000 caracteres
        )
        print("❌ Deveria ter dado erro para descrição muito longa")
    except ValueError as e:
        print(f"✅ Validação descrição longa: {e}")
    
    # Teste 5: Tipos válidos
    tipos_validos = ["Horizontal", "Vertical"]
    for tipo in tipos_validos:
        try:
            turbine_type = TurbineType(
                type=tipo,
                description=f"Descrição para {tipo}"
            )
            print(f"✅ Tipo válido criado: {turbine_type.type}")
        except ValueError as e:
            print(f"❌ Erro inesperado para {tipo}: {e}")
    
    print()


def exemplo_metodos_verificacao():
    """Demonstra os métodos de verificação da entidade"""
    print("🔍 === EXEMPLO: Métodos de Verificação ===")
    
    # Testar tipo Horizontal
    tipo_horizontal = TurbineType(
        type="Horizontal",
        description="Turbina de eixo horizontal"
    )
    
    print("1. Testando tipo Horizontal:")
    print(f"   • is_horizontal(): {tipo_horizontal.is_horizontal()}")
    print(f"   • is_vertical(): {tipo_horizontal.is_vertical()}")
    
    # Testar tipo Vertical
    tipo_vertical = TurbineType(
        type="Vertical",
        description="Turbina de eixo vertical"
    )
    
    print("\\n2. Testando tipo Vertical:")
    print(f"   • is_horizontal(): {tipo_vertical.is_horizontal()}")
    print(f"   • is_vertical(): {tipo_vertical.is_vertical()}")
    
    print()


def exemplo_operacoes_crud():
    """Demonstra operações CRUD completas"""
    print("🔄 === EXEMPLO: Operações CRUD ===")
    
    repo = TurbineTypeRepository()
    
    # CREATE - Criar um tipo de teste (se não existir um dos padrão)
    print("1. CREATE - Verificando/criando tipo de teste...")
    
    # Primeiro, tentar buscar um tipo existente para teste
    tipo_teste = repo.buscar_por_tipo("Horizontal")
    
    if not tipo_teste:
        # Se não existe, criar um novo tipo de teste
        tipo_teste = TurbineType(
            type="Horizontal",
            description="Tipo de teste para demonstração CRUD"
        )
        
        try:
            type_id = repo.salvar(tipo_teste)
            print(f"✅ Tipo criado com ID: {type_id}")
        except ValueError as e:
            print(f"❌ Erro ao criar: {e}")
            return
    else:
        type_id = tipo_teste.id
        print(f"✅ Usando tipo existente com ID: {type_id}")
    
    # READ - Ler o tipo
    print("\\n2. READ - Buscando tipo...")
    tipo_encontrado = repo.buscar_por_id(type_id)
    if tipo_encontrado:
        print(f"✅ Tipo encontrado: {tipo_encontrado.type}")
        print(f"   Descrição: {tipo_encontrado.description}")
    else:
        print("❌ Tipo não encontrado")
        return
    
    # UPDATE - Atualizar o tipo (apenas se for um tipo de teste que criamos)
    if "teste" in tipo_encontrado.description.lower():
        print("\\n3. UPDATE - Atualizando tipo...")
        tipo_encontrado.description = "Descrição atualizada para demonstração"
        
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
    
    repo = TurbineTypeRepository()
    
    # Listar todos os tipos
    print("1. Listando todos os tipos de turbina:")
    todos_tipos = repo.listar_todos()
    for tipo in todos_tipos:
        print(f"   • {tipo.type}: {tipo.description}")
    
    # Buscar por tipo específico
    print("\\n2. Buscando tipo 'Horizontal':")
    tipo_horizontal = repo.buscar_por_tipo("Horizontal")
    if tipo_horizontal:
        print(f"   ✅ Encontrado: {tipo_horizontal.type}")
        print(f"      Descrição: {tipo_horizontal.description}")
    else:
        print("   ❌ Tipo 'Horizontal' não encontrado")
    
    # Buscar por termo
    print("\\n3. Buscando tipos com 'vertical' na descrição:")
    tipos_vertical = repo.buscar_por_termo("vertical")
    for tipo in tipos_vertical:
        print(f"   • {tipo.type}: {tipo.description}")
    
    # Verificar existência
    print("\\n4. Verificando existência de tipos:")
    tipos_para_verificar = ["Horizontal", "Vertical", "Diagonal"]
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
    
    # Criar um tipo de turbina
    turbine_type = TurbineType(
        type="Horizontal",
        description="Turbinas de eixo horizontal - mais comuns no mercado"
    )
    
    # Converter para dicionário
    print("1. Convertendo entidade para dicionário:")
    type_dict = turbine_type.to_dict()
    for key, value in type_dict.items():
        print(f"   {key}: {value}")
    
    # Converter de volta para entidade
    print("\\n2. Convertendo dicionário de volta para entidade:")
    type_from_dict = TurbineType.from_dict(type_dict)
    print(f"   Tipo: {type_from_dict.type}")
    print(f"   Descrição: {type_from_dict.description}")
    print(f"   É horizontal: {type_from_dict.is_horizontal()}")
    print(f"   É vertical: {type_from_dict.is_vertical()}")
    
    print()


def exemplo_tratamento_erros():
    """Demonstra tratamento de erros e situações especiais"""
    print("⚠️  === EXEMPLO: Tratamento de Erros ===")
    
    repo = TurbineTypeRepository()
    
    # Tentativa de salvar tipo duplicado
    print("1. Tentando salvar tipo com nome duplicado:")
    try:
        # Primeiro, garantir que existe um tipo
        if not repo.existe_tipo("Horizontal"):
            repo.inicializar_tipos_padrao()
        
        # Tentar salvar duplicado
        tipo_duplicado = TurbineType(
            type="Horizontal",
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
    tipo_nome_inexistente = repo.buscar_por_tipo("Diagonal")
    if tipo_nome_inexistente is None:
        print("   ✅ Retornou None para nome inexistente")
    else:
        print("   ❌ Deveria ter retornado None")
    
    # Testar atualização com ID inválido
    print("\\n4. Tentando atualizar com ID inválido:")
    tipo_invalido = TurbineType(type="Vertical", description="Teste com ID inválido")
    tipo_invalido.id = 99999  # ID que não existe
    try:
        sucesso = repo.atualizar(tipo_invalido)
        if not sucesso:
            print("   ✅ Retornou False para ID inválido")
        else:
            print("   ❌ Deveria ter retornado False")
    except ValueError as e:
        print(f"   ✅ Erro de validação capturado: {e}")
    
    # Testar exclusão com ID inválido
    print("\\n5. Tentando excluir com ID inválido:")
    sucesso_exclusao = repo.excluir(99999)
    if not sucesso_exclusao:
        print("   ✅ Retornou False para exclusão com ID inválido")
    else:
        print("   ❌ Deveria ter retornado False")
    
    print()


def main():
    """Função principal que executa todos os exemplos"""
    print("🌪️  === SISTEMA DE VALIDAÇÃO: TURBINE TYPES ===")
    print("Testando entidade TurbineType e TurbineTypeRepository")
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
        exemplo_tratamento_erros()
        
        print("🎉 === VALIDAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Todos os testes de TurbineTypes foram executados.")
        print("Verifique os resultados acima para confirmar o funcionamento.")
        
    except Exception as e:
        print(f"💥 Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
