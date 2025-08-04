"""
Módulo de Análise de Performance de Turbinas

Este módulo implementa os cálculos de performance de turbinas eólicas:
- Coeficiente de Performance (Cp)
- Cálculos de potência
- Curvas características de turbina
- Análise de viabilidade energética

Baseado nos códigos legados em MATLAB, adaptado para Python.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import math


@dataclass
class TurbinePerformance:
    """
    Classe de dados para representar a performance de uma turbina.
    """
    wind_speeds: np.ndarray  # Velocidades do vento (m/s)
    power_output: np.ndarray  # Potência de saída (kW)
    cp_values: np.ndarray  # Coeficientes de performance
    lambda_values: np.ndarray  # Tip Speed Ratio (λ)
    lambda_i_values: np.ndarray  # λ inverso
    turbine_specs: Dict  # Especificações da turbina
    operating_regions: Dict  # Regiões operacionais


class TurbinePerformanceCalculator:
    """
    Calculadora de performance de turbinas eólicas.
    
    Implementa os modelos matemáticos para cálculo de Cp, potência extraível
    e análise de performance de turbinas eólicas.
    """
    
    # Parâmetros padrão para diferentes modelos de Cp
    CP_MODELS = {
        'heier': {
            'c1': 0.5, 'c2': 116, 'c3': 0.4, 'c4': 0, 'c5': 0,
            'c6': 5, 'c7': 21, 'c8': 0.08, 'c9': 0.035
        },
        'default': {
            'c1': 0.5176, 'c2': 116, 'c3': 0.4, 'c4': 5, 'c5': 21,
            'c6': 0.0068, 'c7': 0.08, 'c8': 0.035, 'c9': 0
        }
    }
    
    def __init__(self):
        """Inicializa o calculador de performance de turbinas."""
        pass
    
    def calculate_lambda(self, omega: float, rotor_radius: float, wind_speed: float) -> float:
        """
        Calcula o Tip Speed Ratio (λ).
        
        λ = (ω * R) / V
        
        Args:
            omega: Velocidade angular do rotor (rad/s)
            rotor_radius: Raio do rotor (m)
            wind_speed: Velocidade do vento (m/s)
        
        Returns:
            float: Tip Speed Ratio
        """
        if wind_speed <= 0:
            return 0
        return (omega * rotor_radius) / wind_speed
    
    def calculate_lambda_i(self, lambda_val: float, beta: float, c8: float = 0.08, c9: float = 0.035) -> float:
        """
        Calcula λ inverso para o modelo de Cp.
        
        1/λᵢ = 1/(λ + c8*β) - c9/(β³ + 1)
        
        Args:
            lambda_val: Tip Speed Ratio (λ)
            beta: Ângulo de pitch das pás (graus)
            c8, c9: Coeficientes do modelo
        
        Returns:
            float: λ inverso
        """
        if lambda_val + c8 * beta == 0:
            return 0
        
        term1 = 1 / (lambda_val + c8 * beta)
        term2 = c9 / (beta**3 + 1)
        lambda_i_inv = term1 - term2
        
        return 1 / lambda_i_inv if lambda_i_inv != 0 else 0
    
    def calculate_cp(self, lambda_val: float, beta: float, model: str = 'heier') -> Tuple[float, float]:
        """
        Calcula o Coeficiente de Performance (Cp).
        
        Cp = c1 * ((c2/λᵢ) - (c3*β) - (c4*β*c5) - c6) * exp(-c7/λᵢ)
        
        Args:
            lambda_val: Tip Speed Ratio (λ)
            beta: Ângulo de pitch das pás (graus)
            model: Modelo de coeficientes ('heier', 'default')
        
        Returns:
            Tuple[float, float]: (Cp, λᵢ)
        """
        if model not in self.CP_MODELS:
            raise ValueError(f"Modelo '{model}' não encontrado")
        
        coeffs = self.CP_MODELS[model]
        
        # Calcular λᵢ
        lambda_i = self.calculate_lambda_i(lambda_val, beta, coeffs['c8'], coeffs['c9'])
        
        if lambda_i == 0:
            return 0, 0
        
        # Calcular Cp
        term1 = coeffs['c2'] / lambda_i
        term2 = coeffs['c3'] * beta
        term3 = coeffs['c4'] * beta * coeffs['c5']
        term4 = coeffs['c6']
        
        cp = coeffs['c1'] * (term1 - term2 - term3 - term4) * math.exp(-coeffs['c7'] / lambda_i)
        
        # Garantir que Cp seja não-negativo e não exceda limite físico
        cp = max(0, min(cp, 0.593))  # Limite de Betz
        
        return cp, lambda_i
    
    def calculate_power_available(self, wind_speed: float, rotor_diameter: float, 
                                air_density: float = 1.225) -> float:
        """
        Calcula a potência disponível no vento.
        
        P = 0.5 * ρ * A * V³
        
        Args:
            wind_speed: Velocidade do vento (m/s)
            rotor_diameter: Diâmetro do rotor (m)
            air_density: Densidade do ar (kg/m³)
        
        Returns:
            float: Potência disponível (W)
        """
        rotor_area = math.pi * (rotor_diameter / 2) ** 2
        return 0.5 * air_density * rotor_area * (wind_speed ** 3)
    
    def calculate_power_extracted(self, wind_speed: float, rotor_diameter: float, cp: float,
                                air_density: float = 1.225) -> float:
        """
        Calcula a potência extraída pela turbina.
        
        P_extracted = Cp * P_available
        
        Args:
            wind_speed: Velocidade do vento (m/s)
            rotor_diameter: Diâmetro do rotor (m)
            cp: Coeficiente de performance
            air_density: Densidade do ar (kg/m³)
        
        Returns:
            float: Potência extraída (W)
        """
        power_available = self.calculate_power_available(wind_speed, rotor_diameter, air_density)
        return cp * power_available
    
    def generate_power_curve(self, turbine_specs: Dict, wind_speeds: np.ndarray = None,
                           beta: float = 0, omega: float = None) -> TurbinePerformance:
        """
        Gera a curva de potência de uma turbina.
        
        Args:
            turbine_specs: Especificações da turbina
                          (rated_power_kw, rotor_diameter_m, cut_in_speed, cut_out_speed, etc.)
            wind_speeds: Array de velocidades do vento (m/s)
            beta: Ângulo de pitch (graus)
            omega: Velocidade angular (rad/s) - se None, será calculada
        
        Returns:
            TurbinePerformance: Objeto com dados de performance
        """
        if wind_speeds is None:
            wind_speeds = np.linspace(0, 25, 251)  # 0 a 25 m/s com 0.1 m/s de passo
        
        # Especificações da turbina
        rated_power = turbine_specs.get('rated_power_kw', 2000) * 1000  # Converter para W
        rotor_diameter = turbine_specs.get('rotor_diameter_m', 90)
        cut_in_speed = turbine_specs.get('cut_in_speed', 3.5)
        cut_out_speed = turbine_specs.get('cut_out_speed', 25)
        rated_wind_speed = turbine_specs.get('rated_wind_speed', 12)
        rated_rotor_speed_rpm = turbine_specs.get('rated_rotor_speed_rpm', 15)
        
        # Calcular velocidade angular se não fornecida
        if omega is None:
            omega = (rated_rotor_speed_rpm * 2 * math.pi) / 60  # Converter RPM para rad/s
        
        rotor_radius = rotor_diameter / 2
        
        # Arrays para armazenar resultados
        power_output = np.zeros_like(wind_speeds)
        cp_values = np.zeros_like(wind_speeds)
        lambda_values = np.zeros_like(wind_speeds)
        lambda_i_values = np.zeros_like(wind_speeds)
        
        for i, wind_speed in enumerate(wind_speeds):
            if wind_speed < cut_in_speed or wind_speed > cut_out_speed:
                # Turbina parada
                power_output[i] = 0
                cp_values[i] = 0
                lambda_values[i] = 0
                lambda_i_values[i] = 0
            else:
                # Calcular λ
                lambda_val = self.calculate_lambda(omega, rotor_radius, wind_speed)
                lambda_values[i] = lambda_val
                
                # Calcular Cp
                cp, lambda_i = self.calculate_cp(lambda_val, beta)
                cp_values[i] = cp
                lambda_i_values[i] = lambda_i
                
                # Calcular potência extraída
                power_extracted = self.calculate_power_extracted(wind_speed, rotor_diameter, cp)
                
                # Limitar pela potência nominal
                if wind_speed >= rated_wind_speed:
                    power_output[i] = min(power_extracted, rated_power)
                else:
                    power_output[i] = power_extracted
        
        # Converter potência para kW
        power_output = power_output / 1000
        
        # Definir regiões operacionais
        operating_regions = {
            'stopped': (0, cut_in_speed),
            'mppt': (cut_in_speed, rated_wind_speed),
            'rated': (rated_wind_speed, cut_out_speed),
            'shutdown': (cut_out_speed, wind_speeds[-1])
        }
        
        return TurbinePerformance(
            wind_speeds=wind_speeds,
            power_output=power_output,
            cp_values=cp_values,
            lambda_values=lambda_values,
            lambda_i_values=lambda_i_values,
            turbine_specs=turbine_specs,
            operating_regions=operating_regions
        )
    
    def analyze_performance(self, performance: TurbinePerformance) -> Dict:
        """
        Analisa a performance da turbina.
        
        Args:
            performance: Dados de performance da turbina
        
        Returns:
            Dict: Análise estatística da performance
        """
        # Filtrar dados operacionais (potência > 0)
        operational_mask = performance.power_output > 0
        
        if not np.any(operational_mask):
            return {'error': 'Nenhum dado operacional encontrado'}
        
        operational_speeds = performance.wind_speeds[operational_mask]
        operational_power = performance.power_output[operational_mask]
        operational_cp = performance.cp_values[operational_mask]
        
        analysis = {
            'operational_range': {
                'min_wind_speed': float(np.min(operational_speeds)),
                'max_wind_speed': float(np.max(operational_speeds)),
                'range': float(np.max(operational_speeds) - np.min(operational_speeds))
            },
            'power_statistics': {
                'max_power': float(np.max(operational_power)),
                'average_power': float(np.mean(operational_power)),
                'power_at_rated_speed': float(operational_power[np.argmax(operational_power)])
            },
            'cp_statistics': {
                'max_cp': float(np.max(operational_cp)),
                'average_cp': float(np.mean(operational_cp)),
                'optimal_cp_wind_speed': float(operational_speeds[np.argmax(operational_cp)])
            },
            'efficiency_metrics': {
                'capacity_factor_estimate': self._estimate_capacity_factor(performance),
                'energy_production_estimate': self._estimate_annual_energy(performance)
            }
        }
        
        return analysis
    
    def _estimate_capacity_factor(self, performance: TurbinePerformance, 
                                weibull_k: float = 2.0, weibull_c: float = 8.0) -> float:
        """
        Estima o fator de capacidade usando distribuição de Weibull.
        
        Args:
            performance: Dados de performance
            weibull_k: Parâmetro de forma da distribuição Weibull
            weibull_c: Parâmetro de escala da distribuição Weibull
        
        Returns:
            float: Fator de capacidade estimado (0-1)
        """
        from scipy.stats import weibull_min
        
        rated_power = performance.turbine_specs.get('rated_power_kw', 2000)
        
        # Calcular densidade de probabilidade para cada velocidade de vento
        wind_speeds = performance.wind_speeds
        power_output = performance.power_output
        
        # Distribuição de Weibull
        prob_density = weibull_min.pdf(wind_speeds, weibull_k, scale=weibull_c)
        
        # Energia esperada
        expected_energy = np.trapz(power_output * prob_density, wind_speeds)
        
        # Fator de capacidade
        capacity_factor = expected_energy / rated_power
        
        return min(1.0, max(0.0, capacity_factor))
    
    def _estimate_annual_energy(self, performance: TurbinePerformance,
                              weibull_k: float = 2.0, weibull_c: float = 8.0) -> float:
        """
        Estima a produção anual de energia.
        
        Args:
            performance: Dados de performance
            weibull_k: Parâmetro de forma da distribuição Weibull
            weibull_c: Parâmetro de escala da distribuição Weibull
        
        Returns:
            float: Energia anual estimada (MWh)
        """
        capacity_factor = self._estimate_capacity_factor(performance, weibull_k, weibull_c)
        rated_power = performance.turbine_specs.get('rated_power_kw', 2000)
        
        # Energia anual = Potência nominal × Fator de capacidade × 8760 horas
        annual_energy_kwh = rated_power * capacity_factor * 8760
        
        return annual_energy_kwh / 1000  # Converter para MWh
    
    def generate_performance_dataframe(self, performance: TurbinePerformance) -> pd.DataFrame:
        """
        Gera DataFrame com dados de performance.
        
        Args:
            performance: Dados de performance
        
        Returns:
            pd.DataFrame: DataFrame com todos os dados
        """
        # Determinar região operacional para cada ponto
        regions = []
        for wind_speed in performance.wind_speeds:
            if wind_speed < performance.operating_regions['stopped'][1]:
                regions.append('Parado')
            elif wind_speed < performance.operating_regions['mppt'][1]:
                regions.append('MPPT')
            elif wind_speed < performance.operating_regions['rated'][1]:
                regions.append('Potência Nominal')
            else:
                regions.append('Desligado')
        
        df = pd.DataFrame({
            'Velocidade Vento (m/s)': performance.wind_speeds,
            'Potência (kW)': np.round(performance.power_output, 2),
            'Cp': np.round(performance.cp_values, 4),
            'Lambda (λ)': np.round(performance.lambda_values, 2),
            'Lambda_i (λᵢ)': np.round(performance.lambda_i_values, 4),
            'Região Operacional': regions
        })
        
        return df
    
    @classmethod
    def get_cp_models_info(cls) -> pd.DataFrame:
        """
        Retorna informações sobre os modelos de Cp disponíveis.
        
        Returns:
            pd.DataFrame: Informações sobre os modelos
        """
        models_info = []
        for model_name, coeffs in cls.CP_MODELS.items():
            models_info.append({
                'Modelo': model_name.title(),
                'Descrição': 'Modelo de Heier' if model_name == 'heier' else 'Modelo Padrão',
                'c1': coeffs['c1'],
                'c2': coeffs['c2'],
                'c3': coeffs['c3'],
                'c6': coeffs['c6'],
                'c7': coeffs['c7']
            })
        
        return pd.DataFrame(models_info)

    def simulate_temporal_performance(self, turbine_specs: Dict, wind_data: np.ndarray, 
                                    time_vector: np.ndarray, beta: float = 0.0, 
                                    model: str = 'heier') -> Dict:
        """
        Simula a performance temporal da turbina com dados de vento variáveis.
        
        Args:
            turbine_specs: Especificações da turbina
            wind_data: Dados de velocidade do vento ao longo do tempo
            time_vector: Vetor de tempo correspondente
            beta: Ângulo de pitch (graus)
            model: Modelo de Cp a ser usado
        
        Returns:
            Dict: Dados de performance temporal
        """
        # Parâmetros da turbina
        rotor_diameter = turbine_specs.get('rotor_diameter', 80.0)
        rated_power = turbine_specs.get('rated_power', 2000.0)  # kW
        cut_in_speed = turbine_specs.get('cut_in_speed', 3.0)
        cut_out_speed = turbine_specs.get('cut_out_speed', 25.0)
        rated_speed = turbine_specs.get('rated_speed', 12.0)
        
        # Arrays para resultados
        power_output = np.zeros_like(wind_data)
        cp_values = np.zeros_like(wind_data)
        lambda_values = np.zeros_like(wind_data)
        operational_status = np.full_like(wind_data, 'Stopped', dtype=object)
        
        for i, wind_speed in enumerate(wind_data):
            if wind_speed < cut_in_speed or wind_speed > cut_out_speed:
                # Turbina parada
                power_output[i] = 0.0
                cp_values[i] = 0.0
                lambda_values[i] = 0.0
                operational_status[i] = 'Stopped'
            
            elif wind_speed <= rated_speed:
                # Região MPPT (Maximum Power Point Tracking)
                # Calcular lambda ótimo (assumindo omega variável)
                lambda_opt = 7.0  # Valor típico para lambda ótimo
                omega = lambda_opt * wind_speed / (rotor_diameter / 2)
                
                lambda_values[i] = self.calculate_lambda(omega, rotor_diameter/2, wind_speed)
                cp, _ = self.calculate_cp(lambda_values[i], beta, model)
                cp_values[i] = cp
                
                # Calcular potência extraída
                power_output[i] = self.calculate_power_extracted(
                    wind_speed, rotor_diameter, cp
                )
                operational_status[i] = 'MPPT'
            
            else:
                # Região de potência nominal
                power_output[i] = rated_power
                cp_values[i] = rated_power / self.calculate_power_available(wind_speed, rotor_diameter)
                lambda_values[i] = 7.0  # Valor aproximado
                operational_status[i] = 'Rated'
        
        # Calcular métricas de performance
        total_energy = np.trapz(power_output, time_vector)  # kWh
        capacity_factor = np.mean(power_output) / rated_power * 100
        avg_wind_speed = np.mean(wind_data)
        avg_cp = np.mean(cp_values[cp_values > 0])
        
        return {
            'time': time_vector,
            'wind_speeds': wind_data,
            'power_output': power_output,
            'cp_values': cp_values,
            'lambda_values': lambda_values,
            'operational_status': operational_status,
            'metrics': {
                'total_energy': total_energy,
                'capacity_factor': capacity_factor,
                'avg_wind_speed': avg_wind_speed,
                'avg_cp': avg_cp,
                'max_power': np.max(power_output),
                'operating_hours': np.sum(power_output > 0) / len(power_output) * 100
            }
        }

    def calculate_operational_statistics(self, performance_data: Dict = None, 
                                       power_curve: TurbinePerformance = None,
                                       wind_speeds: np.ndarray = None) -> Dict:
        """
        Calcula estatísticas operacionais da turbina.
        
        Args:
            performance_data: Dados de performance temporal (opcional)
            power_curve: Curva de potência da turbina (opcional)
            wind_speeds: Velocidades de vento para análise (opcional)
        
        Returns:
            Dict: Estatísticas operacionais
        """
        stats = {
            'power_stats': {},
            'operational_stats': {},
            'efficiency_stats': {}
        }
        
        # Estatísticas da curva de potência
        if power_curve:
            stats['power_stats'] = {
                'rated_power': np.max(power_curve.power_output),
                'cut_in_speed': power_curve.wind_speeds[power_curve.power_output > 0][0] if np.any(power_curve.power_output > 0) else 0,
                'rated_speed': power_curve.wind_speeds[np.argmax(power_curve.power_output)],
                'max_cp': np.max(power_curve.cp_values),
                'optimal_lambda': power_curve.lambda_values[np.argmax(power_curve.cp_values)]
            }
        
        # Estatísticas temporais
        if performance_data:
            total_hours = len(performance_data['time'])
            operating_hours = np.sum(performance_data['power_output'] > 0)
            
            stats['operational_stats'] = {
                'total_hours': total_hours,
                'operating_hours': operating_hours,
                'availability': (operating_hours / total_hours) * 100,
                'avg_power': np.mean(performance_data['power_output']),
                'peak_power': np.max(performance_data['power_output']),
                'energy_production': np.trapz(performance_data['power_output'], performance_data['time'])
            }
            
            stats['efficiency_stats'] = {
                'avg_cp': np.mean(performance_data['cp_values'][performance_data['cp_values'] > 0]),
                'max_cp': np.max(performance_data['cp_values']),
                'avg_lambda': np.mean(performance_data['lambda_values'][performance_data['lambda_values'] > 0]),
                'capacity_factor': performance_data['metrics']['capacity_factor']
            }
        
        # Estatísticas de vento
        if wind_speeds is not None:
            stats['wind_stats'] = {
                'avg_wind_speed': np.mean(wind_speeds),
                'max_wind_speed': np.max(wind_speeds),
                'min_wind_speed': np.min(wind_speeds),
                'wind_std': np.std(wind_speeds)
            }
        
        return stats
