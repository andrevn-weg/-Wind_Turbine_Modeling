#!/usr/bin/env python3
"""
Exemplo de integração meteorológica com dados reais - Sistema de Simulação de Turbinas Eólicas

Este script demonstra a integração do módulo meteorológico com:
- Importação de dados reais (simulados)
- Análise estatística de dados de vento
- Relatórios de viabilidade eólica
- Visualização de dados meteorológicos

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importações dos módulos
from meteorological import (
    MeteorologicalDataSource, MeteorologicalDataSourceRepository,
    MeteorologicalData, MeteorologicalDataRepository
)
from geographic.cidade.entity import Cidade
from geographic.cidade.repository import CidadeRepository


class AnalisadorDadosMeteorologicos:
    """Classe para análise de dados meteorológicos e viabilidade eólica"""
    
    def __init__(self):
        self.dados_repo = MeteorologicalDataRepository()
        self.cidade_repo = CidadeRepository()
    
    def calcular_potencial_eolico(self, cidade_id: int, altura_turbina: float = 50.0) -> Dict:
        """
        Calcula o potencial eólico de uma cidade baseado nos dados disponíveis.
        
        Args:
            cidade_id: ID da cidade para análise
            altura_turbina: Altura da turbina em metros (padrão: 50m)
            
        Returns:
            Dict: Relatório de potencial eólico
        """
        dados = self.dados_repo.buscar_por_cidade(cidade_id)
        
        if not dados:
            return {"erro": "Sem dados meteorológicos para esta cidade"}
        
        # Filtrar apenas dados com velocidade de vento
        dados_vento = [d for d in dados if d.tem_dados_vento()]
        
        if not dados_vento:
            return {"erro": "Sem dados de vento para esta cidade"}
        
        velocidades = [d.velocidade_vento for d in dados_vento]
        
        # Correção para altura da turbina (lei de potência)
        # V2 = V1 * (H2/H1)^α, onde α ≈ 0.2 para terrenos abertos
        alpha = 0.2
        velocidades_corrigidas = []
        
        for i, d in enumerate(dados_vento):
            altura_medida = d.altura_captura or 10.0  # Padrão 10m se não especificado
            fator_correcao = (altura_turbina / altura_medida) ** alpha
            velocidade_corrigida = velocidades[i] * fator_correcao
            velocidades_corrigidas.append(velocidade_corrigida)
        
        # Estatísticas básicas
        velocidade_media = sum(velocidades_corrigidas) / len(velocidades_corrigidas)
        velocidade_maxima = max(velocidades_corrigidas)
        velocidade_minima = min(velocidades_corrigidas)
        
        # Classificação de viabilidade
        if velocidade_media >= 7.0:
            viabilidade = "Excelente"
        elif velocidade_media >= 5.5:
            viabilidade = "Boa"
        elif velocidade_media >= 4.0:
            viabilidade = "Moderada"
        else:
            viabilidade = "Baixa"
        
        # Distribuição de velocidades
        distribuicao = {
            "0-3 m/s": len([v for v in velocidades_corrigidas if v < 3]),
            "3-5 m/s": len([v for v in velocidades_corrigidas if 3 <= v < 5]),
            "5-7 m/s": len([v for v in velocidades_corrigidas if 5 <= v < 7]),
            "7-10 m/s": len([v for v in velocidades_corrigidas if 7 <= v < 10]),
            "10+ m/s": len([v for v in velocidades_corrigidas if v >= 10])
        }
        
        # Estimativa de potência (usando uma turbina típica de 2MW)
        # P = 0.5 * ρ * A * V³ * Cp (simplificado)
        densidade_ar = 1.225  # kg/m³ ao nível do mar
        area_turbina = 5027  # m² (raio ~40m para turbina 2MW)
        cp = 0.35  # Coeficiente de potência típico
        
        potencias = []
        for v in velocidades_corrigidas:
            if v >= 3.5 and v <= 25:  # Faixa operacional típica
                potencia = 0.5 * densidade_ar * area_turbina * (v ** 3) * cp / 1000000  # MW
                potencia = min(potencia, 2.0)  # Limite de 2MW
                potencias.append(potencia)
            else:
                potencias.append(0.0)  # Fora da faixa operacional
        
        potencia_media = sum(potencias) / len(potencias) if potencias else 0
        fator_capacidade = potencia_media / 2.0 * 100 if potencia_media > 0 else 0
        
        return {
            "cidade_id": cidade_id,
            "altura_turbina": altura_turbina,
            "total_registros": len(dados_vento),
            "periodo_dias": (max(d.data for d in dados_vento) - min(d.data for d in dados_vento)).days,
            "velocidade_media": round(velocidade_media, 2),
            "velocidade_maxima": round(velocidade_maxima, 2),
            "velocidade_minima": round(velocidade_minima, 2),
            "viabilidade": viabilidade,
            "distribuicao_velocidades": distribuicao,
            "potencia_media_MW": round(potencia_media, 3),
            "fator_capacidade_pct": round(fator_capacidade, 1),
            "energia_anual_MWh": round(potencia_media * 8760, 0)
        }


def simular_dados_reais():
    """Simula importação de dados meteorológicos reais"""
    print("📡 === SIMULAÇÃO DE IMPORTAÇÃO DE DADOS REAIS ===")
    
    fonte_repo = MeteorologicalDataSourceRepository()
    dados_repo = MeteorologicalDataRepository()
    cidade_repo = CidadeRepository()
    
    # Verificar se temos cidades cadastradas
    cidades = cidade_repo.listar_todos()
    if not cidades:
        print("❌ Necessário ter cidades cadastradas para simular dados")
        return
    
    # Criar fonte NASA_POWER se não existir
    nasa_fonte = fonte_repo.buscar_por_nome("NASA_POWER")
    if not nasa_fonte:
        nasa_fonte = MeteorologicalDataSource(
            name="NASA_POWER",
            description="NASA Prediction of Worldwide Energy Resources - Dados reais simulados"
        )
        fonte_id = fonte_repo.salvar(nasa_fonte)
        nasa_fonte.id = fonte_id
    
    print(f"📊 Usando fonte: {nasa_fonte.name}")
    
    # Simular dados para as 3 primeiras cidades
    for cidade in cidades[:3]:
        print(f"\n🏙️ Importando dados para: {cidade.nome}")
        
        # Simular 1 ano de dados (1 registro por dia)
        data_inicial = date.today() - timedelta(days=365)
        
        # Parâmetros base para cada cidade (simulando características regionais)
        if "Sul" in cidade.nome or cidade.latitude < -25:
            # Região Sul - ventos mais fortes
            velocidade_base = 6.5
            temp_base = 20.0
        elif "Nordeste" in cidade.nome or cidade.latitude < -8:
            # Região Nordeste - ventos constantes
            velocidade_base = 8.0
            temp_base = 28.0
        else:
            # Outras regiões
            velocidade_base = 5.0
            temp_base = 24.0
        
        dados_criados = 0
        for dia in range(365):
            data_registro = data_inicial + timedelta(days=dia)
            
            # Variações sazonais e aleatórias
            variacao_sazonal = 1.0 + 0.3 * (random.random() - 0.5)  # ±15%
            variacao_diaria = 1.0 + 0.5 * (random.random() - 0.5)   # ±25%
            
            velocidade = velocidade_base * variacao_sazonal * variacao_diaria
            velocidade = max(0.1, velocidade)  # Mínimo 0.1 m/s
            
            temperatura = temp_base + random.uniform(-8, 8)  # Variação de temperatura
            umidade = random.uniform(40, 90)  # Umidade entre 40-90%
            altura = random.choice([10, 20, 30, 50])  # Diferentes alturas de medição
            
            # Criar registro meteorológico
            dados = MeteorologicalData(
                meteorological_data_source_id=nasa_fonte.id,
                cidade_id=cidade.id,
                data=data_registro,
                altura_captura=altura,
                velocidade_vento=round(velocidade, 1),
                temperatura=round(temperatura, 1),
                umidade=round(umidade, 1)
            )
            
            try:
                dados_repo.salvar(dados)
                dados_criados += 1
                
                # Mostrar progresso a cada 50 registros
                if dados_criados % 50 == 0:
                    print(f"   📈 {dados_criados}/365 registros criados...")
            except Exception as e:
                print(f"   ⚠️ Erro ao salvar dados: {e}")
        
        print(f"   ✅ Total criado: {dados_criados} registros")


def gerar_relatorio_viabilidade():
    """Gera relatório de viabilidade eólica para todas as cidades"""
    print("\n📊 === RELATÓRIO DE VIABILIDADE EÓLICA ===")
    
    analisador = AnalisadorDadosMeteorologicos()
    cidade_repo = CidadeRepository()
    
    cidades = cidade_repo.listar_todos()
    
    if not cidades:
        print("❌ Nenhuma cidade encontrada para análise")
        return
    
    relatorios = []
    
    for cidade in cidades:
        print(f"\n🏙️ Analisando: {cidade.nome}")
        
        # Análise para diferentes alturas de turbina
        for altura in [30, 50, 80]:
            relatorio = analisador.calcular_potencial_eolico(cidade.id, altura)
            
            if "erro" not in relatorio:
                relatorio["cidade_nome"] = cidade.nome
                relatorio["latitude"] = cidade.latitude
                relatorio["longitude"] = cidade.longitude
                relatorios.append(relatorio)
                
                print(f"   📏 Altura {altura}m:")
                print(f"      💨 Velocidade média: {relatorio['velocidade_media']} m/s")
                print(f"      🎯 Viabilidade: {relatorio['viabilidade']}")
                print(f"      ⚡ Fator de capacidade: {relatorio['fator_capacidade_pct']}%")
                print(f"      🔋 Energia anual: {relatorio['energia_anual_MWh']} MWh")
            else:
                print(f"   ❌ {relatorio['erro']}")
    
    # Resumo geral
    if relatorios:
        print(f"\n📈 === RESUMO GERAL ({len(relatorios)} análises) ===")
        
        # Melhores localizações por fator de capacidade
        relatorios_ordenados = sorted(relatorios, key=lambda x: x['fator_capacidade_pct'], reverse=True)
        
        print("\n🏆 TOP 5 - Melhores localizações:")
        for i, rel in enumerate(relatorios_ordenados[:5], 1):
            print(f"   {i}. {rel['cidade_nome']} ({rel['altura_turbina']}m): "
                  f"{rel['fator_capacidade_pct']}% FC, {rel['velocidade_media']} m/s")
        
        # Estatísticas gerais
        fatores_capacidade = [r['fator_capacidade_pct'] for r in relatorios]
        fc_medio = sum(fatores_capacidade) / len(fatores_capacidade)
        
        print(f"\n📊 Estatísticas gerais:")
        print(f"   📈 Fator de capacidade médio: {fc_medio:.1f}%")
        print(f"   🎯 Localizações viáveis (FC > 25%): {len([f for f in fatores_capacidade if f > 25])}")
        print(f"   ⭐ Localizações excelentes (FC > 40%): {len([f for f in fatores_capacidade if f > 40])}")
    
    return relatorios


def exemplo_consultas_avancadas():
    """Demonstra consultas SQL avançadas e análises personalizadas"""
    print("\n🔍 === CONSULTAS AVANÇADAS E ANÁLISES ===")
    
    dados_repo = MeteorologicalDataRepository()
    
    # 1. Análise temporal de dados
    print("\n1️⃣ Análise temporal dos dados...")
    dados_completos = dados_repo.buscar_com_detalhes_cidade(limite=1000)
    
    if dados_completos:
        # Agrupar por mês
        dados_por_mes = {}
        for dados in dados_completos:
            if dados['data'] and dados['velocidade_vento']:
                mes = dados['data'][:7]  # YYYY-MM
                if mes not in dados_por_mes:
                    dados_por_mes[mes] = []
                dados_por_mes[mes].append(dados['velocidade_vento'])
        
        print(f"   📅 Dados disponíveis para {len(dados_por_mes)} meses")
        
        # Mostrar médias mensais
        meses_ordenados = sorted(dados_por_mes.keys())[-6:]  # Últimos 6 meses
        for mes in meses_ordenados:
            velocidades = dados_por_mes[mes]
            media_mensal = sum(velocidades) / len(velocidades)
            print(f"      {mes}: {media_mensal:.2f} m/s (média de {len(velocidades)} registros)")
    
    # 2. Comparação entre fontes de dados
    print("\n2️⃣ Comparação entre fontes de dados...")
    fonte_repo = MeteorologicalDataSourceRepository()
    fontes = fonte_repo.listar_todos()
    
    for fonte in fontes:
        dados_fonte = dados_repo.buscar_por_fonte(fonte.id, limite=100)
        if dados_fonte:
            velocidades = [d.velocidade_vento for d in dados_fonte if d.velocidade_vento]
            if velocidades:
                media = sum(velocidades) / len(velocidades)
                print(f"   📊 {fonte.name}: {len(dados_fonte)} registros, "
                      f"vento médio {media:.2f} m/s")
    
    # 3. Identificação de padrões
    print("\n3️⃣ Identificação de padrões de vento...")
    
    # Buscar dias com vento forte (>10 m/s)
    todos_dados = dados_repo.listar_todos(limite=500)
    dias_vento_forte = [d for d in todos_dados if d.velocidade_vento and d.velocidade_vento > 10]
    
    print(f"   💨 Dias com vento forte (>10 m/s): {len(dias_vento_forte)}")
    
    if dias_vento_forte:
        velocidade_maxima = max(d.velocidade_vento for d in dias_vento_forte)
        print(f"   🌪️ Velocidade máxima registrada: {velocidade_maxima} m/s")
        
        # Agrupar por cidade para identificar locais mais ventosos
        cidades_ventosas = {}
        for dados in dias_vento_forte:
            cidade_id = dados.cidade_id
            if cidade_id not in cidades_ventosas:
                cidades_ventosas[cidade_id] = 0
            cidades_ventosas[cidade_id] += 1
        
        cidade_repo = CidadeRepository()
        print("   🏙️ Cidades com mais dias de vento forte:")
        for cidade_id, dias in sorted(cidades_ventosas.items(), key=lambda x: x[1], reverse=True)[:3]:
            cidade = cidade_repo.buscar_por_id(cidade_id)
            nome_cidade = cidade.nome if cidade else f"ID {cidade_id}"
            print(f"      • {nome_cidade}: {dias} dias")


def exportar_relatorio_json(relatorios: List[Dict], arquivo: str = "relatorio_viabilidade_eolica.json"):
    """Exporta relatório de viabilidade para arquivo JSON"""
    print(f"\n💾 Exportando relatório para {arquivo}...")
    
    dados_exportacao = {
        "timestamp": datetime.now().isoformat(),
        "total_analises": len(relatorios),
        "versao": "1.0",
        "relatorios": relatorios
    }
    
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_exportacao, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Relatório exportado com sucesso!")
    except Exception as e:
        print(f"   ❌ Erro ao exportar: {e}")


def main():
    """Função principal que executa a demonstração completa"""
    print("🌍 === INTEGRAÇÃO METEOROLÓGICA COM DADOS REAIS ===")
    print("Sistema de Simulação de Turbinas Eólicas")
    print("Demonstração de análise de viabilidade eólica\n")
    
    try:
        # 1. Simular importação de dados reais
        simular_dados_reais()
        
        # 2. Gerar relatório de viabilidade
        relatorios = gerar_relatorio_viabilidade()
        
        # 3. Consultas avançadas
        exemplo_consultas_avancadas()
        
        # 4. Exportar relatórios
        if relatorios:
            exportar_relatorio_json(relatorios)
        
        print("\n✅ === DEMONSTRAÇÃO DE INTEGRAÇÃO CONCLUÍDA ===")
        print("🎯 Módulo meteorológico totalmente funcional!")
        print("📊 Análises de viabilidade eólica realizadas com sucesso!")
        print("🌪️ Sistema pronto para simulação de turbinas eólicas!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
