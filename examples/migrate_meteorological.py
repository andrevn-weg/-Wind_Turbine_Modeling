#!/usr/bin/env python3
"""
Script de migração do banco de dados para o módulo meteorológico

Este script cria as tabelas meteorológicas e popula com dados iniciais básicos.
Deve ser executado uma vez para configurar o banco de dados.

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological import (
    MeteorologicalDataSourceRepository,
    MeteorologicalDataRepository,
    MeteorologicalDataSource
)


def criar_tabelas():
    """Cria as tabelas meteorológicas"""
    print("🔧 Criando tabelas meteorológicas...")
    
    fonte_repo = MeteorologicalDataSourceRepository()
    dados_repo = MeteorologicalDataRepository()
    
    # Criar tabelas
    fonte_repo.criar_tabela()
    dados_repo.criar_tabela()
    
    print("✅ Tabelas criadas com sucesso!")


def popular_fontes_basicas():
    """Popula o banco com fontes de dados meteorológicos básicas"""
    print("📊 Populando fontes de dados básicas...")
    
    repo = MeteorologicalDataSourceRepository()
    
    fontes_basicas = [
        MeteorologicalDataSource(
            name="NASA_POWER",
            description="NASA Prediction of Worldwide Energy Resources - Dados satelitais globais de energia solar e meteorologia"
        ),
        MeteorologicalDataSource(
            name="INMET",
            description="Instituto Nacional de Meteorologia - Dados meteorológicos oficiais do Brasil"
        ),
        MeteorologicalDataSource(
            name="OPEN_METEO",
            description="Open-Meteo API - Dados meteorológicos históricos e previsões de código aberto"
        ),
        MeteorologicalDataSource(
            name="MANUAL",
            description="Dados inseridos manualmente através da interface do sistema"
        )
    ]
    
    fontes_criadas = 0
    for fonte in fontes_basicas:
        try:
            # Verificar se já existe
            fonte_existente = repo.buscar_por_nome(fonte.name)
            if not fonte_existente:
                fonte_id = repo.salvar(fonte)
                print(f"   ✅ Criada: {fonte.name} (ID: {fonte_id})")
                fontes_criadas += 1
            else:
                print(f"   ⚠️ Já existe: {fonte.name}")
        except Exception as e:
            print(f"   ❌ Erro ao criar {fonte.name}: {e}")
    
    print(f"✅ {fontes_criadas} fontes criadas!")


def main():
    """Função principal de migração"""
    print("🚀 === MIGRAÇÃO DO BANCO DE DADOS METEOROLÓGICO ===")
    print("Sistema de Simulação de Turbinas Eólicas\n")
    
    try:
        criar_tabelas()
        popular_fontes_basicas()
        
        print("\n✅ === MIGRAÇÃO CONCLUÍDA COM SUCESSO ===")
        print("🎯 Módulo meteorológico pronto para uso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
