"""
Exemplo 16: Teste Simples da Correção de Subscripting

Este exemplo reproduz exatamente o erro encontrado em results_reports.py
e demonstra que a correção está funcionando.
"""

import sys
from pathlib import Path
import numpy as np

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from analysis_tools.turbine_performance import TurbinePerformanceCalculator, TurbinePerformance
from analysis_tools.visualization import AnalysisVisualizer


def test_subscripting_fix():
    """Testa a correção do erro de subscripting do results_reports.py"""
    
    print("🔧 Teste Específico da Correção de Subscripting")
    print("=" * 50)
    
    # 1. Criar uma instância de TurbinePerformance
    calculator = TurbinePerformanceCalculator()
    turbine_specs = {
        'rated_power_kw': 1500,
        'rotor_diameter_m': 82,
        'cut_in_speed': 3.5,
        'cut_out_speed': 25.0,
        'rated_wind_speed': 12.0,
        'air_density': 1.225
    }
    
    wind_speeds = np.linspace(0, 30, 50)
    power_curve = calculator.generate_power_curve(turbine_specs, wind_speeds)
    
    print(f"✅ TurbinePerformance criado: {type(power_curve)}")
    
    # 2. Dados de vento simulados
    real_wind_speeds = np.random.weibull(2, 1000) * 8 + 2  # Distribuição Weibull típica
    real_wind_speeds = np.clip(real_wind_speeds, 0, 25)   # Limitar velocidades
    
    print(f"✅ Dados de vento simulados: {len(real_wind_speeds)} pontos")
    
    # 3. Reproduzir exatamente o código de results_reports.py
    print("\n📊 Testando o código do results_reports.py...")
    
    try:
        # Este é o código exato que estava falhando
        if hasattr(power_curve, 'wind_speeds'):
            # É um objeto TurbinePerformance
            wind_speeds_curve = power_curve.wind_speeds
            power_outputs_curve = power_curve.power_output
            print(f"✅ Acesso por atributo funcionou")
            print(f"   wind_speeds: {len(wind_speeds_curve)} pontos")
            print(f"   power_output: {len(power_outputs_curve)} valores")
        else:
            # É um dicionário
            wind_speeds_curve = power_curve.get('wind_speeds', [])
            power_outputs_curve = power_curve.get('power_output', power_curve.get('power_outputs', []))
            print(f"✅ Tratamento de dicionário disponível como fallback")
        
        # Verificar se os dados estão disponíveis
        has_wind_speeds = (hasattr(wind_speeds_curve, '__len__') and len(wind_speeds_curve) > 0) or bool(wind_speeds_curve)
        has_power_outputs = (hasattr(power_outputs_curve, '__len__') and len(power_outputs_curve) > 0) or bool(power_outputs_curve)
        
        print(f"✅ Validação de dados: wind_speeds={has_wind_speeds}, power_outputs={has_power_outputs}")
        
        # 4. Testar a visualização (onde estava o erro de subscripting)
        if has_wind_speeds and has_power_outputs:
            visualizer = AnalysisVisualizer()
            
            # Esta linha causava o erro antes da correção
            fig_power_real = visualizer.plot_power_curve_with_real_data(
                power_curve=power_curve,
                real_wind_speeds=real_wind_speeds,
                height=600
            )
            
            print("✅ Visualização gerada com sucesso!")
            print(f"   Figura: {type(fig_power_real)}")
            print(f"   Traces: {len(fig_power_real.data)}")
            
            # Salvar para verificação manual
            output_file = Path(__file__).parent / "subscripting_fix_test.html"
            fig_power_real.write_html(str(output_file))
            print(f"   Salvo em: {output_file}")
            
            return True
        else:
            print("❌ Dados incompletos")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"   Tipo: {type(e)}")
        return False


def test_before_fix_simulation():
    """Simula o que aconteceria antes da correção."""
    print("\n🔍 Simulando o Erro Original...")
    
    # Simular tentativa de acessar como dicionário
    calculator = TurbinePerformanceCalculator()
    turbine_specs = {
        'rated_power_kw': 1500,
        'rotor_diameter_m': 82,
        'cut_in_speed': 3.5,
        'cut_out_speed': 25.0
    }
    
    power_curve = calculator.generate_power_curve(turbine_specs, np.linspace(0, 30, 20))
    
    try:
        # Isso causaria o erro original
        power_output_wrong = power_curve['power_output']  # ❌ 'TurbinePerformance' object is not subscriptable
        print("❌ ERRO: Subscripting não deveria funcionar!")
    except TypeError as e:
        print(f"✅ Erro esperado capturado: {e}")
        print("   Isso confirma que TurbinePerformance não é subscriptable")
    
    try:
        # Jeito correto
        power_output_correct = power_curve.power_output  # ✅ Acesso por atributo
        print(f"✅ Acesso correto por atributo: {len(power_output_correct)} valores")
    except Exception as e:
        print(f"❌ Erro inesperado no acesso por atributo: {e}")


def main():
    """Executa todos os testes."""
    success = test_subscripting_fix()
    test_before_fix_simulation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ CORREÇÃO VALIDADA COM SUCESSO!")
        print("O erro de subscripting em results_reports.py foi corrigido.")
        print("\nResumo da correção:")
        print("- Problema: power_curve['power_output'] em visualization.py")
        print("- Solução: Usar power_output diretamente (já extraído)")
        print("- Resultado: Gráfico de curva de potência funcionando")
    else:
        print("❌ TESTE FALHOU!")
        print("A correção precisa de mais ajustes.")
    print("=" * 50)


if __name__ == "__main__":
    main()
