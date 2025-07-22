#!/usr/bin/env python3
"""
Teste da Interface de Cadastro Meteorológico

Este script testa os módulos da interface de cadastro de dados meteorológicos
para garantir que todas as importações e funcionalidades básicas estão funcionando.

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path para importações
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def testar_importacoes():
    """Testa se todas as importações necessárias funcionam"""
    print("🧪 === TESTE DE IMPORTAÇÕES ===")
    
    try:
        # Testar importações do módulo meteorológico
        print("⏳ Testando módulo meteorológico...")
        from meteorological.meteorological_data_source.entity import MeteorologicalDataSource
        from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
        from meteorological.meteorological_data.entity import MeteorologicalData
        from meteorological.meteorological_data.repository import MeteorologicalDataRepository
        from meteorological.api.nasa_power import NASAPowerClient
        from meteorological.api.open_meteo import OpenMeteoClient
        print("✅ Módulo meteorológico OK")
        
        # Testar importações do módulo geográfico
        print("⏳ Testando módulo geográfico...")
        from geographic import CidadeRepository, RegiaoRepository, PaisRepository
        print("✅ Módulo geográfico OK")
        
        # Testar importações das interfaces
        print("⏳ Testando interfaces meteorológicas...")
        from web.pages.meteorological_registration.create_meteorological_data_source import create_meteorological_data_source
        from web.pages.meteorological_registration.create_meteorological_data import create_meteorological_data
        print("✅ Interfaces meteorológicas OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def testar_entidades():
    """Testa a criação e validação das entidades"""
    print("\n🏗️ === TESTE DE ENTIDADES ===")
    
    try:
        from meteorological.meteorological_data_source.entity import MeteorologicalDataSource
        from meteorological.meteorological_data.entity import MeteorologicalData
        from datetime import datetime, date
        
        # Testar MeteorologicalDataSource
        print("⏳ Testando MeteorologicalDataSource...")
        fonte = MeteorologicalDataSource(
            name="TESTE_API",
            description="API de teste para validação"
        )
        
        if fonte.validar():
            print("✅ MeteorologicalDataSource válida")
        else:
            print("❌ MeteorologicalDataSource inválida")
            return False
        
        # Testar MeteorologicalData
        print("⏳ Testando MeteorologicalData...")
        dado = MeteorologicalData(
            cidade_id=1,
            meteorological_data_source_id=1,
            data=date.today(),
            velocidade_vento=5.5,
            altura_captura=10,
            created_at=datetime.now()
        )
        
        if dado.validar():
            print("✅ MeteorologicalData válido")
        else:
            print("❌ MeteorologicalData inválido")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar entidades: {e}")
        return False


def testar_repositorios():
    """Testa a inicialização dos repositórios"""
    print("\n🗄️ === TESTE DE REPOSITÓRIOS ===")
    
    try:
        from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
        from meteorological.meteorological_data.repository import MeteorologicalDataRepository
        
        # Testar repositório de fontes
        print("⏳ Testando MeteorologicalDataSourceRepository...")
        fonte_repo = MeteorologicalDataSourceRepository()
        print("✅ MeteorologicalDataSourceRepository OK")
        
        # Testar repositório de dados
        print("⏳ Testando MeteorologicalDataRepository...")
        dados_repo = MeteorologicalDataRepository()
        print("✅ MeteorologicalDataRepository OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar repositórios: {e}")
        return False


def testar_apis():
    """Testa a inicialização dos clientes das APIs"""
    print("\n🌐 === TESTE DE CLIENTES API ===")
    
    try:
        from meteorological.api.nasa_power import NASAPowerClient
        from meteorological.api.open_meteo import OpenMeteoClient
        
        # Testar NASA POWER
        print("⏳ Testando NASAPowerClient...")
        nasa_client = NASAPowerClient()
        info_nasa = nasa_client.obter_informacoes_api()
        print(f"✅ NASA POWER: {info_nasa['nome']}")
        
        # Testar Open-Meteo
        print("⏳ Testando OpenMeteoClient...")
        meteo_client = OpenMeteoClient()
        info_meteo = meteo_client.obter_informacoes_api()
        print(f"✅ Open-Meteo: {info_meteo['nome']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar APIs: {e}")
        return False


def testar_funcoes_interface():
    """Testa se as funções das interfaces podem ser chamadas"""
    print("\n🖥️ === TESTE DE INTERFACES ===")
    
    try:
        # Importar as funções
        from web.pages.meteorological_registration.create_meteorological_data_source import create_meteorological_data_source
        from web.pages.meteorological_registration.create_meteorological_data import create_meteorological_data
        
        print("✅ Funções de interface importadas com sucesso")
        print("⚠️ Nota: Testes completos da interface requerem Streamlit em execução")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar interfaces: {e}")
        return False


def main():
    """Função principal de teste"""
    print("🧪 === TESTE DA INTERFACE DE CADASTRO METEOROLÓGICO ===")
    print("Sistema de Simulação de Turbinas Eólicas\n")
    
    resultados = {
        'importacoes': False,
        'entidades': False,
        'repositorios': False,
        'apis': False,
        'interfaces': False
    }
    
    # Executar testes
    resultados['importacoes'] = testar_importacoes()
    
    if resultados['importacoes']:
        resultados['entidades'] = testar_entidades()
        resultados['repositorios'] = testar_repositorios()
        resultados['apis'] = testar_apis()
        resultados['interfaces'] = testar_funcoes_interface()
    
    # Resumo
    print(f"\n📊 === RESUMO DOS TESTES ===")
    print(f"📦 Importações: {'✅ OK' if resultados['importacoes'] else '❌ FALHA'}")
    print(f"🏗️ Entidades: {'✅ OK' if resultados['entidades'] else '❌ FALHA'}")
    print(f"🗄️ Repositórios: {'✅ OK' if resultados['repositorios'] else '❌ FALHA'}")
    print(f"🌐 APIs: {'✅ OK' if resultados['apis'] else '❌ FALHA'}")
    print(f"🖥️ Interfaces: {'✅ OK' if resultados['interfaces'] else '❌ FALHA'}")
    
    total_funcionando = sum(resultados.values())
    print(f"\n🎯 Total: {total_funcionando}/5 módulos funcionando")
    
    if total_funcionando == 5:
        print("🎉 Todos os módulos estão funcionais!")
        print("\n🚀 Para testar a interface completa, execute:")
        print("   streamlit run src/web/pages/meteorological_registration.py")
    elif total_funcionando >= 3:
        print("⚠️ Alguns módulos com problemas - verifique as dependências")
    else:
        print("❌ Muitos problemas encontrados - verifique a configuração")
    
    print("\n💡 Estrutura criada:")
    print("   📁 src/web/pages/meteorological_registration.py")
    print("   📁 src/web/pages/meteorological_registration/")
    print("      ├── create_meteorological_data_source.py")
    print("      └── create_meteorological_data.py")


if __name__ == "__main__":
    main()
