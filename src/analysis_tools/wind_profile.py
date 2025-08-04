"""
Módulo de Análise de Perfil Vertical do Vento

Este módulo implementa os modelos de perfil vertical de vento:
- Lei de Potência
- Lei Logarítmica
- Análise comparativa entre modelos
- Correção de velocidade por altura

Baseado nos códigos legados em MATLAB, adaptado para Python.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math


@dataclass
class WindProfile:
    """
    Classe de dados para representar um perfil de vento.
    """
    reference_speed: float  # Velocidade de referência (m/s)
    reference_height: float  # Altura de referência (m)
    heights: np.ndarray  # Alturas para cálculo (m)
    power_law_speeds: np.ndarray  # Velocidades pela Lei de Potência
    logarithmic_speeds: np.ndarray  # Velocidades pela Lei Logarítmica
    power_law_coefficient: float  # Coeficiente n da Lei de Potência
    roughness_length: float  # Comprimento de rugosidade z0 (m)
    intersection_height: Optional[float] = None  # Altura de intersecção
    intersection_speed: Optional[float] = None  # Velocidade na intersecção


class WindProfileCalculator:
    """
    Calculadora de perfis verticais de vento.
    
    Implementa os modelos matemáticos para extrapolação vertical de velocidade do vento.
    """
    
    # Parâmetros unificados por tipo de terreno
    TERRAIN_PARAMETERS = {
        'smooth_lake': {
            'name': 'Superfície Lisa (Lago/Oceano)',
            'n': 0.10,
            'z0': 0.0002,
            'description': 'Mar aberto, lagos grandes'
        },
        'short_grass': {
            'name': 'Grama Baixa',
            'n': 0.14,
            'z0': 0.008,
            'description': 'Gramado, campos abertos'
        },
        'low_vegetation': {
            'name': 'Vegetação Rasteira',
            'n': 0.16,
            'z0': 0.03,
            'description': 'Vegetação até 0,3m'
        },
        'shrubs': {
            'name': 'Arbustos e Árvores Ocasionais',
            'n': 0.20,
            'z0': 0.1,
            'description': 'Poucas árvores esparsas'
        },
        'trees_buildings': {
            'name': 'Árvores e Construções',
            'n': 0.22,
            'z0': 0.25,
            'description': 'Muitas árvores, poucos edifícios'
        },
        'residential': {
            'name': 'Área Residencial',
            'n': 0.28,
            'z0': 1.5,
            'description': 'Subúrbios, áreas urbanas'
        },
        'urban': {
            'name': 'Área Urbana Densa',
            'n': 0.35,
            'z0': 3.0,
            'description': 'Edifícios altos, centro urbano'
        }
    }
    
    # Manter compatibilidade com código existente
    @property
    def POWER_LAW_COEFFICIENTS(self):
        return {k: v['n'] for k, v in self.TERRAIN_PARAMETERS.items()}
    
    @property  
    def ROUGHNESS_VALUES(self):
        return {k: v['z0'] for k, v in self.TERRAIN_PARAMETERS.items()}
    
    def __init__(self):
        """Inicializa o calculador de perfis de vento."""
        pass
    
    def power_law(self, v_ref: float, h_ref: float, h_target: float, n: float = 0.22) -> float:
        """
        Calcula a velocidade do vento usando a Lei de Potência.
        
        V2 = V1 * (H2/H1)^n
        
        Args:
            v_ref: Velocidade de referência (m/s)
            h_ref: Altura de referência (m)
            h_target: Altura alvo (m)
            n: Coeficiente de potência (padrão 0.22)
        
        Returns:
            float: Velocidade do vento na altura alvo (m/s)
        """
        if h_ref <= 0 or h_target <= 0:
            raise ValueError("Alturas devem ser positivas")
        
        return v_ref * ((h_target / h_ref) ** n)
    
    def logarithmic_law(self, v_ref: float, h_ref: float, h_target: float, z0: float = 0.15) -> float:
        """
        Calcula a velocidade do vento usando a Lei Logarítmica.
        
        V2 = V1 * ln(H2/z0) / ln(H1/z0)
        
        Args:
            v_ref: Velocidade de referência (m/s)
            h_ref: Altura de referência (m)
            h_target: Altura alvo (m)
            z0: Comprimento de rugosidade (m, padrão 0.15)
        
        Returns:
            float: Velocidade do vento na altura alvo (m/s)
        """
        if h_ref <= z0 or h_target <= z0:
            raise ValueError("Alturas devem ser maiores que o comprimento de rugosidade")
        
        return v_ref * (math.log(h_target / z0) / math.log(h_ref / z0))
    
    def calculate_profile(self, v_ref: float, h_ref: float, h_max: float = 100.0, 
                         n: float = 0.22, z0: float = 0.15, step: float = 0.1) -> WindProfile:
        """
        Calcula o perfil completo de vento usando ambos os modelos.
        
        Args:
            v_ref: Velocidade de referência (m/s)
            h_ref: Altura de referência (m)
            h_max: Altura máxima para cálculo (m)
            n: Coeficiente da Lei de Potência
            z0: Comprimento de rugosidade (m)
            step: Passo de altura (m)
        
        Returns:
            WindProfile: Objeto com todos os dados do perfil
        """
        # Criar array de alturas
        heights = np.arange(max(z0 + 0.1, 1.0), h_max + step, step)
        
        # Calcular velocidades usando ambos os métodos
        power_law_speeds = np.array([
            self.power_law(v_ref, h_ref, h, n) for h in heights
        ])
        
        logarithmic_speeds = np.array([
            self.logarithmic_law(v_ref, h_ref, h, z0) for h in heights
        ])
        
        # Encontrar ponto de intersecção
        diff_curves = np.abs(power_law_speeds - logarithmic_speeds)
        idx_intersect = np.argmin(diff_curves)
        intersection_height = heights[idx_intersect]
        intersection_speed = power_law_speeds[idx_intersect]
        
        return WindProfile(
            reference_speed=v_ref,
            reference_height=h_ref,
            heights=heights,
            power_law_speeds=power_law_speeds,
            logarithmic_speeds=logarithmic_speeds,
            power_law_coefficient=n,
            roughness_length=z0,
            intersection_height=intersection_height,
            intersection_speed=intersection_speed
        )
    
    def get_highlighted_points(self, profile: WindProfile, interval: float = 10.0) -> Dict:
        """
        Extrai pontos destacados do perfil em intervalos regulares.
        
        Args:
            profile: Perfil de vento calculado
            interval: Intervalo entre pontos (m)
        
        Returns:
            Dict: Dicionário com alturas e velocidades destacadas
        """
        highlight_heights = np.arange(interval, profile.heights[-1], interval)
        
        # Interpolar valores nas alturas destacadas
        power_law_highlighted = np.interp(highlight_heights, profile.heights, profile.power_law_speeds)
        logarithmic_highlighted = np.interp(highlight_heights, profile.heights, profile.logarithmic_speeds)
        
        return {
            'heights': highlight_heights,
            'power_law_speeds': power_law_highlighted,
            'logarithmic_speeds': logarithmic_highlighted,
            'differences': np.abs(power_law_highlighted - logarithmic_highlighted)
        }
    
    def correct_wind_speed_to_turbine_height(self, measured_speed: float, measured_height: float,
                                           turbine_height: float, terrain_type: str = 'trees_buildings') -> Dict:
        """
        Corrige a velocidade do vento para a altura do hub da turbina.
        
        Args:
            measured_speed: Velocidade medida (m/s)
            measured_height: Altura de medição (m)
            turbine_height: Altura do hub da turbina (m)
            terrain_type: Tipo de terreno (chave do dicionário TERRAIN_PARAMETERS)
        
        Returns:
            Dict: Velocidades corrigidas pelos dois métodos
        """
        terrain_params = self.TERRAIN_PARAMETERS.get(terrain_type, self.TERRAIN_PARAMETERS['trees_buildings'])
        n = terrain_params['n']
        z0 = terrain_params['z0']
        
        power_law_corrected = self.power_law(measured_speed, measured_height, turbine_height, n)
        logarithmic_corrected = self.logarithmic_law(measured_speed, measured_height, turbine_height, z0)
        
        return {
            'power_law_speed': power_law_corrected,
            'logarithmic_speed': logarithmic_corrected,
            'difference': abs(power_law_corrected - logarithmic_corrected),
            'coefficient_used': n,
            'roughness_used': z0,
            'terrain_type': terrain_type
        }
    
    def generate_analysis_table(self, profile: WindProfile, interval: float = 10.0) -> pd.DataFrame:
        """
        Gera tabela de análise com valores destacados.
        
        Args:
            profile: Perfil de vento calculado
            interval: Intervalo entre pontos (m)
        
        Returns:
            pd.DataFrame: Tabela com análise completa
        """
        highlighted = self.get_highlighted_points(profile, interval)
        
        df = pd.DataFrame({
            'Altura (m)': highlighted['heights'],
            'Lei Potência (m/s)': np.round(highlighted['power_law_speeds'], 2),
            'Lei Logarítmica (m/s)': np.round(highlighted['logarithmic_speeds'], 2),
            'Diferença (m/s)': np.round(highlighted['differences'], 3),
            'Diferença (%)': np.round((highlighted['differences'] / highlighted['power_law_speeds']) * 100, 1)
        })
        
        return df
    
    @classmethod
    def get_terrain_types_info(cls) -> pd.DataFrame:
        """
        Retorna informações sobre tipos de terreno e seus parâmetros.
        
        Returns:
            pd.DataFrame: Tabela com tipos de terreno e parâmetros
        """
        data = []
        for terrain_key, params in cls.TERRAIN_PARAMETERS.items():
            data.append({
                'Tipo de Terreno': params['name'],
                'Coeficiente n': params['n'],
                'Rugosidade z0 (m)': params['z0'],
                'Chave': terrain_key,
                'Descrição': params['description']
            })
        
        return pd.DataFrame(data)
