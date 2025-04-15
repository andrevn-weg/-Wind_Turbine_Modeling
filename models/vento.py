import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import math  # Importando o módulo math para usar a função gamma


class Vento:
    topologia = {
            "Liso, gelo, lama": {'Lei Logarítmica': 0.01, 'Lei da Potencia': 0.10},
            "Mar aberto e calmo": {'Lei Logarítmica': 0.20, 'Lei da Potencia': 0.10},
            "Mar agitado": {'Lei Logarítmica': 0.50, 'Lei da Potencia': 0.10},
            "Neve": {'Lei Logarítmica': 3.00, 'Lei da Potencia': 0.10},
            "Gramado": {'Lei Logarítmica': 8.00, 'Lei da Potencia': 0.14},
            "Pasto acidentado": {'Lei Logarítmica': 10.00, 'Lei da Potencia': 0.16},
            "Campo em declive": {'Lei Logarítmica': 30.00, 'Lei da Potencia': 0.16},
            "Cultivado": {'Lei Logarítmica': 50.00, 'Lei da Potencia': 0.20},
            "Poucas árvores": {'Lei Logarítmica': 100.00, 'Lei da Potencia': 0.22},
            "Muitas árvores, poucos edifícios, cercas": {'Lei Logarítmica': 250.00, 'Lei da Potencia': 0.24},
            "Florestas": {'Lei Logarítmica': 500.00, 'Lei da Potencia': 0.28},
            "Subúrbios": {'Lei Logarítmica': 1500.00, 'Lei da Potencia': 0.40},
            "Zonas urbanas com edifícios altos": {'Lei Logarítmica': 3000.00, 'Lei da Potencia': 0.40}
        }
        
    # Dados de velocidade média do vento por região (exemplo)
    dados_locais = {
        "Região Sul": 7.5,
        "Região Nordeste": 8.0,
        "Região Sudeste": 6.5,
        "Região Centro-Oeste": 5.5,
        "Região Norte": 5.0,
        "Florianópolis": 7.2,
        "Fortaleza": 8.5,
        "São Paulo": 6.0,
        "Rio de Janeiro": 6.3,
        "Brasília": 5.8
    }
    
    def __init__(self, local=None, altura=50, periodo=168, vento_medio=None, topologia_terreno="Gramado"): # construtor
        # Parâmetros da interface
        self.local = local
        self.altura = altura
        self.periodo = periodo  # horas
        
        # Se a velocidade média não foi fornecida, tenta obter pelo local
        if vento_medio is None:
            self.vento_medio = self._obter_vento_medio_por_local(local)
        else:
            self.vento_medio = vento_medio
            
        # Obter a topologia do terreno
        self.topologia_terreno = self.topologia.get(self.get_topologia(topologia_terreno))
    
    def _obter_vento_medio_por_local(self, local):
        # Verifica se o local está no dicionário de dados
        if local and local in self.dados_locais:
            return self.dados_locais[local]
        else:
            # Default: retorna uma média geral caso o local não seja encontrado
            return 6.5  # Valor médio default para o Brasil
    
    def msg(self):
        texto = 'Modelo de Serie Temporal.\n'
        texto += ' Parametros Iniciais: \n'
        texto += '  Velocidade Média do Vento: '+str(self.vento_medio) + ' m/s \n'
        texto += '  Altura do dado: ' + str(self.altura) + ' metros \n'
        texto += '  Local: ' + str(self.local) + '\n'
        texto += '  Período: ' + str(self.periodo) + ' horas \n'
        return texto


    def get_topologia(self,buscaTopologia=None):
        if buscaTopologia != None:
            for chave in self.topologia:
                if buscaTopologia in chave:
                    print(f"Chave encontrada: {chave}")
                    print(f"Valores: {self.topologia[chave]}")
                    return chave
        else:
            for terreno in self.topologia:
                print(f'{terreno}')
            return self.topologia
    
    def set_topologia(self,buscaTopologia):
        self.topologia_terreno = self.topologia.get(self.get_topologia(buscaTopologia))
   
    def Lei_Potencia(self, altura_Estipulada):# Estimula a velocidade do vento de acordo com a altura
        # Calcula a velocidade do vento para cada altura na Lei de Potência
        n = self.topologia_terreno['Lei da Potencia']
        VelocidadeVento_LeiPotencia = self.vento_medio * (altura_Estipulada / self.altura) ** n
        return VelocidadeVento_LeiPotencia

    def Lei_Logaritmica(self, altura_Estipulada): # Estimula a velocidade do vento de acordo com a altura
        # Calcula a velocidade do vento para cada altura na Lei Logarítmica
        z0 = self.topologia_terreno['Lei Logarítmica'] / 1000
        if altura_Estipulada > z0:  # Evitar log(0) quando altura_Estipulada == z0
            VelocidadeVento_LeiLogarirmica = self.vento_medio * np.log(altura_Estipulada / z0) / np.log(self.altura / z0)     
        else:
            VelocidadeVento_LeiLogarirmica = 0  # ou algum valor apropriado para quando a altura é menor ou igual a z0     
        return VelocidadeVento_LeiLogarirmica

    def Grafico_Vel_Vento_Estipulado(self, LeiPotencia = False, LeiLogaritmica = False):
        altura_desejado = np.arange(0, 100.1, 0.1)
        V_desejado_LP = np.arange(0, 100.1, 0.1)
        V_desejado_LG = np.arange(0, 100.1, 0.1)
        # Calcula a velocidade do vento para cada altura na Lei de Potência
        for i in range(len(altura_desejado)):
            V_desejado_LP[i] = self.Lei_Potencia(altura_desejado[i])
            V_desejado_LG[i] = self.Lei_Logaritmica(altura_desejado[i])

        if LeiPotencia == True and LeiLogaritmica == False:
            plt.plot(altura_desejado, V_desejado_LP, linewidth=1.5)
            plt.title('Lei da Potência')
            plt.xlabel('Altura (H)')
            plt.ylabel('Velocidade do Vento (V)')
            plt.grid(True)
        
        elif LeiPotencia == False and LeiLogaritmica == True :
            plt.plot(altura_desejado, V_desejado_LG, linewidth=1.5)
            plt.title('Lei da Logaritmica')
            plt.xlabel('Altura (H)')
            plt.ylabel('Velocidade do Vento (V)')
            plt.grid(True)            

        elif LeiPotencia == True and LeiLogaritmica == True :
            #plt.plot(H_desejado, V_desejado_LP, H_desejado, V_desejado_LG, linewidth=1.5)
            plt.plot(altura_desejado, V_desejado_LP, linewidth=1.5, label='Lei da Potência')
            plt.plot(altura_desejado, V_desejado_LG, linewidth=1.5, label='Lei Logarítmica')
            plt.title('Velocidade do Vento')
            plt.xlabel('Altura (H)')
            plt.ylabel('Velocidade do Vento (V)')
            plt.legend()  
            plt.grid(True)
        else :
            plt.subplot(2, 1, 1)
            plt.plot(altura_desejado, V_desejado_LP, linewidth=1.5)
            plt.title('Lei da Potência')
            plt.xlabel('Altura (H)')
            plt.ylabel('Velocidade do Vento (V)')
            plt.grid(True)

            # Gráfico da Lei Logarítmica
            plt.subplot(2, 1, 2)
            plt.plot(altura_desejado, V_desejado_LG, linewidth=1.5)
            plt.title('Lei Logarítmica')
            plt.xlabel('Altura (H)')
            plt.ylabel('Velocidade do Vento (V)')
            plt.grid(True)
        
        return plt

    def gerar_serie_temporal(self):
        """
        Gera uma série temporal de velocidade do vento para o período especificado
        e calcula o potencial eólico correspondente.
        
        Returns:
            tuple: (serie_temporal, potencial_eolico)
                - serie_temporal: DataFrame com a série temporal do vento
                - potencial_eolico: Valor médio do potencial eólico em W/m²
        """
        # Parâmetros para a série temporal
        horas = self.periodo
        intervalo_minutos = 10  # Dados a cada 10 minutos
        n_pontos = int(horas * 60 / intervalo_minutos)
        
        # Velocidade média na altura especificada
        velocidade_media = self.vento_medio
        
        # Parâmetros para a simulação da série temporal
        k = 2.0  # Fator de forma (shape) de Weibull
        c = velocidade_media / math.gamma(1 + 1/k)  # Fator de escala de Weibull usando math.gamma
        
        # Componente determinística: variação diária
        t = np.linspace(0, horas, n_pontos)
        variacao_diaria = 0.2 * velocidade_media * np.sin(2 * np.pi * t / 24)
        
        # Componente aleatória: ruído com distribuição de Weibull
        np.random.seed(42)  # Para reprodutibilidade
        ruido_weibull = np.random.weibull(k, n_pontos) * c * 0.5
        
        # Combinação dos componentes para gerar a série temporal
        velocidade_vento = velocidade_media + variacao_diaria + ruido_weibull - 0.5 * c
        
        # Garantir que a velocidade não seja negativa
        velocidade_vento = np.maximum(velocidade_vento, 0)
        
        # Criar um DataFrame com timestamps
        data_inicio = datetime.now()
        timestamps = [data_inicio + timedelta(minutes=i*intervalo_minutos) for i in range(n_pontos)]
        
        serie_temporal = pd.DataFrame({
            'timestamp': timestamps,
            'velocidade_vento': velocidade_vento
        })
        
        # Calcular o potencial eólico (P = 0.5 * rho * A * v³)
        # Densidade do ar (rho) aproximada: 1.225 kg/m³
        rho = 1.225  # kg/m³
        
        # Potencial eólico em W/m² (por unidade de área)
        serie_temporal['potencial_eolico'] = 0.5 * rho * serie_temporal['velocidade_vento']**3
        
        # Potencial eólico médio
        potencial_eolico_medio = serie_temporal['potencial_eolico'].mean()
        
        return serie_temporal, potencial_eolico_medio