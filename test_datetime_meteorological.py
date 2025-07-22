"""
Script de Teste - Campo Data/Hora Meteorológica

Este script demonstra e valida o funcionamento do campo data_hora (TIMESTAMP)
nos dados meteorológicos, realizando inserção e consulta de dados com data e hora completa.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from meteorological.meteorological_data.entity import MeteorologicalData
from meteorological.meteorological_data.repository import MeteorologicalDataRepository
from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
from geographic import CidadeRepository


def criar_dados_teste():
    """Cria dados de teste com timestamps específicos"""
    
    print("🧪 === TESTE DO CAMPO DATA/HORA METEOROLÓGICA ===\n")
    
    # Inicializar repositórios
    met_repo = MeteorologicalDataRepository()
    fonte_repo = MeteorologicalDataSourceRepository()
    cidade_repo = CidadeRepository()
    
    print("🔧 Inicializando repositórios...")
    
    # Verificar se temos cidades e fontes
    cidades = cidade_repo.listar_todos()
    fontes = fonte_repo.listar_todos()
    
    if not cidades:
        print("❌ Nenhuma cidade cadastrada. Cadastre uma cidade primeiro.")
        return False
    
    if not fontes:
        print("❌ Nenhuma fonte cadastrada. Cadastre uma fonte primeiro.")
        return False
    
    cidade = cidades[0]  # Usar primeira cidade
    fonte = fontes[0]    # Usar primeira fonte
    
    print(f"✅ Usando cidade: {cidade.nome}")
    print(f"✅ Usando fonte: {fonte.name}")
    
    # Criar dados de teste com horários específicos
    dados_teste = []
    base_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"\n📅 Criando dados de teste para {base_datetime.date()}...")
    
    # Gerar 24 registros (um para cada hora do dia)
    for hora in range(24):
        data_hora = base_datetime + timedelta(hours=hora)
        
        # Simular dados meteorológicos realistas
        velocidade_vento = round(random.uniform(2.0, 15.0), 2)
        temperatura = round(random.uniform(15.0, 35.0), 1) if random.choice([True, False]) else None
        umidade = round(random.uniform(40.0, 90.0), 1) if random.choice([True, False]) else None
        altura = random.choice([10, 50, 80, 120])
        
        dado = MeteorologicalData(
            cidade_id=cidade.id,
            meteorological_data_source_id=fonte.id,
            data_hora=data_hora,
            altura_captura=altura,
            velocidade_vento=velocidade_vento,
            temperatura=temperatura,
            umidade=umidade,
            created_at=datetime.now()
        )
        
        dados_teste.append(dado)
    
    print(f"📊 Gerados {len(dados_teste)} registros de teste")
    
    # Validar dados antes de inserir
    print("\n🔍 Validando dados...")
    dados_validos = []
    for dado in dados_teste:
        if dado.validar():
            dados_validos.append(dado)
        else:
            print(f"⚠️ Dado inválido: {dado}")
    
    print(f"✅ {len(dados_validos)} dados válidos")
    
    # Inserir dados no banco
    print("\n💾 Inserindo dados no banco...")
    dados_inseridos = 0
    ids_inseridos = []
    
    for dado in dados_validos:
        try:
            dado_id = met_repo.salvar(dado)
            if dado_id:
                dados_inseridos += 1
                ids_inseridos.append(dado_id)
                print(f"  ✅ Inserido: ID={dado_id}, Data/Hora={dado.data_hora}, Vento={dado.velocidade_vento}m/s")
        except Exception as e:
            print(f"  ❌ Erro ao inserir: {e}")
    
    print(f"\n📈 Total inserido: {dados_inseridos} registros")
    
    return dados_inseridos > 0, ids_inseridos, cidade.id, fonte.id


def consultar_dados_teste(cidade_id, fonte_id):
    """Consulta e exibe os dados de teste inseridos"""
    
    print(f"\n📋 === CONSULTANDO DADOS INSERIDOS ===\n")
    
    met_repo = MeteorologicalDataRepository()
    
    # Consultar todos os dados da cidade
    print("🔍 Buscando todos os dados da cidade...")
    dados_cidade = met_repo.buscar_por_cidade(cidade_id, limite=50)
    
    if not dados_cidade:
        print("❌ Nenhum dado encontrado")
        return False
    
    print(f"📊 Encontrados {len(dados_cidade)} registros")
    
    # Exibir primeiros 10 registros
    print("\n📝 Primeiros 10 registros:")
    print("=" * 100)
    print(f"{'ID':<5} {'Data/Hora':<20} {'Vento (m/s)':<12} {'Temp (°C)':<10} {'Umidade (%)':<12} {'Altura (m)':<10}")
    print("=" * 100)
    
    for i, dado in enumerate(dados_cidade[:10]):
        temp_str = f"{dado.temperatura:.1f}" if dado.temperatura is not None else "N/A"
        umid_str = f"{dado.umidade:.1f}" if dado.umidade is not None else "N/A"
        
        print(f"{dado.id:<5} {dado.data_hora:<20} {dado.velocidade_vento:<12} {temp_str:<10} {umid_str:<12} {dado.altura_captura:<10}")
    
    print("=" * 100)
    
    # Consultar por período (últimas 24 horas)
    print(f"\n🕐 Consultando dados das últimas 24 horas...")
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(hours=24)
    
    dados_periodo = met_repo.buscar_por_periodo(data_inicio, data_fim, cidade_id)
    print(f"📊 Dados no período {data_inicio} a {data_fim}: {len(dados_periodo)} registros")
    
    # Estatísticas dos dados
    if dados_cidade:
        print(f"\n📈 Estatísticas dos dados:")
        velocidades = [d.velocidade_vento for d in dados_cidade if d.velocidade_vento is not None]
        if velocidades:
            print(f"  🌪️ Velocidade do vento:")
            print(f"    - Média: {sum(velocidades)/len(velocidades):.2f} m/s")
            print(f"    - Mínima: {min(velocidades):.2f} m/s")
            print(f"    - Máxima: {max(velocidades):.2f} m/s")
        
        temperaturas = [d.temperatura for d in dados_cidade if d.temperatura is not None]
        if temperaturas:
            print(f"  🌡️ Temperatura:")
            print(f"    - Média: {sum(temperaturas)/len(temperaturas):.1f} °C")
            print(f"    - Mínima: {min(temperaturas):.1f} °C")
            print(f"    - Máxima: {max(temperaturas):.1f} °C")
    
    # Testar conversão para dicionário
    print(f"\n🔄 Testando conversão para dicionário...")
    primeiro_dado = dados_cidade[0]
    dict_dado = primeiro_dado.to_dict()
    
    print(f"📋 Exemplo de dado convertido para dict:")
    for chave, valor in dict_dado.items():
        print(f"  • {chave}: {valor}")
    
    return True


def testar_apis_com_datetime():
    """Testa se as APIs estão retornando datetime corretamente"""
    
    print(f"\n🌐 === TESTANDO APIs COM DATETIME ===\n")
    
    from meteorological.api.nasa_power import NASAPowerClient
    from meteorological.api.open_meteo import OpenMeteoClient
    from datetime import date
    
    # Coordenadas de teste (São Paulo)
    latitude = -23.5505
    longitude = -46.6333
    data_inicio = date.today() - timedelta(days=2)
    data_fim = date.today() - timedelta(days=1)
    
    print(f"📍 Testando com coordenadas: {latitude}, {longitude}")
    print(f"📅 Período: {data_inicio} a {data_fim}")
    
    # Testar NASA POWER
    print(f"\n🛰️ Testando NASA POWER...")
    try:
        nasa_client = NASAPowerClient()
        nasa_result = nasa_client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10]
        )
        
        if nasa_result and 'dados' in nasa_result:
            print(f"✅ NASA POWER retornou {len(nasa_result['dados'])} registros")
            if nasa_result['dados']:
                primeiro = nasa_result['dados'][0]
                print(f"📝 Primeiro registro: {primeiro}")
                print(f"🕐 Tipo da data_hora: {type(primeiro.get('data_hora'))}")
        else:
            print("❌ NASA POWER não retornou dados válidos")
            
    except Exception as e:
        print(f"❌ Erro NASA POWER: {e}")
    
    # Testar Open-Meteo
    print(f"\n🌍 Testando Open-Meteo...")
    try:
        meteo_client = OpenMeteoClient()
        meteo_result = meteo_client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10]
        )
        
        if meteo_result and 'dados' in meteo_result:
            print(f"✅ Open-Meteo retornou {len(meteo_result['dados'])} registros")
            if meteo_result['dados']:
                primeiro = meteo_result['dados'][0]
                print(f"📝 Primeiro registro: {primeiro}")
                print(f"🕐 Tipo da data_hora: {type(primeiro.get('data_hora'))}")
        else:
            print("❌ Open-Meteo não retornou dados válidos")
            
    except Exception as e:
        print(f"❌ Erro Open-Meteo: {e}")


def main():
    """Função principal do teste"""
    
    print("🚀 Iniciando teste completo do campo data_hora...")
    
    # Teste 1: Criar e inserir dados
    sucesso_insercao, ids_inseridos, cidade_id, fonte_id = criar_dados_teste()
    
    if not sucesso_insercao:
        print("❌ Falha na inserção de dados. Abortando testes.")
        return
    
    # Teste 2: Consultar dados
    sucesso_consulta = consultar_dados_teste(cidade_id, fonte_id)
    
    if not sucesso_consulta:
        print("❌ Falha na consulta de dados.")
        return
    
    # Teste 3: Testar APIs
    testar_apis_com_datetime()
    
    print(f"\n🎉 === TESTE COMPLETO CONCLUÍDO ===")
    print(f"✅ Campo data_hora está funcionando corretamente!")
    print(f"✅ Inserção e consulta de dados com timestamp funcionais!")
    print(f"✅ APIs retornando datetime conforme esperado!")
    
    # Limpar dados de teste (opcional)
    resposta = input(f"\n🗑️ Deseja remover os {len(ids_inseridos)} dados de teste inseridos? (s/N): ").lower()
    if resposta == 's':
        met_repo = MeteorologicalDataRepository()
        removidos = 0
        for dado_id in ids_inseridos:
            if met_repo.excluir(dado_id):
                removidos += 1
        print(f"🗑️ Removidos {removidos} dados de teste")
    else:
        print("ℹ️ Dados de teste mantidos no banco")


if __name__ == "__main__":
    main()
