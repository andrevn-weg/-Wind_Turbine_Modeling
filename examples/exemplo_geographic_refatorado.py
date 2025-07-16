#!/usr/bin/env python3
"""
Exemplo de uso da nova estrutura do módulo geographic

Este script demonstra como usar as entidades e repositórios separados
seguindo as melhores práticas de arquitetura de software.
"""

import sys
from pathlib import Path

# Adicionar src ao path
PROJECT_ROOT = Path(__file__).parent.parent
src_path = PROJECT_ROOT / "src"
sys.path.insert(0, str(src_path))

from geographic import Pais, Regiao, Cidade
from geographic import PaisRepository, RegiaoRepository, CidadeRepository


def exemplo_completo():
    """Demonstra o uso completo do sistema geográfico"""
    
    print("🌍 Exemplo de uso do Sistema Geográfico Refatorado")
    print("=" * 60)
    
    # Criar repositórios
    pais_repo = PaisRepository()
    regiao_repo = RegiaoRepository()
    cidade_repo = CidadeRepository()
    
    # Criar tabelas se não existirem
    print("\n📋 Criando tabelas no banco de dados...")
    pais_repo.criar_tabela()
    regiao_repo.criar_tabela()
    cidade_repo.criar_tabela()
    print("✅ Tabelas criadas com sucesso!")
    
    # 1. Criar e salvar um país (ou usar existente)
    print("\n🏳️ Criando/buscando país...")
    brasil = Pais(nome="Brasil", codigo="BR")
    
    if brasil.validar():
        # Tentar buscar primeiro
        brasil_existente = pais_repo.buscar_por_codigo("BR")
        if brasil_existente:
            brasil_id = brasil_existente.id
            print(f"✅ País já existe: {brasil_existente} (ID: {brasil_id})")
        else:
            brasil_id = pais_repo.salvar(brasil)
            print(f"✅ País salvo: {brasil} (ID: {brasil_id})")
    else:
        print("❌ Dados do país são inválidos")
        return
    
    # 2. Criar e salvar uma região (ou usar existente)
    print("\n🗺️ Criando/buscando região...")
    santa_catarina = Regiao(
        nome="Santa Catarina",
        pais_id=brasil_id,
        sigla="SC"
    )
    
    if santa_catarina.validar():
        # Tentar buscar primeira região de SC no Brasil
        regioes_sc = regiao_repo.buscar_por_sigla("SC")
        sc_existente = next((r for r in regioes_sc if r.pais_id == brasil_id), None)
        
        if sc_existente:
            sc_id = sc_existente.id
            print(f"✅ Região já existe: {sc_existente.nome_completo()} (ID: {sc_id})")
        else:
            sc_id = regiao_repo.salvar(santa_catarina)
            print(f"✅ Região salva: {santa_catarina.nome_completo()} (ID: {sc_id})")
    else:
        print("❌ Dados da região são inválidos")
        return
    
    # 3. Criar e salvar uma cidade (ou usar existente)
    print("\n🏙️ Criando/buscando cidade...")
    jaragua = Cidade(
        nome="Jaraguá do Sul",
        regiao_id=sc_id,
        pais_id=brasil_id,
        latitude=-26.4986085,
        longitude=-49.1928379,
        populacao=180000,
        altitude=45.0,
        notes="Cidade conhecida por sua forte tradição industrial"
    )
    
    if jaragua.validar():
        # Tentar buscar cidade existente
        cidades_existentes = cidade_repo.buscar_por_nome("Jaraguá do Sul")
        jaragua_existente = next((c for c in cidades_existentes if c.regiao_id == sc_id), None)
        
        if jaragua_existente:
            jaragua_id = jaragua_existente.id
            print(f"✅ Cidade já existe: {jaragua_existente.nome} (ID: {jaragua_id})")
            print(f"   📍 Coordenadas: {jaragua_existente.latitude}, {jaragua_existente.longitude}")
            jaragua = jaragua_existente  # Usar a cidade existente para os próximos exemplos
        else:
            jaragua_id = cidade_repo.salvar(jaragua)
            print(f"✅ Cidade salva: {jaragua.nome} (ID: {jaragua_id})")
            print(f"   📍 Coordenadas: {jaragua.latitude}, {jaragua.longitude}")
            print(f"   👥 População: {jaragua.populacao:,} habitantes")
    else:
        print("❌ Dados da cidade são inválidos")
        return
    
    # 4. Demonstrar consultas
    print("\n🔍 Realizando consultas...")
    
    # Buscar país por código
    brasil_encontrado = pais_repo.buscar_por_codigo("BR")
    print(f"   País encontrado por código: {brasil_encontrado}")
    
    # Buscar regiões do país
    regioes_brasil = regiao_repo.buscar_por_pais(brasil_id)
    print(f"   Regiões do Brasil: {[r.nome_completo() for r in regioes_brasil]}")
    
    # Buscar cidades da região
    cidades_sc = cidade_repo.buscar_por_regiao(sc_id)
    print(f"   Cidades de SC: {[c.nome for c in cidades_sc]}")
    
    # Buscar cidades próximas
    cidades_proximas = cidade_repo.buscar_proximas(
        latitude=-26.5, 
        longitude=-49.2, 
        raio_km=50
    )
    print(f"   Cidades próximas a Jaraguá: {[c.nome for c in cidades_proximas]}")
    
    # 5. Demonstrar validações
    print("\n✅ Demonstrando validações...")
    
    # Cidade inválida (sem nome)
    cidade_invalida = Cidade(latitude=-26.5, longitude=-49.2)
    print(f"   Cidade sem nome é válida? {cidade_invalida.validar()}")
    
    # País inválido (código com tamanho errado)
    pais_invalido = Pais(nome="Teste", codigo="BRASIL")  # Deve ter 2 caracteres
    print(f"   País com código inválido é válido? {pais_invalido.validar()}")
    
    # 6. Demonstrar métodos utilitários
    print("\n🛠️ Métodos utilitários...")
    
    # Distância entre cidades (se tivéssemos outra cidade)
    cidade_exemplo = Cidade(
        nome="Blumenau",
        latitude=-26.9194,
        longitude=-49.0661
    )
    
    distancia = jaragua.distancia_aproximada(cidade_exemplo)
    print(f"   Distância aproximada Jaraguá ↔ Blumenau: {distancia:.1f} km")
    
    # Conversão para dicionário
    jaragua_dict = jaragua.to_dict()
    print(f"   Cidade como dicionário: {jaragua_dict}")
    
    print("\n🎉 Exemplo concluído com sucesso!")
    print("=" * 60)


def exemplo_tratamento_erros():
    """Demonstra o tratamento de erros da nova estrutura"""
    
    print("\n🚨 Exemplo de tratamento de erros")
    print("-" * 40)
    
    repo = CidadeRepository()
    repo.criar_tabela()
    
    # Tentar salvar cidade inválida
    cidade_invalida = Cidade(nome="", latitude=200)  # Latitude inválida
    
    try:
        repo.salvar(cidade_invalida)
    except ValueError as e:
        print(f"✅ Erro capturado corretamente: {e}")
    
    # Tentar atualizar cidade sem ID
    cidade_sem_id = Cidade(nome="Teste", latitude=-26.5, longitude=-49.2)
    
    try:
        repo.atualizar(cidade_sem_id)
    except ValueError as e:
        print(f"✅ Erro capturado corretamente: {e}")


if __name__ == "__main__":
    try:
        exemplo_completo()
        exemplo_tratamento_erros()
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
