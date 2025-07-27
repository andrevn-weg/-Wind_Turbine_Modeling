#!/usr/bin/env python3
"""
Exemplo 5 - Teste e Validação de Manufacturers (Fabricantes de Turbinas)

Este exemplo demonstra o uso completo da entidade Manufacturer e seu repositório,
incluindo operações CRUD, validações e consultas especializadas.

Funcionalidades demonstradas:
- Criação e validação de fabricantes
- Operações CRUD (Create, Read, Update, Delete)
- Consultas por nome, país e termo
- Listagem de países únicos
- Contagem de registros
- Tratamento de erros e validações

Autor: andrevn
Data: 2025-01-27
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turbine_parameters.manufacturers import Manufacturer, ManufacturerRepository


def configurar_base_de_dados():
    """Cria as tabelas necessárias se não existirem"""
    print("🔧 Configurando base de dados...")
    
    repo = ManufacturerRepository()
    repo.criar_tabela()
    
    print("✅ Tabela de fabricantes criada/verificada com sucesso!")
    print()


def exemplo_criacao_fabricantes():
    """Demonstra a criação de fabricantes com validações"""
    print("📦 === EXEMPLO: Criação de Fabricantes ===")
    
    repo = ManufacturerRepository()
    
    # Fabricantes de exemplo com dados reais
    fabricantes_exemplo = [
        {
            "name": "Vestas Wind Systems",
            "country": "Denmark",
            "official_website": "https://www.vestas.com"
        },
        {
            "name": "General Electric",
            "country": "United States",
            "official_website": "https://www.ge.com/renewableenergy"
        },
        {
            "name": "Siemens Gamesa",
            "country": "Spain",
            "official_website": "https://www.siemensgamesa.com"
        },
        {
            "name": "Goldwind",
            "country": "China",
            "official_website": "https://www.goldwindamericas.com"
        },
        {
            "name": "Enercon",
            "country": "Germany",
            "official_website": "https://www.enercon.de"
        }
    ]
    
    fabricantes_salvos = []
    
    for dados in fabricantes_exemplo:
        try:
            # Verificar se já existe
            if not repo.existe_nome(dados["name"]):
                manufacturer = Manufacturer(
                    name=dados["name"],
                    country=dados["country"],
                    official_website=dados["official_website"]
                )
                
                manufacturer_id = repo.salvar(manufacturer)
                fabricantes_salvos.append(manufacturer)
                
                print(f"✅ Fabricante salvo: {manufacturer.name} (ID: {manufacturer_id})")
            else:
                print(f"⚠️  Fabricante já existe: {dados['name']}")
                
        except ValueError as e:
            print(f"❌ Erro ao salvar {dados['name']}: {e}")
    
    print(f"\n📊 Total de fabricantes salvos nesta execução: {len(fabricantes_salvos)}")
    print()
    
    return fabricantes_salvos


def exemplo_validacoes():
    """Demonstra validações da entidade Manufacturer"""
    print("🔍 === EXEMPLO: Validações de Fabricantes ===")
    
    # Teste 1: Nome obrigatório
    try:
        manufacturer = Manufacturer(name="", country="Denmark")
        print("❌ Deveria ter dado erro para nome vazio")
    except ValueError as e:
        print(f"✅ Validação nome vazio: {e}")
    
    # Teste 2: Nome muito longo
    try:
        manufacturer = Manufacturer(name="A" * 300, country="Denmark")
        print("❌ Deveria ter dado erro para nome muito longo")
    except ValueError as e:
        print(f"✅ Validação nome longo: {e}")
    
    # Teste 3: País muito longo
    try:
        manufacturer = Manufacturer(
            name="Teste",
            country="A" * 150,
            official_website="https://teste.com"
        )
        print("❌ Deveria ter dado erro para país muito longo")
    except ValueError as e:
        print(f"✅ Validação país longo: {e}")
    
    # Teste 4: Website muito longo
    try:
        manufacturer = Manufacturer(
            name="Teste",
            country="Denmark",
            official_website="https://" + "a" * 500 + ".com"
        )
        print("❌ Deveria ter dado erro para website muito longo")
    except ValueError as e:
        print(f"✅ Validação website longo: {e}")
    
    # Teste 5: Fabricante válido
    try:
        manufacturer = Manufacturer(
            name="Teste Válido",
            country="Denmark",
            official_website="https://teste.com"
        )
        print(f"✅ Fabricante válido criado: {manufacturer.name}")
    except ValueError as e:
        print(f"❌ Erro inesperado: {e}")
    
    print()


def exemplo_operacoes_crud():
    """Demonstra operações CRUD completas"""
    print("🔄 === EXEMPLO: Operações CRUD ===")
    
    repo = ManufacturerRepository()
    
    # CREATE - Criar um fabricante de teste
    print("1. CREATE - Criando fabricante de teste...")
    test_manufacturer = Manufacturer(
        name="WEG S.A.",
        country="Brazil",
        official_website="https://www.weg.net"
    )
    
    try:
        if not repo.existe_nome(test_manufacturer.name):
            manufacturer_id = repo.salvar(test_manufacturer)
            print(f"✅ Fabricante criado com ID: {manufacturer_id}")
        else:
            # Se já existe, buscar o existente
            test_manufacturer = repo.buscar_por_nome(test_manufacturer.name)
            manufacturer_id = test_manufacturer.id
            print(f"⚠️  Fabricante já existe com ID: {manufacturer_id}")
    except ValueError as e:
        print(f"❌ Erro ao criar: {e}")
        return
    
    # READ - Ler o fabricante
    print("\\n2. READ - Buscando fabricante...")
    manufacturer_encontrado = repo.buscar_por_id(manufacturer_id)
    if manufacturer_encontrado:
        print(f"✅ Fabricante encontrado: {manufacturer_encontrado.name}")
        print(f"   País: {manufacturer_encontrado.country}")
        print(f"   Website: {manufacturer_encontrado.official_website}")
    else:
        print("❌ Fabricante não encontrado")
        return
    
    # UPDATE - Atualizar o fabricante
    print("\\n3. UPDATE - Atualizando fabricante...")
    manufacturer_encontrado.country = "Brasil"
    manufacturer_encontrado.official_website = "https://www.weg.net/institucional"
    
    try:
        sucesso = repo.atualizar(manufacturer_encontrado)
        if sucesso:
            print("✅ Fabricante atualizado com sucesso")
            # Verificar a atualização
            manufacturer_atualizado = repo.buscar_por_id(manufacturer_id)
            print(f"   País atualizado: {manufacturer_atualizado.country}")
        else:
            print("❌ Falha ao atualizar fabricante")
    except ValueError as e:
        print(f"❌ Erro ao atualizar: {e}")
    
    # DELETE - Pergunta ao usuário se deseja excluir
    print("\\n4. DELETE - Excluindo fabricante de teste...")
    resposta = input("Deseja excluir o fabricante de teste? (s/N): ").strip().lower()
    
    if resposta == 's':
        sucesso = repo.excluir(manufacturer_id)
        if sucesso:
            print("✅ Fabricante excluído com sucesso")
        else:
            print("❌ Falha ao excluir fabricante")
    else:
        print("⚠️  Fabricante de teste mantido no banco")
    
    print()


def exemplo_consultas_especializadas():
    """Demonstra consultas especializadas"""
    print("🔍 === EXEMPLO: Consultas Especializadas ===")
    
    repo = ManufacturerRepository()
    
    # Listar todos os fabricantes
    print("1. Listando todos os fabricantes:")
    todos_fabricantes = repo.listar_todos()
    for manufacturer in todos_fabricantes:
        print(f"   • {manufacturer.name} ({manufacturer.country})")
    
    # Buscar por país
    print("\\n2. Fabricantes da Dinamarca:")
    fabricantes_dinamarca = repo.buscar_por_pais("Denmark")
    for manufacturer in fabricantes_dinamarca:
        print(f"   • {manufacturer.name} - {manufacturer.official_website}")
    
    # Buscar por termo
    print("\\n3. Fabricantes com 'Wind' no nome:")
    fabricantes_wind = repo.buscar_por_termo("Wind")
    for manufacturer in fabricantes_wind:
        print(f"   • {manufacturer.name} ({manufacturer.country})")
    
    # Listar países únicos
    print("\\n4. Países únicos dos fabricantes:")
    paises = repo.listar_paises()
    for pais in paises:
        print(f"   • {pais}")
    
    # Estatísticas
    print("\\n5. Estatísticas:")
    total = repo.contar_total()
    print(f"   • Total de fabricantes cadastrados: {total}")
    
    print()


def exemplo_conversao_dados():
    """Demonstra conversão de dados (to_dict/from_dict)"""
    print("🔄 === EXEMPLO: Conversão de Dados ===")
    
    # Criar um fabricante
    manufacturer = Manufacturer(
        name="Nordex SE",
        country="Germany",
        official_website="https://www.nordex-online.com"
    )
    
    # Converter para dicionário
    print("1. Convertendo entidade para dicionário:")
    manufacturer_dict = manufacturer.to_dict()
    for key, value in manufacturer_dict.items():
        print(f"   {key}: {value}")
    
    # Converter de volta para entidade
    print("\\n2. Convertendo dicionário de volta para entidade:")
    manufacturer_from_dict = Manufacturer.from_dict(manufacturer_dict)
    print(f"   Nome: {manufacturer_from_dict.name}")
    print(f"   País: {manufacturer_from_dict.country}")
    print(f"   Website: {manufacturer_from_dict.official_website}")
    
    print()


def exemplo_tratamento_erros():
    """Demonstra tratamento de erros e situações especiais"""
    print("⚠️  === EXEMPLO: Tratamento de Erros ===")
    
    repo = ManufacturerRepository()
    
    # Tentativa de salvar fabricante duplicado
    print("1. Tentando salvar fabricante com nome duplicado:")
    try:
        manufacturer1 = Manufacturer(
            name="Fabricante Teste Duplicado",
            country="Test Country"
        )
        # Salvar o primeiro (deve funcionar)
        if not repo.existe_nome(manufacturer1.name):
            repo.salvar(manufacturer1)
            print("   ✅ Primeiro fabricante salvo")
        
        # Tentar salvar o segundo com mesmo nome (deve dar erro)
        manufacturer2 = Manufacturer(
            name="Fabricante Teste Duplicado",
            country="Another Country"
        )
        repo.salvar(manufacturer2)
        print("   ❌ Deveria ter dado erro para nome duplicado")
    except ValueError as e:
        print(f"   ✅ Erro capturado corretamente: {e}")
    
    # Buscar fabricante inexistente
    print("\\n2. Buscando fabricante inexistente:")
    manufacturer_inexistente = repo.buscar_por_id(99999)
    if manufacturer_inexistente is None:
        print("   ✅ Retornou None para fabricante inexistente")
    else:
        print("   ❌ Deveria ter retornado None")
    
    # Buscar por nome inexistente
    print("\\n3. Buscando por nome inexistente:")
    manufacturer_nome_inexistente = repo.buscar_por_nome("Fabricante Inexistente XYZ")
    if manufacturer_nome_inexistente is None:
        print("   ✅ Retornou None para nome inexistente")
    else:
        print("   ❌ Deveria ter retornado None")
    
    print()


def main():
    """Função principal que executa todos os exemplos"""
    print("🌪️  === SISTEMA DE VALIDAÇÃO: MANUFACTURERS ===")
    print("Testando entidade Manufacturer e ManufacturerRepository")
    print("=" * 60)
    print()
    
    try:
        # Configurar base de dados
        configurar_base_de_dados()
        
        # Executar exemplos
        exemplo_validacoes()
        fabricantes_salvos = exemplo_criacao_fabricantes()
        exemplo_operacoes_crud()
        exemplo_consultas_especializadas()
        exemplo_conversao_dados()
        exemplo_tratamento_erros()
        
        print("🎉 === VALIDAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Todos os testes de Manufacturers foram executados.")
        print("Verifique os resultados acima para confirmar o funcionamento.")
        
    except Exception as e:
        print(f"💥 Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
