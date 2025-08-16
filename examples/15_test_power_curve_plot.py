"""
Exemplo 15: Teste de Geração de Gráfico da Curva de Potência

Este exemplo demonstra como:
1. Criar uma instância de TurbinePerformance corretamente
2. Gerar dados realistas de vento 
3. Plotar o gráfico de curva de potência vs dados reais
4. Verificar se não há erros de subscripting

Usado para validar a correção do erro:
"'TurbinePerformance' object is not subscriptable"
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from analysis_tools.turbine_performance import TurbinePerformanceCalculator, TurbinePerformance
from analysis_tools.visualization import AnalysisVisualizer
from analysis_tools.wind_components import WindComponentsSimulator


def create_sample_turbine_specs():
    """Cria especificações de exemplo para uma turbina."""
    return {
        'rated_power_kw': 1500,  # 1.5 MW
        'rotor_diameter_m': 82,  # 82 metros de diâmetro
        'hub_height_m': 80,      # 80 metros de altura
        'cut_in_speed': 3.5,     # m/s
        'cut_out_speed': 25.0,   # m/s
        'rated_wind_speed': 12.0,# m/s
        'air_density': 1.225,    # kg/m³
        'system_efficiency': 0.95,
        'operational_losses': 0.05,
        'gear_ratio': 95,
        'generator_efficiency': 0.96
    }


def create_sample_wind_data():
    """Cria dados de vento realistas para teste."""
    # Gerar 24 horas de dados com diferentes padrões
    num_points = 1000
    time_hours = np.linspace(0, 24, num_points)
    
    # Velocidade base variando ao longo do dia (padrão típico)
    base_wind = 8 + 3 * np.sin(2 * np.pi * time_hours / 24 - np.pi/2)  # 5-11 m/s
    
    # Adicionar turbulência e variabilidade
    turbulence = np.random.normal(0, 1.5, num_points)  # ±1.5 m/s
    waves = 0.5 * np.sin(2 * np.pi * time_hours * 3)   # Ondas de 3 ciclos/dia
    
    # Combinar componentes (garantir que não seja negativo)
    wind_speeds = np.maximum(base_wind + turbulence + waves, 0.5)
    
    return wind_speeds


def test_power_curve_creation():
    """Testa a criação da curva de potência."""
    print("1. Testando criação da curva de potência...")
    
    # Criar calculadora e especificações
    calculator = TurbinePerformanceCalculator()
    turbine_specs = create_sample_turbine_specs()
    
    # Gerar curva de potência
    wind_speeds = np.linspace(0, 30, 100)
    
    try:
        power_curve = calculator.generate_power_curve(
            turbine_specs=turbine_specs,
            wind_speeds=wind_speeds
        )
        
        print(f"✅ Curva de potência criada com sucesso!")
        print(f"   Tipo: {type(power_curve)}")
        print(f"   Atributos: {[attr for attr in dir(power_curve) if not attr.startswith('_')]}")
        print(f"   Velocidades: {len(power_curve.wind_speeds)} pontos")
        print(f"   Potências: {len(power_curve.power_output)} valores")
        print(f"   Potência máxima: {np.max(power_curve.power_output):.1f} kW")
        
        return power_curve
        
    except Exception as e:
        print(f"❌ Erro ao criar curva de potência: {e}")
        return None


def test_visualization_plot():
    """Testa a geração do gráfico com o visualizador."""
    print("\n2. Testando visualização da curva de potência...")
    
    # Criar curva de potência
    power_curve = test_power_curve_creation()
    if not power_curve:
        return False
    
    # Criar dados de vento realistas
    real_wind_speeds = create_sample_wind_data()
    print(f"   Dados de vento: {len(real_wind_speeds)} pontos")
    print(f"   Velocidade média: {np.mean(real_wind_speeds):.2f} m/s")
    print(f"   Faixa: {np.min(real_wind_speeds):.1f} - {np.max(real_wind_speeds):.1f} m/s")
    
    # Criar visualizador
    visualizer = AnalysisVisualizer()
    
    try:
        # Tentar gerar o gráfico (mesma função que falha no results_reports.py)
        fig = visualizer.plot_power_curve_with_real_data(
            power_curve=power_curve,
            real_wind_speeds=real_wind_speeds,
            height=600
        )
        
        print("✅ Gráfico gerado com sucesso!")
        print(f"   Tipo da figura: {type(fig)}")
        print(f"   Número de traces: {len(fig.data)}")
        
        # Salvar como HTML para verificação
        output_file = Path(__file__).parent / "power_curve_test_plot.html"
        fig.write_html(str(output_file))
        print(f"   Gráfico salvo em: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar gráfico: {e}")
        print(f"   Tipo do erro: {type(e)}")
        return False


def test_object_vs_dict_access():
    """Testa diferentes formas de acessar dados da curva de potência."""
    print("\n3. Testando acesso aos dados...")
    
    power_curve = test_power_curve_creation()
    if not power_curve:
        return
    
    print("   Testando acesso por atributo (correto):")
    try:
        wind_speeds = power_curve.wind_speeds
        power_output = power_curve.power_output
        print(f"   ✅ wind_speeds: {len(wind_speeds)} pontos")
        print(f"   ✅ power_output: {len(power_output)} valores")
    except Exception as e:
        print(f"   ❌ Erro no acesso por atributo: {e}")
    
    print("   Testando acesso por subscripting (incorreto):")
    try:
        wind_speeds = power_curve['wind_speeds']  # Isso deve falhar
        print(f"   ⚠️ Subscripting funcionou inesperadamente!")
    except TypeError as e:
        print(f"   ✅ Subscripting falhou como esperado: {e}")
    except Exception as e:
        print(f"   ❓ Erro inesperado: {e}")


def test_data_validation():
    """Valida os dados gerados."""
    print("\n4. Validando dados gerados...")
    
    power_curve = test_power_curve_creation()
    if not power_curve:
        return
    
    # Verificar estrutura dos dados
    wind_speeds = power_curve.wind_speeds
    power_output = power_curve.power_output
    
    print(f"   Velocidades válidas: {np.all(wind_speeds >= 0)}")
    print(f"   Potências válidas: {np.all(power_output >= 0)}")
    print(f"   Tamanhos compatíveis: {len(wind_speeds) == len(power_output)}")
    print(f"   Dados não são NaN: {not np.any(np.isnan(wind_speeds))} e {not np.any(np.isnan(power_output))}")
    
    # Verificar características típicas de uma curva de potência
    cut_in_idx = np.where(power_output > 0)[0]
    if len(cut_in_idx) > 0:
        cut_in_speed = wind_speeds[cut_in_idx[0]]
        max_power = np.max(power_output)
        rated_speed_idx = np.where(power_output >= max_power * 0.95)[0]
        
        print(f"   Cut-in speed estimado: {cut_in_speed:.1f} m/s")
        print(f"   Potência máxima: {max_power:.1f} kW")
        
        if len(rated_speed_idx) > 0:
            rated_speed = wind_speeds[rated_speed_idx[0]]
            print(f"   Velocidade nominal estimada: {rated_speed:.1f} m/s")


def test_wind_components_integration():
    """Testa integração com dados de componentes de vento."""
    print("\n5. Testando integração com componentes de vento...")
    
    try:
        # Criar calculadora de componentes
        wind_calc = WindComponentsSimulator()
        
        # Parâmetros de teste
        params = {
            'duration': 24,
            'points': 1000,
            'base_speed': 8.0,
            'turbulence_intensity': 1.5,
            'wave_amplitude': 0.5
        }
        
        # Gerar componentes
        components = wind_calc.simulate_wind_components(**params)
        
        print(f"   Componentes gerados: {type(components)}")
        print(f"   Air flow: {len(components.air_flow)} pontos")
        print(f"   Velocidade média: {np.mean(components.air_flow):.2f} m/s")
        
        # Usar com curva de potência
        power_curve = test_power_curve_creation()
        if power_curve:
            visualizer = AnalysisVisualizer()
            
            fig = visualizer.plot_power_curve_with_real_data(
                power_curve=power_curve,
                real_wind_speeds=components.air_flow,
                height=600
            )
            
            print("   ✅ Integração com componentes bem-sucedida!")
            
            # Salvar gráfico integrado
            output_file = Path(__file__).parent / "integrated_power_curve_plot.html"
            fig.write_html(str(output_file))
            print(f"   Gráfico integrado salvo em: {output_file}")
            
    except Exception as e:
        print(f"   ❌ Erro na integração: {e}")


def main():
    """Função principal do teste."""
    print("🔧 Teste de Gráfico da Curva de Potência")
    print("=" * 50)
    print("Este teste valida a correção do erro de subscripting")
    print("no gráfico da curva de potência em results_reports.py")
    print("=" * 50)
    
    # Executar todos os testes
    success = True
    
    try:
        test_power_curve_creation()
        success &= test_visualization_plot()
        test_object_vs_dict_access()
        test_data_validation()
        test_wind_components_integration()
        
    except Exception as e:
        print(f"\n❌ Erro geral no teste: {e}")
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("A correção do erro de subscripting foi bem-sucedida.")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("Verificar logs acima para detalhes.")
    print("=" * 50)


if __name__ == "__main__":
    main()
