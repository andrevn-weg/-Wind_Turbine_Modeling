"""
Módulo para cálculos de perfil de vento e velocidades corrigidas
"""

import math


def calcular_velocidade_corrigida(velocidade_ref, altura_ref, altura_destino, rugosidade, metodo="power_law"):
    """
    Calcula velocidade do vento corrigida usando perfis de vento.
    
    Args:
        velocidade_ref: Velocidade de referência (m/s)
        altura_ref: Altura de referência (m)
        altura_destino: Altura de destino (m)
        rugosidade: Rugosidade do terreno (valor alpha ou z0)
        metodo: "power_law" ou "logarithmic"
    
    Returns:
        Velocidade corrigida na altura de destino (m/s)
    """
    if velocidade_ref is None or altura_ref is None or altura_destino is None:
        return None
    
    if altura_ref <= 0 or altura_destino <= 0:
        return None
    
    if metodo == "power_law":
        return calcular_perfil_potencia(velocidade_ref, altura_ref, altura_destino, rugosidade)
    elif metodo == "logarithmic":
        return calcular_perfil_logaritmico(velocidade_ref, altura_ref, altura_destino, rugosidade)
    else:
        return velocidade_ref  # Sem correção


def calcular_perfil_potencia(velocidade_ref, altura_ref, altura_destino, alpha):
    """
    Lei da Potência: v(h) = v_ref × (h/h_ref)^α
    
    α (alpha) - coeficiente de rugosidade:
    - 0.10: Superfícies de água, campos abertos
    - 0.15: Terreno agrícola com poucas obstruções
    - 0.20: Áreas rurais com obstruções esparsas
    - 0.25: Subúrbios e áreas florestais
    - 0.30+: Áreas urbanas e terrenos muito rugosos
    """
    try:
        velocidade_corrigida = velocidade_ref * ((altura_destino / altura_ref) ** alpha)
        return velocidade_corrigida
    except (ValueError, ZeroDivisionError):
        return None


def calcular_perfil_logaritmico(velocidade_ref, altura_ref, altura_destino, z0):
    """
    Perfil Logarítmico: v(h) = v_ref × ln(h/z0) / ln(h_ref/z0)
    
    z0 - comprimento de rugosidade:
    - 0.0002: Superfícies de água calma
    - 0.001: Terreno muito liso (gelo, areia)
    - 0.01: Campos abertos
    - 0.1: Áreas agrícolas
    - 1.0: Florestas
    - 2.0+: Áreas urbanas
    """
    try:
        if altura_destino <= z0 or altura_ref <= z0:
            return None
        
        velocidade_corrigida = velocidade_ref * (math.log(altura_destino / z0) / math.log(altura_ref / z0))
        return velocidade_corrigida
    except (ValueError, ZeroDivisionError):
        return None


def obter_rugosidade_padrao(tipo_terreno):
    """
    Retorna valores padrão de rugosidade para diferentes tipos de terreno.
    
    Returns:
        tuple: (alpha_power_law, z0_logarithmic)
    """
    rugosidades = {
        'agua_aberta': (0.10, 0.0002),
        'campo_aberto': (0.15, 0.01),
        'rural_disperso': (0.20, 0.1),
        'suburban': (0.25, 0.5),
        'urbano': (0.30, 1.0),
        'muito_rugoso': (0.35, 2.0)
    }
    
    return rugosidades.get(tipo_terreno, (0.20, 0.1))  # Padrão rural


def validar_parametros_perfil(velocidade_ref, altura_ref, altura_destino, rugosidade):
    """
    Valida parâmetros para cálculo de perfil de vento.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if velocidade_ref is None or velocidade_ref <= 0:
        return False, "Velocidade de referência deve ser maior que zero"
    
    if altura_ref is None or altura_ref <= 0:
        return False, "Altura de referência deve ser maior que zero"
    
    if altura_destino is None or altura_destino <= 0:
        return False, "Altura de destino deve ser maior que zero"
    
    if rugosidade is None or rugosidade <= 0:
        return False, "Parâmetro de rugosidade deve ser maior que zero"
    
    # Verificação de alturas muito baixas para perfil logarítmico
    if rugosidade > 0.5 and (altura_ref <= rugosidade or altura_destino <= rugosidade):
        return False, "Alturas devem ser maiores que o comprimento de rugosidade"
    
    return True, ""


def comparar_metodos_perfil(velocidade_ref, altura_ref, altura_destino, alpha, z0):
    """
    Compara resultados dos dois métodos de perfil de vento.
    
    Returns:
        dict: Resultados e comparação dos métodos
    """
    resultado = {
        'power_law': None,
        'logarithmic': None,
        'diferenca': None,
        'diferenca_percentual': None
    }
    
    # Calcular ambos os métodos
    v_power = calcular_perfil_potencia(velocidade_ref, altura_ref, altura_destino, alpha)
    v_log = calcular_perfil_logaritmico(velocidade_ref, altura_ref, altura_destino, z0)
    
    resultado['power_law'] = v_power
    resultado['logarithmic'] = v_log
    
    # Calcular diferenças se ambos os métodos funcionaram
    if v_power is not None and v_log is not None:
        diferenca = v_power - v_log
        diferenca_percentual = (diferenca / v_log) * 100 if v_log != 0 else None
        
        resultado['diferenca'] = diferenca
        resultado['diferenca_percentual'] = diferenca_percentual
    
    return resultado