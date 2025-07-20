#!/usr/bin/env python3
"""
Teste rápido das APIs meteorológicas

Este script executa testes básicos das APIs Open-Meteo e NASA POWER
para validar que as implementações estão funcionando corretamente.

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os
from datetime import date, timedelta

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.open_meteo import OpenMeteoClient
from meteorological.api.nasa_power import NASAPowerClient


def testar_open_meteo():
    """Teste rápido da API Open-Meteo"""
    print("🌍 === TESTE RÁPIDO - OPEN-METEO ===")
    
    try:
        client = OpenMeteoClient()
        
        # Teste 1: Informações da API
        info = client.obter_informacoes_api()
        print(f"✅ Informações obtidas: {info['nome']}")
        print(f"📏 Alturas suportadas: {info['alturas_suportadas']}")
        
        # Teste 2: Validação de altura
        try:
            client.validar_altura(10)
            print("✅ Validação de altura funcional")
        except:
            print("❌ Erro na validação de altura")
        
        # Teste 3: Requisição pequena (apenas 1 dia)
        print("⏳ Testando requisição pequena...")
        dados = client.obter_dados_historicos_vento(
            latitude=-30.0346,  # Porto Alegre
            longitude=-51.2177,
            data_inicio=date(2024, 6, 1),
            data_fim=date(2024, 6, 1),  # Apenas 1 dia
            alturas=[10]  # Apenas uma altura
        )
        
        if dados and 'metadata' in dados:
            print(f"✅ Requisição bem-sucedida: {dados['metadata']['total_registros']} registros")
            return True
        else:
            print("❌ Requisição falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste Open-Meteo: {e}")
        return False


def testar_nasa_power():
    """Teste rápido da API NASA POWER"""
    print("\n🛰️ === TESTE RÁPIDO - NASA POWER ===")
    
    try:
        client = NASAPowerClient()
        
        # Teste 1: Informações da API
        info = client.obter_informacoes_api()
        print(f"✅ Informações obtidas: {info['nome']}")
        print(f"📏 Alturas suportadas: {info['alturas_suportadas']}")
        
        # Teste 2: Parâmetros disponíveis
        parametros = client.obter_parametros_disponiveis()
        print(f"✅ Parâmetros disponíveis: {list(parametros.keys())}")
        
        # Teste 3: Verificação de período
        verificacao = client.verificar_disponibilidade_periodo(
            date(2023, 1, 1), 
            date(2023, 1, 7)
        )
        print(f"✅ Verificação de período funcional: {verificacao['disponivel']}")
        
        # Teste 4: Requisição pequena (apenas 3 dias)
        print("⏳ Testando requisição pequena... (pode demorar)")
        dados = client.obter_dados_historicos_vento(
            latitude=-15.7801,  # Brasília
            longitude=-47.9292,
            data_inicio=date(2023, 6, 1),
            data_fim=date(2023, 6, 3),  # Apenas 3 dias
            alturas=[10]  # Apenas uma altura
        )
        
        if dados and 'metadata' in dados:
            print(f"✅ Requisição bem-sucedida: {dados['metadata']['total_registros']} registros")
            return True
        else:
            print("❌ Requisição falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste NASA POWER: {e}")
        print("💡 Nota: NASA POWER pode estar temporariamente indisponível")
        return False


def testar_validacoes():
    """Testa validações dos clientes"""
    print("\n🧪 === TESTE DE VALIDAÇÕES ===")
    
    # Open-Meteo
    print("🌍 Open-Meteo:")
    client_om = OpenMeteoClient()
    
    try:
        client_om.validar_altura(25)  # Deve dar erro
        print("❌ Validação falhou (deveria rejeitar altura 25m)")
    except ValueError:
        print("✅ Validação de altura funcionando")
    
    # NASA POWER
    print("🛰️ NASA POWER:")
    client_nasa = NASAPowerClient()
    
    try:
        client_nasa.validar_altura(80)  # Deve dar erro
        print("❌ Validação falhou (deveria rejeitar altura 80m)")
    except ValueError:
        print("✅ Validação de altura funcionando")


def main():
    """Função principal de teste"""
    print("🧪 === TESTE RÁPIDO DAS APIS METEOROLÓGICAS ===")
    print("Sistema de Simulação de Turbinas Eólicas\n")
    
    resultados = {
        'open_meteo': False,
        'nasa_power': False
    }
    
    # Testar Open-Meteo
    resultados['open_meteo'] = testar_open_meteo()
    
    # Testar NASA POWER
    resultados['nasa_power'] = testar_nasa_power()
    
    # Testar validações
    testar_validacoes()
    
    # Resumo
    print(f"\n📊 === RESUMO DOS TESTES ===")
    print(f"🌍 Open-Meteo: {'✅ Funcionando' if resultados['open_meteo'] else '❌ Com problemas'}")
    print(f"🛰️ NASA POWER: {'✅ Funcionando' if resultados['nasa_power'] else '❌ Com problemas'}")
    
    total_funcionando = sum(resultados.values())
    print(f"\n🎯 Total: {total_funcionando}/2 APIs funcionando")
    
    if total_funcionando == 2:
        print("🎉 Todas as APIs estão funcionais!")
    elif total_funcionando == 1:
        print("⚠️ Uma API com problemas - verifique conectividade")
    else:
        print("❌ Problemas nas APIs - verifique configuração e conectividade")
    
    print("\n💡 Para testes completos, execute:")
    print("   python examples/example_open_meteo.py")
    print("   python examples/example_nasa_power.py")


if __name__ == "__main__":
    main()
