"""
Módulo de Simulação de Componentes do Vento

Este módulo implementa a simulação dos componentes do vento:
- Vento médio (Mean Wind)
- Ondas (Waves)
- Turbulência (Turbulence)
- Fluxo de ar resultante

Baseado nos códigos legados em MATLAB, adaptado para Python.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random


@dataclass
class WindComponents:
    """
    Classe de dados para representar os componentes do vento.
    """
    time: np.ndarray  # Vetor de tempo
    mean_wind: np.ndarray  # Componente de vento médio
    waves: np.ndarray  # Componente de ondas
    turbulence: np.ndarray  # Componente de turbulência
    air_flow: np.ndarray  # Fluxo de ar resultante
    base_speed: float  # Velocidade base do vento médio
    wave_amplitude: float  # Amplitude das ondas
    turbulence_intensity: float  # Intensidade da turbulência


class WindComponentsSimulator:
    """
    Simulador de componentes do vento.
    
    Implementa a modelagem matemática dos diferentes componentes que compõem
    o vento real: médio, ondas e turbulência.
    """
    
    def __init__(self):
        """Inicializa o simulador de componentes do vento."""
        pass
    
    def generate_mean_wind(self, time: np.ndarray, base_speed: float = 5.0, 
                          variation_amplitude: float = 0.5, frequency: float = 0.1) -> np.ndarray:
        """
        Gera o componente de vento médio com variação suave.
        
        Args:
            time: Vetor de tempo
            base_speed: Velocidade base (m/s)
            variation_amplitude: Amplitude de variação (m/s)
            frequency: Frequência de variação (Hz)
        
        Returns:
            np.ndarray: Componente de vento médio
        """
        return base_speed + variation_amplitude * np.sin(2 * np.pi * frequency * time)
    
    def generate_waves(self, time: np.ndarray, amplitude: float = 1.0, 
                      frequency: float = 0.2, phase_shift: float = 0.0) -> np.ndarray:
        """
        Gera o componente de ondas do vento.
        
        Args:
            time: Vetor de tempo
            amplitude: Amplitude das ondas
            frequency: Frequência das ondas (Hz)
            phase_shift: Deslocamento de fase
        
        Returns:
            np.ndarray: Componente de ondas
        """
        # Normalizar para usar posição no ciclo completo
        x = np.linspace(0, 2*np.pi, len(time))
        return amplitude * np.sin(x + phase_shift)
    
    def generate_turbulence(self, time: np.ndarray, intensity: float = 1.0, 
                           method: str = 'rayleigh') -> np.ndarray:
        """
        Gera o componente de turbulência do vento.
        
        Args:
            time: Vetor de tempo
            intensity: Intensidade da turbulência
            method: Método de geração ('rayleigh', 'normal', 'uniform')
        
        Returns:
            np.ndarray: Componente de turbulência
        """
        np.random.seed(42)  # Para reprodutibilidade
        
        if method == 'rayleigh':
            # Distribuição de Rayleigh (similar ao código MATLAB original)
            turbulence = intensity * np.sqrt(-2 * np.log(np.random.uniform(0.001, 1, len(time))))
        elif method == 'normal':
            # Distribuição normal
            turbulence = intensity * np.random.normal(0, 1, len(time))
        elif method == 'uniform':
            # Distribuição uniforme
            turbulence = intensity * 2 * (np.random.uniform(0, 1, len(time)) - 0.5)
        else:
            raise ValueError(f"Método '{method}' não reconhecido")
        
        return turbulence
    
    def combine_components(self, mean_wind: np.ndarray, waves: np.ndarray, 
                          turbulence: np.ndarray, combination_method: str = 'weighted') -> np.ndarray:
        """
        Combina os componentes do vento para formar o fluxo de ar resultante.
        
        Args:
            mean_wind: Componente de vento médio
            waves: Componente de ondas
            turbulence: Componente de turbulência
            combination_method: Método de combinação ('weighted', 'additive', 'multiplicative')
        
        Returns:
            np.ndarray: Fluxo de ar resultante
        """
        if combination_method == 'weighted':
            # Método do código original: média ponderada
            air_flow = (mean_wind + (mean_wind * waves) + (mean_wind * turbulence)) / 3
        elif combination_method == 'additive':
            # Soma simples dos componentes
            air_flow = mean_wind + waves + turbulence
        elif combination_method == 'multiplicative':
            # Produto dos componentes normalizados
            air_flow = mean_wind * (1 + 0.1 * waves) * (1 + 0.1 * turbulence)
        else:
            raise ValueError(f"Método de combinação '{combination_method}' não reconhecido")
        
        # Garantir que velocidades sejam não-negativas
        return np.maximum(air_flow, 0)
    
    def simulate_wind_components(self, duration: float = 24.0, points: int = 500,
                               base_speed: float = 5.0, wave_amplitude: float = 1.0,
                               turbulence_intensity: float = 1.0, 
                               combination_method: str = 'weighted') -> WindComponents:
        """
        Simula todos os componentes do vento para um período específico.
        
        Args:
            duration: Duração da simulação (horas)
            points: Número de pontos da simulação
            base_speed: Velocidade base do vento médio (m/s)
            wave_amplitude: Amplitude das ondas
            turbulence_intensity: Intensidade da turbulência
            combination_method: Método de combinação dos componentes
        
        Returns:
            WindComponents: Objeto com todos os componentes simulados
        """
        # Criar vetor de tempo
        time = np.linspace(0, duration, points)
        
        # Gerar cada componente
        mean_wind = self.generate_mean_wind(time, base_speed)
        waves = self.generate_waves(time, wave_amplitude)
        turbulence = self.generate_turbulence(time, turbulence_intensity)
        
        # Combinar componentes
        air_flow = self.combine_components(mean_wind, waves, turbulence, combination_method)
        
        return WindComponents(
            time=time,
            mean_wind=mean_wind,
            waves=waves,
            turbulence=turbulence,
            air_flow=air_flow,
            base_speed=base_speed,
            wave_amplitude=wave_amplitude,
            turbulence_intensity=turbulence_intensity
        )
    
    def analyze_components(self, components: WindComponents) -> Dict:
        """
        Analisa estatisticamente os componentes do vento.
        
        Args:
            components: Componentes do vento simulados
        
        Returns:
            Dict: Análise estatística dos componentes
        """
        analysis = {}
        
        for component_name, component_data in [
            ('mean_wind', components.mean_wind),
            ('waves', components.waves),
            ('turbulence', components.turbulence),
            ('air_flow', components.air_flow)
        ]:
            analysis[component_name] = {
                'mean': np.mean(component_data),
                'std': np.std(component_data),
                'min': np.min(component_data),
                'max': np.max(component_data),
                'range': np.max(component_data) - np.min(component_data),
                'variance': np.var(component_data)
            }
        
        # Análise de correlação
        analysis['correlations'] = {
            'mean_wind_vs_air_flow': np.corrcoef(components.mean_wind, components.air_flow)[0, 1],
            'waves_vs_air_flow': np.corrcoef(components.waves, components.air_flow)[0, 1],
            'turbulence_vs_air_flow': np.corrcoef(components.turbulence, components.air_flow)[0, 1]
        }
        
        # Análise de energia (variabilidade)
        analysis['energy'] = {
            'mean_wind_energy': np.sum(components.mean_wind ** 2),
            'waves_energy': np.sum(components.waves ** 2),
            'turbulence_energy': np.sum(components.turbulence ** 2),
            'air_flow_energy': np.sum(components.air_flow ** 2)
        }
        
        return analysis
    
    def generate_analysis_dataframe(self, components: WindComponents) -> pd.DataFrame:
        """
        Gera DataFrame para análise detalhada dos componentes.
        
        Args:
            components: Componentes do vento simulados
        
        Returns:
            pd.DataFrame: DataFrame com todos os componentes
        """
        df = pd.DataFrame({
            'Tempo (h)': components.time,
            'Vento Médio (m/s)': components.mean_wind,
            'Ondas': components.waves,
            'Turbulência': components.turbulence,
            'Fluxo de Ar (m/s)': components.air_flow
        })
        
        return df
    
    def simulate_real_wind_conditions(self, weather_data: Dict, duration: float = 24.0, 
                                    points: int = 500) -> WindComponents:
        """
        Simula condições de vento realistas baseadas em dados meteorológicos.
        
        Args:
            weather_data: Dicionário com dados meteorológicos
                         (deve conter: 'mean_speed', 'temperature', 'humidity')
            duration: Duração da simulação (horas)
            points: Número de pontos
        
        Returns:
            WindComponents: Componentes simulados com base em condições reais
        """
        base_speed = weather_data.get('mean_speed', 5.0)
        temperature = weather_data.get('temperature', 20.0)
        humidity = weather_data.get('humidity', 60.0)
        
        # Ajustar parâmetros baseados nas condições meteorológicas
        # Turbulência aumenta com temperatura e diminui com umidade
        turbulence_factor = 1.0 + (temperature - 20) * 0.02 - (humidity - 50) * 0.005
        turbulence_intensity = max(0.5, min(2.0, turbulence_factor))
        
        # Amplitude das ondas baseada na velocidade média
        wave_amplitude = min(2.0, base_speed * 0.2)
        
        return self.simulate_wind_components(
            duration=duration,
            points=points,
            base_speed=base_speed,
            wave_amplitude=wave_amplitude,
            turbulence_intensity=turbulence_intensity
        )
    
    @staticmethod
    def get_turbulence_methods_info() -> Dict:
        """
        Retorna informações sobre os métodos de geração de turbulência.
        
        Returns:
            Dict: Informações sobre os métodos
        """
        return {
            'rayleigh': {
                'description': 'Distribuição de Rayleigh - simula rajadas naturais',
                'characteristics': 'Valores sempre positivos, assimétrica',
                'use_case': 'Modelagem realística de turbulência atmosférica'
            },
            'normal': {
                'description': 'Distribuição Normal - turbulência simétrica',
                'characteristics': 'Valores positivos e negativos, simétrica',
                'use_case': 'Análise teórica e comparações'
            },
            'uniform': {
                'description': 'Distribuição Uniforme - turbulência constante',
                'characteristics': 'Valores uniformemente distribuídos',
                'use_case': 'Testes e validação de modelos'
            }
        }
