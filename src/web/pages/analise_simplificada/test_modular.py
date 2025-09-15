"""
Teste para verificar se a modularização da análise simplificada está funcionando corretamente.
"""

import sys
import os

# Adicionar diretório atual ao path para imports relativos
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

def test_imports():
    """
    Testa se todos os módulos podem ser importados corretamente.
    """
    try:
        print("🔄 Testando imports dos módulos...")
        
        # Testar imports individuais usando imports relativos
        from config import OPCOES_FONTE_DADOS, TIPOS_TERRENO
        print("✅ config.py importado com sucesso")
        
        from data_processor import obter_mapeamento_fontes_correto
        print("✅ data_processor.py importado com sucesso")
        
        from wind_profile import calcular_velocidade_corrigida
        print("✅ wind_profile.py importado com sucesso")
        
        from display_utils import exibir_valores_referencia_api
        print("✅ display_utils.py importado com sucesso")
        
        print("\n📊 Testando constantes...")
        print(f"Opções de fonte: {OPCOES_FONTE_DADOS}")
        print(f"Tipos de terreno disponíveis: {len(TIPOS_TERRENO)}")
        
        print("\n🧮 Testando função de cálculo...")
        velocidade_teste = calcular_velocidade_corrigida(10.0, 10.0, 80.0, 0.20, "power_law")
        print(f"Teste de cálculo: 10 m/s a 10m → {velocidade_teste:.2f} m/s a 80m")
        
        print("\n✅ Todos os testes de modularização passaram!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False


def test_source_mapping():
    """
    Testa o mapeamento de fontes corrigido.
    """
    try:
        print("\n🔄 Testando mapeamento de fontes...")
        
        from data_processor import obter_mapeamento_fontes_correto
        
        # Simular objetos de fonte
        class MockSource:
            def __init__(self, id, name):
                self.id = id
                self.name = name
        
        sources = [
            MockSource(1, "NASA_POWER"),
            MockSource(2, "OPEN_METEO")
        ]
        
        source_map = obter_mapeamento_fontes_correto(sources)
        print(f"Mapeamento criado: {source_map}")
        
        # Verificar se as chaves corretas existem
        assert 'nasa_power' in source_map
        assert 'openmeteo' in source_map
        
        print("✅ Mapeamento de fontes funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de mapeamento: {e}")
        return False


def test_wind_calculations():
    """
    Testa os cálculos de perfil de vento.
    """
    try:
        print("\n🔄 Testando cálculos de perfil de vento...")
        
        from wind_profile import (
            calcular_perfil_potencia,
            calcular_perfil_logaritmico,
            validar_parametros_perfil,
            comparar_metodos_perfil
        )
        
        # Teste Lei da Potência
        v_power = calcular_perfil_potencia(10.0, 10.0, 80.0, 0.20)
        print(f"Lei da Potência: 10 m/s (10m) → {v_power:.2f} m/s (80m)")
        
        # Teste Perfil Logarítmico
        v_log = calcular_perfil_logaritmico(10.0, 10.0, 80.0, 0.1)
        print(f"Perfil Logarítmico: 10 m/s (10m) → {v_log:.2f} m/s (80m)")
        
        # Teste validação
        valido, mensagem = validar_parametros_perfil(10.0, 10.0, 80.0, 0.20)
        print(f"Validação de parâmetros: {valido} - {mensagem}")
        
        # Teste comparação
        comparacao = comparar_metodos_perfil(10.0, 10.0, 80.0, 0.20, 0.1)
        print(f"Comparação de métodos: Power={comparacao['power_law']:.2f}, Log={comparacao['logarithmic']:.2f}")
        
        print("✅ Cálculos de perfil de vento funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos cálculos de vento: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Iniciando testes de modularização da análise simplificada...\n")
    
    success = True
    success &= test_imports()
    success &= test_source_mapping()
    success &= test_wind_calculations()
    
    if success:
        print("\n🎉 Todos os testes passaram! A modularização está funcionando corretamente.")
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
    
    print("\n📁 Estrutura de arquivos criada:")
    print("📂 analise_simplificada/")
    print("├── 📄 __init__.py")
    print("├── 📄 config.py          # Configurações e constantes")
    print("├── 📄 data_processor.py  # Processamento de dados")
    print("├── 📄 wind_profile.py    # Cálculos de perfil de vento")
    print("├── 📄 display_utils.py   # Visualização e exibição")
    print("├── 📄 main_modular.py    # Aplicação principal modular")
    print("└── 📄 test_modular.py    # Arquivo de testes")
    
    print("\n💡 Próximos passos:")
    print("1. Integrar a versão modular com o arquivo original")
    print("2. Corrigir problemas de source filtering e grouping")
    print("3. Testar com dados reais do banco")
    print("4. Substituir arquivo original pela versão modular")