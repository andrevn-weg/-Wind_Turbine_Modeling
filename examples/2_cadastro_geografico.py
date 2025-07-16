"""
Exemplo de como criar e salvar registros geográficos (País, Região e Cidade)
utilizando os modelos implementados no projeto Wind Turbine Modeling.

Este script demonstra:
1. Como criar instâncias de País, Região e Cidade
2. Como salvar esses dados no banco de dados SQLite
3. Como buscar os dados salvos

Autor: André Vinícius
Data: 17 de Maio de 2025
"""

import sys
import os

# Adiciona o diretório raiz do projeto ao path para importação dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importações dos modelos
from pais.models import Pais, PaisModel
from regiao.models import Regiao, RegiaoModel
from cidade.models import Cidade, CidadeModel

# Função para demonstrar a criação de um país
def cadastrar_pais():
    print("\n=== Cadastrando país ===")
    # Criando uma instância do modelo de País
    pais_model = PaisModel()
    
    # Criando a tabela de países se não existir
    pais_model.criar_tabela()
    
    # Criando uma instância de País
    brasil = Pais(
        nome="Brasil",
        codigo="BR"
    )
    
    # Salvando no banco de dados
    brasil_id = pais_model.adicionar(brasil)
    print(f"País cadastrado com ID: {brasil_id}")
    
    # Buscando o país pelo ID para confirmar o salvamento
    pais_salvo = pais_model.buscar_por_id(brasil_id)
    print(f"País recuperado do banco: {pais_salvo}")
    
    return brasil_id

# Função para demonstrar a criação de uma região
def cadastrar_regiao(pais_id):
    print("\n=== Cadastrando região ===")
    # Criando uma instância do modelo de Região
    regiao_model = RegiaoModel()
    
    # Criando a tabela de regiões se não existir
    regiao_model.criar_tabela()
    
    # Criando uma instância de Região
    santa_catarina = Regiao(
        nome="Santa Catarina",
        pais_id=pais_id,
        sigla="SC"
    )
    
    # Salvando no banco de dados
    sc_id = regiao_model.adicionar(santa_catarina)
    print(f"Região cadastrada com ID: {sc_id}")
    
    # Buscando a região pelo ID para confirmar o salvamento
    regiao_salva = regiao_model.buscar_por_id(sc_id)
    print(f"Região recuperada do banco: {regiao_salva}")
    
    return sc_id

# Função para demonstrar a criação de uma cidade
def cadastrar_cidade(pais_id, regiao_id):
    print("\n=== Cadastrando cidade ===")
    # Criando uma instância do modelo de Cidade
    cidade_model = CidadeModel()
    
    # Criando a tabela de cidades se não existir
    cidade_model.criar_tabela()
    
    # Criando uma instância de Cidade
    jaragua = Cidade(
        nome="Jaraguá do Sul",
        regiao_id=regiao_id,
        pais_id=pais_id,
        latitude=-26.4869,
        longitude=-49.0679,
        populacao=180000,
        altitude=29.0,
        notes="Cidade polo industrial de Santa Catarina, com grande potencial eólico no Morro das Antenas."
    )
    
    # Salvando no banco de dados
    jaragua_id = cidade_model.adicionar(jaragua)
    print(f"Cidade cadastrada com ID: {jaragua_id}")
    
    # Buscando a cidade pelo ID para confirmar o salvamento
    cidade_salva = cidade_model.buscar_por_id(jaragua_id)
    print(f"Cidade recuperada do banco: {cidade_salva}")
    
    return jaragua_id

# Função para buscar a cidade mais próxima de um ponto geográfico
def demonstrar_busca_geografica():
    print("\n=== Buscando cidades próximas ===")
    cidade_model = CidadeModel()
    
    # Coordenadas do ponto de referência (Joinville)
    latitude = -26.3045
    longitude = -48.8487
    raio_km = 50.0  # Raio de busca em km
    
    print(f"Buscando cidades em um raio de {raio_km}km das coordenadas ({latitude}, {longitude}):")
    cidades_proximas = cidade_model.buscar_proximas(latitude, longitude, raio_km)
    
    if cidades_proximas:
        for cidade in cidades_proximas:
            print(f"- {cidade}")
    else:
        print("Nenhuma cidade encontrada neste raio.")

# Função principal para executar o exemplo
def main():
    print("===== Exemplo: Cadastro Geográfico =====")
    print("Demonstração de criação e consulta de dados geográficos")
    
    # Cadastrando os registros
    pais_id = cadastrar_pais()
    regiao_id = cadastrar_regiao(pais_id)
    cidade_id = cadastrar_cidade(pais_id, regiao_id)
    
    # Demonstrando funcionalidade avançada
    demonstrar_busca_geografica()
    
    print("\nExemplo concluído com sucesso!")

# Executar o exemplo quando o script for chamado diretamente
if __name__ == "__main__":
    main()
