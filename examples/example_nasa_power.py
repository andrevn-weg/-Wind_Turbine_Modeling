#!/usr/bin/env python3
"""
Exemplo de uso da API NASA POWER

Este script demonstra como usar o cliente NASA POWER para obter dados históricos
de velocidade do vento para cidades cadastradas no banco de dados.

O exemplo faz requisições para ambas as alturas disponíveis (10m e 50m)
e exibe os dados obtidos, incluindo estatísticas básicas.

IMPORTANTE: Este exemplo NÃO grava dados no banco de dados.

Autor: André Vinícius Lima do Nascimento
Data: 2025
"""

import sys
import os
from datetime import date, timedelta
import json

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importações do módulo meteorológico
from meteorological.api.nasa_power import NASAPowerClient

# Importações do módulo geográfico para buscar cidades
from geographic.cidade.repository import CidadeRepository


def exibir_informacoes_api():
    """Exibe informações sobre a API NASA POWER"""
    print("🛰️ === INFORMAÇÕES DA API NASA POWER ===")
    
    client = NASAPowerClient()
    info = client.obter_informacoes_api()
    
    print(f"📊 Nome: {info['nome']}")
    print(f"🔗 URL: {info['url_base']}")
    print(f"📏 Alturas suportadas: {info['alturas_suportadas']} (apenas 10m e 50m)")
    print(f"📈 Frequência: {info['frequencia_dados']}")
    print(f"🎯 Resolução espacial: {info['resolucao_espacial']}")
    print(f"⏰ Atraso de dados: {info['atraso_dados']}")
    print(f"💰 Gratuita: {info['gratuita']}")
    print(f"📚 Documentação: {info['documentacao']}")
    print(f"🛰️ Fonte: {info['fonte_dados']}")
    
    # Exibir parâmetros disponíveis
    print(f"\n📋 Parâmetros de vento disponíveis:")
    parametros = client.obter_parametros_disponiveis()
    for param, info in parametros.items():
        print(f"   🔸 {param}: {info['nome']} ({info['altura']}m)")
        print(f"      📝 {info['descricao']}")
        print(f"      📏 Unidade: {info['unidade']}")
    print()


def buscar_cidades_exemplo():
    """Busca cidades do banco de dados para os exemplos"""
    print("🏙️ === BUSCANDO CIDADES NO BANCO DE DADOS ===")
    
    cidade_repo = CidadeRepository()
    
    try:
        cidades = cidade_repo.listar_todos()
        
        if not cidades:
            print("❌ Nenhuma cidade encontrada no banco de dados!")
            print("   Execute primeiro os exemplos geográficos para cadastrar cidades.")
            return []
        
        print(f"✅ Encontradas {len(cidades)} cidades cadastradas:")
        for cidade in cidades[:5]:  # Mostrar apenas as primeiras 5
            print(f"   🌍 {cidade.nome} - Lat: {cidade.latitude}, Lon: {cidade.longitude}")
        
        if len(cidades) > 5:
            print(f"   ... e mais {len(cidades) - 5} cidades")
        
        print()
        return cidades
        
    except Exception as e:
        print(f"❌ Erro ao buscar cidades: {e}")
        return []


def verificar_disponibilidade_periodo(client: NASAPowerClient, ano: int):
    """Verifica se o período solicitado está disponível"""
    print(f"🔍 === VERIFICANDO DISPONIBILIDADE DO ANO {ano} ===")
    
    data_inicio = date(ano, 1, 1)
    data_fim = date(ano, 12, 31)
    
    try:
        verificacao = client.verificar_disponibilidade_periodo(data_inicio, data_fim)
        
        print(f"📅 Período solicitado: {verificacao['data_inicio_solicitada']} a {verificacao['data_fim_solicitada']}")
        print(f"🕐 Duração: {verificacao['periodo_dias']} dias")
        print(f"✅ Disponível: {'Sim' if verificacao['disponivel'] else 'Não'}")
        print(f"📊 Dados disponíveis desde: {verificacao['data_minima_disponivel']}")
        print(f"📊 Dados disponíveis até: {verificacao['data_maxima_disponivel']}")
        
        if verificacao['avisos']:
            print(f"⚠️ Avisos:")
            for aviso in verificacao['avisos']:
                print(f"   • {aviso}")
        
        print()
        return verificacao['disponivel']
        
    except Exception as e:
        print(f"❌ Erro ao verificar disponibilidade: {e}")
        return False


def requisitar_dados_cidade(client: NASAPowerClient, cidade, ano: int = 2023):
    """
    Faz requisição de dados para uma cidade específica em ambas as alturas disponíveis.
    
    Args:
        client: Cliente NASA POWER inicializado
        cidade: Objeto cidade do banco de dados
        ano: Ano para requisição (padrão: 2023 - mais provável de ter dados completos)
    """
    print(f"🛰️ === REQUISITANDO DADOS PARA {cidade.nome.upper()} ===")
    print(f"📍 Coordenadas: {cidade.latitude}, {cidade.longitude}")
    print(f"📅 Período: Ano {ano} completo")
    print(f"📏 Alturas: Ambas disponíveis ({client.ALTURAS_SUPORTADAS})")
    
    try:
        # Fazer requisição para ambas as alturas de uma vez
        print("⏳ Fazendo requisição... (NASA POWER pode ser lenta)")
        
        dados = client.obter_dados_ano_completo(
            latitude=cidade.latitude,
            longitude=cidade.longitude,
            ano=ano,
            alturas=None  # Ambas as alturas (10m e 50m)
        )
        
        # Exibir metadados
        metadata = dados['metadata']
        print(f"\n📊 Metadados da requisição:")
        print(f"   🛰️ Fonte: {metadata['fonte']}")
        print(f"   📅 Período: {metadata['periodo_inicio']} a {metadata['periodo_fim']}")
        print(f"   📈 Total de registros: {metadata['total_registros']}")
        
        if metadata.get('mensagens'):
            print(f"   📝 Mensagens da API: {metadata['mensagens']}")
        
        # Exibir dados por altura
        print(f"\n📏 Dados por altura:")
        for altura_key, dados_altura in dados['dados_por_altura'].items():
            altura = dados_altura['altura_metros']
            param_nasa = dados_altura['parametro_nasa']
            stats = dados_altura['estatisticas']
            
            print(f"\n   🏗️ Altura: {altura}m (Parâmetro NASA: {param_nasa})")
            print(f"      💨 Velocidade média: {stats['velocidade_media']:.2f} m/s")
            print(f"      📈 Velocidade máxima: {stats['velocidade_maxima']:.2f} m/s")
            print(f"      📉 Velocidade mínima: {stats['velocidade_minima']:.2f} m/s")
            print(f"      📊 Registros válidos: {stats['total_registros']}")
            print(f"      ❌ Registros nulos: {stats['registros_nulos']}")
            
            # Classificar qualidade do vento
            velocidade_media = stats['velocidade_media']
            if velocidade_media >= 7.0:
                qualidade = "🌟 Excelente para energia eólica"
            elif velocidade_media >= 5.5:
                qualidade = "✅ Boa para energia eólica" 
            elif velocidade_media >= 4.0:
                qualidade = "⚠️ Moderada para energia eólica"
            else:
                qualidade = "❌ Baixa para energia eólica"
            
            print(f"      🎯 Avaliação: {qualidade}")
            
            # Comparação entre alturas (se temos dados de ambas)
            if len(dados['dados_por_altura']) == 2:
                print(f"      📊 Cobertura de dados: {(stats['total_registros'] / metadata['total_registros'] * 100):.1f}%")
        
        # Análise comparativa entre alturas
        if len(dados['dados_por_altura']) == 2:
            print(f"\n🔄 Análise comparativa entre alturas:")
            dados_10m = dados['dados_por_altura']['10m']['estatisticas']
            dados_50m = dados['dados_por_altura']['50m']['estatisticas']
            
            diferenca_media = dados_50m['velocidade_media'] - dados_10m['velocidade_media']
            percentual_aumento = (diferenca_media / dados_10m['velocidade_media'] * 100) if dados_10m['velocidade_media'] > 0 else 0
            
            print(f"   📈 Aumento de 10m para 50m: {diferenca_media:.2f} m/s ({percentual_aumento:.1f}%)")
            print(f"   🎯 Recomendação: {'Altura de 50m mais favorável' if diferenca_media > 1.0 else 'Diferença moderada entre alturas'}")
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro na requisição para {cidade.nome}: {e}")
        print(f"   💡 Dica: NASA POWER pode ter limitações de dados recentes ou problemas de conectividade")
        return None


def salvar_dados_arquivo(dados, nome_cidade: str, ano: int):
    """
    Salva os dados obtidos em arquivo JSON local (opcional).
    
    Args:
        dados: Dados retornados pela API
        nome_cidade: Nome da cidade para o arquivo
        ano: Ano dos dados
    """
    if not dados:
        return
    
    nome_arquivo = f"nasa_power_{nome_cidade.lower().replace(' ', '_')}_{ano}.json"
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Dados salvos em: {nome_arquivo}")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar arquivo: {e}")


def exemplo_requisicao_periodo_customizado():
    """Exemplo de requisição para período customizado"""
    print("\n🗓️ === EXEMPLO DE PERÍODO CUSTOMIZADO ===")
    
    client = NASAPowerClient()
    
    # Exemplo: 6 meses de 2023 para uma coordenada específica
    data_inicio = date(2023, 6, 1)   # Junho
    data_fim = date(2023, 11, 30)    # Novembro
    
    # Coordenadas de exemplo (Brasília, DF)
    latitude = -15.7801
    longitude = -47.9292
    
    print(f"📍 Coordenadas de exemplo: {latitude}, {longitude} (Brasília)")
    print(f"📅 Período: {data_inicio} a {data_fim}")
    print(f"📏 Alturas: Apenas 50m")
    
    # Verificar disponibilidade primeiro
    verificacao = client.verificar_disponibilidade_periodo(data_inicio, data_fim)
    
    if not verificacao['disponivel']:
        print("⚠️ Período não disponível, ajustando...")
        data_inicio = date(2022, 6, 1)
        data_fim = date(2022, 11, 30)
        print(f"📅 Novo período: {data_inicio} a {data_fim}")
    
    try:
        print("⏳ Fazendo requisição customizada...")
        
        dados = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[50]  # Apenas altura de 50m
        )
        
        print(f"✅ Requisição bem-sucedida!")
        print(f"📊 Total de registros: {dados['metadata']['total_registros']}")
        
        for altura_key, dados_altura in dados['dados_por_altura'].items():
            stats = dados_altura['estatisticas']
            print(f"   {altura_key}: {stats['velocidade_media']:.2f} m/s (média), {stats['velocidade_maxima']:.2f} m/s (máximo)")
    
    except Exception as e:
        print(f"❌ Erro na requisição personalizada: {e}")


def testar_validacoes():
    """Testa as validações do cliente NASA POWER"""
    print("\n🧪 === TESTANDO VALIDAÇÕES ===")
    
    client = NASAPowerClient()
    
    # Teste 1: Altura não suportada
    print("1️⃣ Testando altura não suportada (80m):")
    try:
        client.validar_altura(80)
        print("   ❌ Deveria ter dado erro!")
    except ValueError as e:
        print(f"   ✅ Erro esperado: {e}")
    
    # Teste 2: Alturas válidas
    print("\n2️⃣ Testando alturas válidas:")
    for altura in [10, 50]:
        try:
            client.validar_altura(altura)
            print(f"   ✅ {altura}m: Válida")
        except ValueError as e:
            print(f"   ❌ {altura}m: {e}")
    
    # Teste 3: Alturas inválidas
    print("\n3️⃣ Testando alturas inválidas:")
    for altura in [20, 80, 100, 120]:
        try:
            client.validar_altura(altura)
            print(f"   ❌ {altura}m: Deveria ter dado erro!")
        except ValueError as e:
            print(f"   ✅ {altura}m: {e}")
    
    # Teste 4: Verificação de período muito recente
    print("\n4️⃣ Testando período muito recente:")
    data_recente = date.today() - timedelta(days=1)
    verificacao = client.verificar_disponibilidade_periodo(data_recente, date.today())
    print(f"   📅 Período recente disponível: {verificacao['disponivel']}")
    if verificacao['avisos']:
        for aviso in verificacao['avisos']:
            print(f"   ⚠️ {aviso}")


def comparar_dados_exemplo():
    """Exemplo comparando dados de diferentes períodos"""
    print("\n📊 === COMPARAÇÃO ENTRE PERÍODOS ===")
    
    client = NASAPowerClient()
    
    # Coordenadas de exemplo (Salvador, BA)
    latitude = -12.9714
    longitude = -38.5014
    
    print(f"📍 Localização: Salvador, BA ({latitude}, {longitude})")
    
    # Comparar dois anos diferentes
    anos = [2022, 2021]
    resultados = {}
    
    for ano in anos:
        print(f"\n📅 Obtendo dados de {ano}...")
        
        try:
            # Usar apenas 3 meses para agilizar o exemplo
            data_inicio = date(ano, 6, 1)   # Junho
            data_fim = date(ano, 8, 31)     # Agosto
            
            dados = client.obter_dados_historicos_vento(
                latitude=latitude,
                longitude=longitude,
                data_inicio=data_inicio,
                data_fim=data_fim,
                alturas=[50]  # Apenas 50m
            )
            
            if dados and '50m' in dados['dados_por_altura']:
                stats = dados['dados_por_altura']['50m']['estatisticas']
                resultados[ano] = stats['velocidade_media']
                print(f"   ✅ {ano}: {stats['velocidade_media']:.2f} m/s (média)")
            else:
                print(f"   ❌ {ano}: Sem dados disponíveis")
                
        except Exception as e:
            print(f"   ❌ {ano}: Erro na requisição - {e}")
    
    # Comparar resultados
    if len(resultados) == 2:
        anos_ordenados = sorted(resultados.keys())
        ano1, ano2 = anos_ordenados
        diferenca = resultados[ano2] - resultados[ano1]
        
        print(f"\n📈 Comparação entre {ano1} e {ano2}:")
        print(f"   🔸 {ano1}: {resultados[ano1]:.2f} m/s")
        print(f"   🔸 {ano2}: {resultados[ano2]:.2f} m/s") 
        print(f"   📊 Diferença: {diferenca:+.2f} m/s")
        
        if abs(diferenca) < 0.5:
            print(f"   🎯 Análise: Ventos similares entre os anos")
        elif diferenca > 0:
            print(f"   🎯 Análise: {ano2} teve ventos mais fortes")
        else:
            print(f"   🎯 Análise: {ano1} teve ventos mais fortes")


def main():
    """Função principal do exemplo"""
    print("🛰️ === EXEMPLO DE USO DA API NASA POWER ===")
    print("Sistema de Simulação de Turbinas Eólicas")
    print("Demonstração de requisição de dados meteorológicos\n")
    
    try:
        # 1. Exibir informações da API
        exibir_informacoes_api()
        
        # 2. Buscar cidades do banco
        cidades = buscar_cidades_exemplo()
        
        if not cidades:
            print("⚠️ Sem cidades disponíveis. Executando exemplos com coordenadas fixas...")
            exemplo_requisicao_periodo_customizado()
            testar_validacoes()
            comparar_dados_exemplo()
            return
        
        # 3. Inicializar cliente
        client = NASAPowerClient(timeout=120)  # Timeout maior para NASA POWER
        
        # 4. Verificar disponibilidade do período
        ano_requisicao = 2023  # Ano mais provável de ter dados completos
        if not verificar_disponibilidade_periodo(client, ano_requisicao):
            ano_requisicao = 2022
            print(f"⚠️ Usando {ano_requisicao} como alternativa")
        
        # 5. Fazer requisições para as primeiras 2 cidades (NASA é mais lenta)
        dados_coletados = []
        
        for i, cidade in enumerate(cidades[:2], 1):
            print(f"\n{'='*60}")
            print(f"🏙️ CIDADE {i}/2")
            
            dados = requisitar_dados_cidade(client, cidade, ano=ano_requisicao)
            
            if dados:
                dados_coletados.append({
                    'cidade': cidade.nome,
                    'dados': dados
                })
                
                # Opcionalmente salvar em arquivo
                # salvar_dados_arquivo(dados, cidade.nome, ano_requisicao)
        
        # 6. Exemplo de período customizado
        exemplo_requisicao_periodo_customizado()
        
        # 7. Testar validações
        testar_validacoes()
        
        # 8. Comparação entre períodos
        comparar_dados_exemplo()
        
        # 9. Resumo final
        print(f"\n🎯 === RESUMO FINAL ===")
        print(f"✅ Cidades processadas: {len(dados_coletados)}")
        print(f"📊 Total de conjuntos de dados: {len(dados_coletados) * len(client.ALTURAS_SUPORTADAS)}")
        print(f"🛰️ API NASA POWER funcionando corretamente!")
        
        if dados_coletados:
            print(f"\n📈 Estatísticas rápidas:")
            for item in dados_coletados:
                nome = item['cidade']
                dados = item['dados']
                
                # Comparar velocidades entre 10m e 50m
                if '10m' in dados['dados_por_altura'] and '50m' in dados['dados_por_altura']:
                    vel_10m = dados['dados_por_altura']['10m']['estatisticas']['velocidade_media']
                    vel_50m = dados['dados_por_altura']['50m']['estatisticas']['velocidade_media']
                    aumento = vel_50m - vel_10m
                    
                    print(f"   🏙️ {nome}:")
                    print(f"      📏 10m: {vel_10m:.2f} m/s")
                    print(f"      📏 50m: {vel_50m:.2f} m/s (+{aumento:.2f} m/s)")
        
        print("\n✅ === EXEMPLO CONCLUÍDO COM SUCESSO ===")
        print("🎉 API NASA POWER integrada e funcionando!")
        print("💡 Dica: NASA POWER é excelente para análises de longo prazo e dados confiáveis!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
