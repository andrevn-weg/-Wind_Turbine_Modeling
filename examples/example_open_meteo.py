#!/usr/bin/env python3
"""
Exemplo de uso da API Open-Meteo

Este script demonstra como usar o cliente Open-Meteo para obter dados históricos
de velocidade do vento para cidades cadastradas no banco de dados.

O exemplo faz requisições para todas as alturas disponíveis (10m, 80m, 120m, 180m)
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
from meteorological.api.open_meteo import OpenMeteoClient

# Importações do módulo geográfico para buscar cidades
from geographic.cidade.repository import CidadeRepository


def exibir_informacoes_api():
    """Exibe informações sobre a API Open-Meteo"""
    print("🌍 === INFORMAÇÕES DA API OPEN-METEO ===")
    
    client = OpenMeteoClient()
    info = client.obter_informacoes_api()
    
    print(f"📊 Nome: {info['nome']}")
    print(f"🔗 URL: {info['url_base']}")
    print(f"📏 Alturas suportadas: {info['alturas_suportadas']}")
    print(f"📈 Frequência: {info['frequencia_dados']}")
    print(f"💰 Gratuita: {info['gratuita']}")
    print(f"📚 Documentação: {info['documentacao']}")
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


def requisitar_dados_cidade(client: OpenMeteoClient, cidade, ano: int = 2024):
    """
    Faz requisição de dados para uma cidade específica em todas as alturas disponíveis.
    
    Args:
        client: Cliente Open-Meteo inicializado
        cidade: Objeto cidade do banco de dados
        ano: Ano para requisição (padrão: 2024)
    """
    print(f"📡 === REQUISITANDO DADOS PARA {cidade.nome.upper()} ===")
    print(f"📍 Coordenadas: {cidade.latitude}, {cidade.longitude}")
    print(f"📅 Período: Ano {ano} completo")
    print(f"📏 Alturas: Todas disponíveis ({client.ALTURAS_SUPORTADAS})")
    
    try:
        # Fazer requisição para todas as alturas de uma vez
        dados = client.obter_dados_ano_completo(
            latitude=cidade.latitude,
            longitude=cidade.longitude,
            ano=ano,
            alturas=None  # Todas as alturas
        )
        
        # Exibir metadados
        metadata = dados['metadata']
        print(f"\n📊 Metadados da requisição:")
        print(f"   🌐 Fonte: {metadata['fonte']}")
        print(f"   🕐 Timezone: {metadata['timezone']}")
        print(f"   📅 Período: {metadata['periodo_inicio']} a {metadata['periodo_fim']}")
        print(f"   📈 Total de registros: {metadata['total_registros']}")
        
        # Exibir dados por altura
        print(f"\n📏 Dados por altura:")
        for altura_key, dados_altura in dados['dados_por_altura'].items():
            altura = dados_altura['altura_metros']
            stats = dados_altura['estatisticas']
            
            print(f"\n   🏗️ Altura: {altura}m")
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
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro na requisição para {cidade.nome}: {e}")
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
    
    nome_arquivo = f"open_meteo_{nome_cidade.lower().replace(' ', '_')}_{ano}.json"
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Dados salvos em: {nome_arquivo}")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar arquivo: {e}")


def exemplo_requisicao_periodo_customizado():
    """Exemplo de requisição para período customizado"""
    print("\n🗓️ === EXEMPLO DE PERÍODO CUSTOMIZADO ===")
    
    client = OpenMeteoClient()
    
    # Exemplo: últimos 30 dias para uma coordenada específica
    data_fim = date.today() - timedelta(days=1)  # Ontem
    data_inicio = data_fim - timedelta(days=29)   # 30 dias atrás
    
    # Coordenadas de exemplo (Porto Alegre, RS)
    latitude = -30.0346
    longitude = -51.2177
    
    print(f"📍 Coordenadas de exemplo: {latitude}, {longitude}")
    print(f"📅 Período: {data_inicio} a {data_fim}")
    print(f"📏 Alturas: Apenas 10m e 80m")
    
    try:
        dados = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10, 80]  # Apenas duas alturas específicas
        )
        
        print(f"✅ Requisição bem-sucedida!")
        print(f"📊 Total de registros: {dados['metadata']['total_registros']}")
        
        for altura_key, dados_altura in dados['dados_por_altura'].items():
            stats = dados_altura['estatisticas']
            print(f"   {altura_key}: {stats['velocidade_media']:.2f} m/s (média)")
    
    except Exception as e:
        print(f"❌ Erro na requisição personalizada: {e}")


def testar_validacoes():
    """Testa as validações do cliente Open-Meteo"""
    print("\n🧪 === TESTANDO VALIDAÇÕES ===")
    
    client = OpenMeteoClient()
    
    # Teste 1: Altura não suportada
    print("1️⃣ Testando altura não suportada (25m):")
    try:
        client.validar_altura(25)
        print("   ❌ Deveria ter dado erro!")
    except ValueError as e:
        print(f"   ✅ Erro esperado: {e}")
    
    # Teste 2: Alturas válidas
    print("\n2️⃣ Testando alturas válidas:")
    for altura in [10, 80, 120, 180]:
        try:
            client.validar_altura(altura)
            print(f"   ✅ {altura}m: Válida")
        except ValueError as e:
            print(f"   ❌ {altura}m: {e}")
    
    # Teste 3: Coordenadas inválidas
    print("\n3️⃣ Testando coordenadas inválidas:")
    try:
        client.obter_dados_historicos_vento(
            latitude=100,  # Inválida
            longitude=200,  # Inválida
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 1, 2),
            alturas=[10]
        )
        print("   ❌ Deveria ter dado erro!")
    except ValueError as e:
        print(f"   ✅ Erro esperado: {e}")


def main():
    """Função principal do exemplo"""
    print("🌪️ === EXEMPLO DE USO DA API OPEN-METEO ===")
    print("Sistema de Simulação de Turbinas Eólicas")
    print("Demonstração de requisição de dados meteorológicos\n")
    
    try:
        # 1. Exibir informações da API
        exibir_informacoes_api()
        
        # 2. Buscar cidades do banco
        cidades = buscar_cidades_exemplo()
        
        if not cidades:
            print("⚠️ Sem cidades disponíveis. Executando exemplo com coordenadas fixas...")
            exemplo_requisicao_periodo_customizado()
            testar_validacoes()
            return
        
        # 3. Inicializar cliente
        client = OpenMeteoClient(timeout=60)  # Timeout maior para requisições longas
        
        # 4. Fazer requisições para as primeiras 3 cidades
        dados_coletados = []
        
        for i, cidade in enumerate(cidades[:3], 1):
            print(f"\n{'='*60}")
            print(f"🏙️ CIDADE {i}/3")
            
            dados = requisitar_dados_cidade(client, cidade, ano=2024)
            
            if dados:
                dados_coletados.append({
                    'cidade': cidade.nome,
                    'dados': dados
                })
                
                # Opcionalmente salvar em arquivo
                # salvar_dados_arquivo(dados, cidade.nome, 2024)
        
        # 5. Exemplo de período customizado
        exemplo_requisicao_periodo_customizado()
        
        # 6. Testar validações
        testar_validacoes()
        
        # 7. Resumo final
        print(f"\n🎯 === RESUMO FINAL ===")
        print(f"✅ Cidades processadas: {len(dados_coletados)}")
        print(f"📊 Total de conjuntos de dados: {len(dados_coletados) * len(client.ALTURAS_SUPORTADAS)}")
        print(f"🌍 API Open-Meteo funcionando corretamente!")
        
        if dados_coletados:
            print(f"\n📈 Estatísticas rápidas:")
            for item in dados_coletados:
                nome = item['cidade']
                dados = item['dados']
                
                # Velocidade média na altura de 50m (se disponível) ou 80m
                altura_ref = "80m" if "80m" in dados['dados_por_altura'] else "10m"
                vel_media = dados['dados_por_altura'][altura_ref]['estatisticas']['velocidade_media']
                
                print(f"   🏙️ {nome}: {vel_media:.2f} m/s (média em {altura_ref})")
        
        print("\n✅ === EXEMPLO CONCLUÍDO COM SUCESSO ===")
        print("🎉 API Open-Meteo integrada e funcionando!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
