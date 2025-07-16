"""
Serviços de análise de dados climáticos.

Este módulo contém serviços para análise estatística
e processamento de dados climáticos e eólicos.
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from statistics import mean, median, stdev

from ..models.entity import DadosEolicos, SerieTemporalVento, LocalizacaoClimatica


class AnaliseEolicaService:
    """
    Serviço para análise de dados eólicos.
    
    Fornece métodos para análise estatística, cálculo de potencial
    eólico e processamento de séries temporais de vento.
    """
    
    def __init__(self):
        """Inicializa o serviço de análise eólica."""
        pass
    
    def calcular_estatisticas_completas(self, dados: List[DadosEolicos]) -> Dict[str, Any]:
        """
        Calcula estatísticas completas de uma série de dados eólicos.
        
        Args:
            dados: Lista de dados eólicos
        
        Returns:
            Dicionário com estatísticas detalhadas
        """
        if not dados:
            return {}
        
        velocidades = [d.velocidade_vento for d in dados]
        temperaturas = [d.temperatura for d in dados]
        umidades = [d.umidade for d in dados]
        
        # Estatísticas básicas de vento
        stats_vento = self._calcular_estatisticas_basicas(velocidades)
        
        # Distribuição de velocidades
        distribuicao = self._calcular_distribuicao_velocidades(velocidades)
        
        # Análise temporal
        analise_temporal = self._analisar_padroes_temporais(dados)
        
        # Viabilidade para turbinas
        viabilidade = self._analisar_viabilidade_turbinas(velocidades)
        
        # Correlações
        correlacoes = self._calcular_correlacoes(dados)
        
        return {
            'periodo': {
                'inicio': min(d.data for d in dados).isoformat(),
                'fim': max(d.data for d in dados).isoformat(),
                'total_dias': len(dados)
            },
            'vento': stats_vento,
            'temperatura': self._calcular_estatisticas_basicas(temperaturas),
            'umidade': self._calcular_estatisticas_basicas(umidades),
            'distribuicao_velocidades': distribuicao,
            'analise_temporal': analise_temporal,
            'viabilidade_turbinas': viabilidade,
            'correlacoes': correlacoes
        }
    
    def calcular_potencial_eolico(self, dados: List[DadosEolicos],
                                 diametro_rotor: float = 15.0,
                                 eficiencia: float = 0.35,
                                 altura_cubo: float = 30.0) -> Dict[str, float]:
        """
        Calcula o potencial eólico para uma turbina específica.
        
        Args:
            dados: Lista de dados eólicos
            diametro_rotor: Diâmetro do rotor em metros
            eficiencia: Eficiência da turbina (0-1)
            altura_cubo: Altura do cubo da turbina em metros
        
        Returns:
            Dicionário com potencial eólico calculado
        """
        if not dados:
            return {}
        
        area_varredura = math.pi * (diametro_rotor / 2) ** 2
        
        # Corrige velocidades para altura do cubo
        dados_corrigidos = []
        for dado in dados:
            fator_altura = self._calcular_fator_altura(
                dado.altura_medicao, altura_cubo
            )
            velocidade_corrigida = dado.velocidade_vento * fator_altura
            
            # Cria novo dado com velocidade corrigida
            dado_corrigido = DadosEolicos(
                cidade=dado.cidade,
                latitude=dado.latitude,
                longitude=dado.longitude,
                temperatura=dado.temperatura,
                umidade=dado.umidade,
                velocidade_vento=velocidade_corrigida,
                direcao_vento=dado.direcao_vento,
                velocidade_vento_max=dado.velocidade_vento_max,
                data=dado.data,
                altura_medicao=int(altura_cubo)
            )
            dados_corrigidos.append(dado_corrigido)
        
        # Calcula potência para cada dia
        potencias_diarias = []
        energias_diarias = []
        
        for dado in dados_corrigidos:
            potencia = dado.calcular_potencia_vento(area_varredura, eficiencia)
            energia_kwh = (potencia * 24) / 1000  # Conversão para kWh/dia
            
            potencias_diarias.append(potencia)
            energias_diarias.append(energia_kwh)
        
        # Estatísticas de energia
        energia_total_periodo = sum(energias_diarias)
        dias_periodo = len(dados)
        energia_media_diaria = energia_total_periodo / dias_periodo if dias_periodo > 0 else 0
        energia_anual_estimada = energia_media_diaria * 365
        
        # Fator de capacidade
        potencia_nominal = max(potencias_diarias) if potencias_diarias else 0
        fator_capacidade = (mean(potencias_diarias) / potencia_nominal) if potencia_nominal > 0 else 0
        
        return {
            'area_varredura_m2': area_varredura,
            'altura_cubo_m': altura_cubo,
            'eficiencia': eficiencia,
            'potencia_media_w': mean(potencias_diarias) if potencias_diarias else 0,
            'potencia_maxima_w': max(potencias_diarias) if potencias_diarias else 0,
            'energia_media_diaria_kwh': energia_media_diaria,
            'energia_anual_estimada_kwh': energia_anual_estimada,
            'fator_capacidade': fator_capacidade,
            'dias_analisados': dias_periodo
        }
    
    def analisar_sazonalidade(self, dados: List[DadosEolicos]) -> Dict[str, Any]:
        """
        Analisa padrões sazonais nos dados eólicos.
        
        Args:
            dados: Lista de dados eólicos
        
        Returns:
            Análise de sazonalidade
        """
        if not dados:
            return {}
        
        # Agrupa por mês
        dados_por_mes = {}
        for dado in dados:
            mes = dado.data.month
            if mes not in dados_por_mes:
                dados_por_mes[mes] = []
            dados_por_mes[mes].append(dado.velocidade_vento)
        
        # Calcula estatísticas por mês
        estatisticas_mensais = {}
        for mes, velocidades in dados_por_mes.items():
            estatisticas_mensais[mes] = {
                'media': mean(velocidades),
                'mediana': median(velocidades),
                'maximo': max(velocidades),
                'minimo': min(velocidades),
                'dias': len(velocidades)
            }
        
        # Identifica melhor e pior mês
        if estatisticas_mensais:
            melhor_mes = max(estatisticas_mensais.keys(), 
                           key=lambda m: estatisticas_mensais[m]['media'])
            pior_mes = min(estatisticas_mensais.keys(),
                         key=lambda m: estatisticas_mensais[m]['media'])
        else:
            melhor_mes = pior_mes = None
        
        return {
            'estatisticas_mensais': estatisticas_mensais,
            'melhor_mes': melhor_mes,
            'pior_mes': pior_mes,
            'variacao_sazonal': max(
                [stats['media'] for stats in estatisticas_mensais.values()]
            ) - min(
                [stats['media'] for stats in estatisticas_mensais.values()]
            ) if estatisticas_mensais else 0
        }
    
    def calcular_curva_duracao(self, dados: List[DadosEolicos],
                              intervalos: int = 100) -> List[Dict[str, float]]:
        """
        Calcula a curva de duração de velocidades de vento.
        
        Args:
            dados: Lista de dados eólicos
            intervalos: Número de intervalos na curva
        
        Returns:
            Lista com pontos da curva de duração
        """
        if not dados:
            return []
        
        velocidades = sorted([d.velocidade_vento for d in dados], reverse=True)
        total_pontos = len(velocidades)
        
        curva = []
        for i in range(intervalos + 1):
            percentil = i / intervalos
            indice = int(percentil * (total_pontos - 1))
            
            curva.append({
                'percentil': percentil * 100,
                'velocidade': velocidades[indice],
                'frequencia': (1 - percentil) * 100
            })
        
        return curva
    
    def estimar_producao_anual(self, dados: List[DadosEolicos],
                              curva_potencia: List[Tuple[float, float]]) -> Dict[str, float]:
        """
        Estima produção anual baseada em curva de potência da turbina.
        
        Args:
            dados: Lista de dados eólicos
            curva_potencia: Lista de tuplas (velocidade, potência)
        
        Returns:
            Estimativa de produção anual
        """
        if not dados or not curva_potencia:
            return {}
        
        # Ordena curva de potência por velocidade
        curva_ordenada = sorted(curva_potencia, key=lambda x: x[0])
        
        # Calcula energia para cada dia
        energias_diarias = []
        for dado in dados:
            potencia = self._interpolar_potencia(dado.velocidade_vento, curva_ordenada)
            energia_kwh = (potencia * 24) / 1000
            energias_diarias.append(energia_kwh)
        
        # Projeta para ano completo
        energia_total_periodo = sum(energias_diarias)
        dias_periodo = len(dados)
        energia_anual = (energia_total_periodo * 365) / dias_periodo if dias_periodo > 0 else 0
        
        return {
            'energia_anual_kwh': energia_anual,
            'energia_media_diaria_kwh': energia_total_periodo / dias_periodo if dias_periodo > 0 else 0,
            'dias_base_calculo': dias_periodo,
            'fator_extrapolacao': 365 / dias_periodo if dias_periodo > 0 else 0
        }
    
    def _calcular_estatisticas_basicas(self, valores: List[float]) -> Dict[str, float]:
        """Calcula estatísticas básicas de uma lista de valores."""
        if not valores:
            return {}
        
        valores_validos = [v for v in valores if v is not None]
        if not valores_validos:
            return {}
        
        return {
            'media': mean(valores_validos),
            'mediana': median(valores_validos),
            'minimo': min(valores_validos),
            'maximo': max(valores_validos),
            'desvio_padrao': stdev(valores_validos) if len(valores_validos) > 1 else 0,
            'total_registros': len(valores_validos)
        }
    
    def _calcular_distribuicao_velocidades(self, velocidades: List[float]) -> Dict[str, Any]:
        """Calcula distribuição de velocidades de vento."""
        if not velocidades:
            return {}
        
        # Define faixas de velocidade
        faixas = [
            (0, 2, "Muito baixa"),
            (2, 5, "Baixa"),
            (5, 8, "Moderada"),
            (8, 12, "Alta"),
            (12, 20, "Muito alta"),
            (20, float('inf'), "Extrema")
        ]
        
        distribuicao = {}
        total = len(velocidades)
        
        for min_vel, max_vel, nome in faixas:
            count = sum(1 for v in velocidades if min_vel <= v < max_vel)
            distribuicao[nome] = {
                'count': count,
                'percentual': (count / total) * 100 if total > 0 else 0,
                'faixa': f"{min_vel}-{max_vel if max_vel != float('inf') else '+'} m/s"
            }
        
        return distribuicao
    
    def _analisar_padroes_temporais(self, dados: List[DadosEolicos]) -> Dict[str, Any]:
        """Analisa padrões temporais nos dados."""
        if not dados:
            return {}
        
        # Agrupa por dia da semana
        dados_por_dia_semana = {}
        for dado in dados:
            dia_semana = dado.data.weekday()  # 0 = Segunda, 6 = Domingo
            if dia_semana not in dados_por_dia_semana:
                dados_por_dia_semana[dia_semana] = []
            dados_por_dia_semana[dia_semana].append(dado.velocidade_vento)
        
        # Calcula médias por dia da semana
        medias_semanais = {}
        nomes_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for dia, velocidades in dados_por_dia_semana.items():
            medias_semanais[nomes_dias[dia]] = mean(velocidades)
        
        return {
            'medias_por_dia_semana': medias_semanais,
            'total_semanas_analisadas': len(dados) // 7
        }
    
    def _analisar_viabilidade_turbinas(self, velocidades: List[float]) -> Dict[str, Any]:
        """Analisa viabilidade para diferentes tipos de turbinas."""
        if not velocidades:
            return {}
        
        # Define características de diferentes turbinas
        turbinas = {
            'Pequena (2kW)': {'cut_in': 2.5, 'cut_out': 15.0, 'nominal': 8.0},
            'Média (20kW)': {'cut_in': 3.0, 'cut_out': 20.0, 'nominal': 10.0},
            'Grande (100kW)': {'cut_in': 3.5, 'cut_out': 25.0, 'nominal': 12.0}
        }
        
        viabilidade = {}
        total_dias = len(velocidades)
        
        for nome, specs in turbinas.items():
            dias_operacao = sum(
                1 for v in velocidades 
                if specs['cut_in'] <= v <= specs['cut_out']
            )
            
            dias_potencia_nominal = sum(
                1 for v in velocidades 
                if v >= specs['nominal']
            )
            
            viabilidade[nome] = {
                'dias_operacao': dias_operacao,
                'percentual_operacao': (dias_operacao / total_dias) * 100 if total_dias > 0 else 0,
                'dias_potencia_nominal': dias_potencia_nominal,
                'percentual_potencia_nominal': (dias_potencia_nominal / total_dias) * 100 if total_dias > 0 else 0
            }
        
        return viabilidade
    
    def _calcular_correlacoes(self, dados: List[DadosEolicos]) -> Dict[str, float]:
        """Calcula correlações entre variáveis meteorológicas."""
        if len(dados) < 2:
            return {}
        
        velocidades = [d.velocidade_vento for d in dados]
        temperaturas = [d.temperatura for d in dados]
        umidades = [d.umidade for d in dados]
        
        try:
            return {
                'vento_temperatura': self._correlacao_pearson(velocidades, temperaturas),
                'vento_umidade': self._correlacao_pearson(velocidades, umidades),
                'temperatura_umidade': self._correlacao_pearson(temperaturas, umidades)
            }
        except:
            return {}
    
    def _correlacao_pearson(self, x: List[float], y: List[float]) -> float:
        """Calcula correlação de Pearson entre duas variáveis."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerador = n * sum_xy - sum_x * sum_y
        denominador = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        
        return numerador / denominador if denominador != 0 else 0.0
    
    def _calcular_fator_altura(self, altura_referencia: float, altura_desejada: float,
                              alpha: float = 0.15) -> float:
        """Calcula fator de correção para altura usando lei da potência."""
        return (altura_desejada / altura_referencia) ** alpha
    
    def _interpolar_potencia(self, velocidade: float, 
                           curva_potencia: List[Tuple[float, float]]) -> float:
        """Interpola potência baseada na curva de potência da turbina."""
        if not curva_potencia:
            return 0.0
        
        # Se velocidade está fora da faixa, retorna valores extremos
        if velocidade <= curva_potencia[0][0]:
            return curva_potencia[0][1]
        
        if velocidade >= curva_potencia[-1][0]:
            return curva_potencia[-1][1]
        
        # Interpolação linear
        for i in range(len(curva_potencia) - 1):
            v1, p1 = curva_potencia[i]
            v2, p2 = curva_potencia[i + 1]
            
            if v1 <= velocidade <= v2:
                # Interpolação linear
                fator = (velocidade - v1) / (v2 - v1)
                return p1 + fator * (p2 - p1)
        
        return 0.0


class ProcessamentoSerieTemporalService:
    """
    Serviço para processamento de séries temporais de vento.
    
    Fornece métodos para análise de tendências, preenchimento de lacunas
    e suavização de dados de séries temporais.
    """
    
    def __init__(self):
        """Inicializa o serviço de processamento."""
        pass
    
    def detectar_lacunas(self, dados: List[DadosEolicos]) -> List[Dict[str, Any]]:
        """
        Detecta lacunas na série temporal.
        
        Args:
            dados: Lista de dados eólicos ordenados por data
        
        Returns:
            Lista de lacunas encontradas
        """
        if len(dados) < 2:
            return []
        
        # Ordena dados por data
        dados_ordenados = sorted(dados, key=lambda x: x.data)
        lacunas = []
        
        for i in range(len(dados_ordenados) - 1):
            data_atual = dados_ordenados[i].data
            data_proxima = dados_ordenados[i + 1].data
            
            diferenca = (data_proxima - data_atual).days
            
            if diferenca > 1:  # Lacuna de mais de 1 dia
                lacunas.append({
                    'inicio': data_atual,
                    'fim': data_proxima,
                    'dias_faltando': diferenca - 1
                })
        
        return lacunas
    
    def calcular_tendencia(self, dados: List[DadosEolicos]) -> Dict[str, Any]:
        """
        Calcula tendência temporal nos dados de vento.
        
        Args:
            dados: Lista de dados eólicos
        
        Returns:
            Análise de tendência
        """
        if len(dados) < 10:
            return {'tendencia': 'insuficiente_dados'}
        
        # Ordena por data e prepara dados
        dados_ordenados = sorted(dados, key=lambda x: x.data)
        
        # Converte datas para números (dias desde o início)
        data_inicio = dados_ordenados[0].data
        x = [(d.data - data_inicio).days for d in dados_ordenados]
        y = [d.velocidade_vento for d in dados_ordenados]
        
        # Calcula regressão linear simples
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        # Coeficientes da regressão
        denominador = n * sum_x2 - sum_x ** 2
        if denominador == 0:
            return {'tendencia': 'sem_tendencia'}
        
        inclinacao = (n * sum_xy - sum_x * sum_y) / denominador
        intercepto = (sum_y - inclinacao * sum_x) / n
        
        # Classifica tendência
        if abs(inclinacao) < 0.001:
            classificacao = 'estavel'
        elif inclinacao > 0:
            classificacao = 'crescente'
        else:
            classificacao = 'decrescente'
        
        return {
            'tendencia': classificacao,
            'inclinacao_m_por_s_por_dia': inclinacao,
            'intercepto': intercepto,
            'variacao_anual_estimada': inclinacao * 365,
            'periodo_analise_dias': max(x) - min(x)
        }
    
    def suavizar_serie(self, dados: List[DadosEolicos], 
                      janela: int = 7) -> List[DadosEolicos]:
        """
        Aplica suavização por média móvel na série temporal.
        
        Args:
            dados: Lista de dados eólicos
            janela: Tamanho da janela de suavização
        
        Returns:
            Lista de dados suavizados
        """
        if len(dados) < janela:
            return dados.copy()
        
        dados_ordenados = sorted(dados, key=lambda x: x.data)
        dados_suavizados = []
        
        for i in range(len(dados_ordenados)):
            # Define janela centrada
            inicio = max(0, i - janela // 2)
            fim = min(len(dados_ordenados), i + janela // 2 + 1)
            
            # Calcula médias da janela
            janela_dados = dados_ordenados[inicio:fim]
            velocidade_suavizada = mean(d.velocidade_vento for d in janela_dados)
            temperatura_suavizada = mean(d.temperatura for d in janela_dados)
            umidade_suavizada = mean(d.umidade for d in janela_dados)
            
            # Cria novo dado suavizado
            dado_original = dados_ordenados[i]
            dado_suavizado = DadosEolicos(
                cidade=dado_original.cidade,
                latitude=dado_original.latitude,
                longitude=dado_original.longitude,
                temperatura=temperatura_suavizada,
                umidade=umidade_suavizada,
                velocidade_vento=velocidade_suavizada,
                direcao_vento=dado_original.direcao_vento,
                velocidade_vento_max=dado_original.velocidade_vento_max,
                data=dado_original.data,
                altura_medicao=dado_original.altura_medicao
            )
            
            dados_suavizados.append(dado_suavizado)
        
        return dados_suavizados
    
    def identificar_outliers(self, dados: List[DadosEolicos],
                           metodo: str = 'iqr') -> List[int]:
        """
        Identifica outliers na série temporal.
        
        Args:
            dados: Lista de dados eólicos
            metodo: Método de detecção ('iqr' ou 'zscore')
        
        Returns:
            Lista de índices dos outliers
        """
        if len(dados) < 4:
            return []
        
        velocidades = [d.velocidade_vento for d in dados]
        outliers = []
        
        if metodo == 'iqr':
            # Método do intervalo interquartil
            velocidades_ordenadas = sorted(velocidades)
            n = len(velocidades_ordenadas)
            
            q1 = velocidades_ordenadas[n // 4]
            q3 = velocidades_ordenadas[3 * n // 4]
            iqr = q3 - q1
            
            limite_inferior = q1 - 1.5 * iqr
            limite_superior = q3 + 1.5 * iqr
            
            for i, velocidade in enumerate(velocidades):
                if velocidade < limite_inferior or velocidade > limite_superior:
                    outliers.append(i)
        
        elif metodo == 'zscore':
            # Método do Z-score
            media = mean(velocidades)
            desvio = stdev(velocidades) if len(velocidades) > 1 else 0
            
            if desvio > 0:
                for i, velocidade in enumerate(velocidades):
                    zscore = abs(velocidade - media) / desvio
                    if zscore > 3:  # Threshold comum para outliers
                        outliers.append(i)
        
        return outliers
