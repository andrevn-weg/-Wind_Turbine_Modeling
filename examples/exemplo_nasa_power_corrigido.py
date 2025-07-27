"""
Exemplo de uso da NASA POWER API corrigida

Este exemplo mostra como usar corretamente a API NASA POWER
para obter dados meteorológicos completos (vento, temperatura e umidade).

CORREÇÕES APLICADAS:
- Corrigido metadata para retornar booleans corretos
- Corrigido processamento de dados para incluir temperatura e umidade
- Removido código duplicado que causava problemas
- Melhorada validação de parâmetros
"""

import sys
import os
from datetime import date, timedelta

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.nasa_power import NASAPowerClient


def exemplo_basico():
    """Exemplo básico de uso da NASA POWER API."""
    print("EXEMPLO DE USO - NASA POWER API")
    print("=" * 50)
    
    # Inicializar cliente
    client = NASAPowerClient()
    
    # Configurar parâmetros
    latitude = -29.6842  # Santa Maria, RS
    longitude = -53.8069
    data_inicio = date(2024, 7, 1)
    data_fim = date(2024, 7, 7)  # Uma semana
    
    print(f"Local: Santa Maria, RS ({latitude}, {longitude})")
    print(f"Período: {data_inicio} a {data_fim}")
    print(f"Alturas: 10m e 50m")
    print("Incluindo: Velocidade do vento, Temperatura e Umidade")
    print()
    
    try:
        # Obter dados completos
        resultado = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10, 50],  # Alturas suportadas pela NASA POWER
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        # Mostrar informações do resultado
        print("RESULTADO OBTIDO:")
        print(f"✓ Total de registros: {len(resultado['dados'])}")
        print(f"✓ Período coberto: {resultado['metadata']['periodo_inicio']} até {resultado['metadata']['periodo_fim']}")
        print(f"✓ Fonte: {resultado['metadata']['fonte']}")
        print()
        
        # Mostrar dados incluídos
        dados_incluidos = resultado['metadata']['dados_incluidos']
        print("DADOS INCLUÍDOS:")
        print(f"✓ Velocidade do vento: {dados_incluidos['velocidade_vento']}")
        print(f"✓ Temperatura: {dados_incluidos['temperatura']}")
        print(f"✓ Umidade: {dados_incluidos['umidade']}")
        print()
        
        # Mostrar estatísticas por altura
        print("ESTATÍSTICAS POR ALTURA:")
        for altura_str, dados_altura in resultado['dados_por_altura'].items():
            stats = dados_altura['estatisticas']
            print(f"  {altura_str}:")
            print(f"    Registros: {stats['total_registros']}")
            print(f"    Velocidade média: {stats['velocidade_media']:.2f} m/s")
            print(f"    Velocidade máxima: {stats['velocidade_maxima']:.2f} m/s")
        print()
        
        # Calcular estatísticas de temperatura e umidade
        temperaturas = [r['temperatura'] for r in resultado['dados'] if r['temperatura'] is not None]
        umidades = [r['umidade'] for r in resultado['dados'] if r['umidade'] is not None]
        
        if temperaturas:
            temp_media = sum(temperaturas) / len(temperaturas)
            temp_max = max(temperaturas)
            temp_min = min(temperaturas)
            print("ESTATÍSTICAS DE TEMPERATURA:")
            print(f"  Média: {temp_media:.1f}°C")
            print(f"  Máxima: {temp_max:.1f}°C")
            print(f"  Mínima: {temp_min:.1f}°C")
        
        if umidades:
            umid_media = sum(umidades) / len(umidades)
            umid_max = max(umidades)
            umid_min = min(umidades)
            print("ESTATÍSTICAS DE UMIDADE:")
            print(f"  Média: {umid_media:.1f}%")
            print(f"  Máxima: {umid_max:.1f}%")
            print(f"  Mínima: {umid_min:.1f}%")
        print()
        
        # Mostrar alguns registros de exemplo
        print("REGISTROS DE EXEMPLO (primeiros 5):")
        for i, registro in enumerate(resultado['dados'][:5]):
            print(f"  {i+1}: {registro['data_hora']} | "
                  f"Alt: {registro['altura_captura']}m | "
                  f"Vel: {registro['velocidade_vento']:.2f}m/s | "
                  f"Temp: {registro['temperatura']:.1f}°C | "
                  f"Umid: {registro['umidade']:.1f}%")
        
        print("\n✅ EXEMPLO EXECUTADO COM SUCESSO!")
        
        # Mostrar como usar os dados
        print("\nCOMO USAR OS DADOS:")
        print("1. resultado['dados'] contém todos os registros individuais")
        print("2. resultado['dados_por_altura'] contém dados organizados por altura")
        print("3. resultado['metadata'] contém informações sobre os dados")
        print("4. Cada registro tem: data_hora, velocidade_vento, temperatura, umidade, altura_captura")
        
        return resultado
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None


def exemplo_somente_vento():
    """Exemplo obtendo apenas dados de vento (sem temperatura/umidade)."""
    print("\n" + "=" * 50)
    print("EXEMPLO SOMENTE VENTO")
    print("=" * 50)
    
    client = NASAPowerClient()
    
    try:
        resultado = client.obter_dados_historicos_vento(
            latitude=-23.5505,  # São Paulo
            longitude=-46.6333,
            data_inicio=date(2024, 5, 1),
            data_fim=date(2024, 5, 2),
            alturas=[10, 50],
            incluir_temperatura=False,  # Não incluir temperatura
            incluir_umidade=False       # Não incluir umidade
        )
        
        print(f"✓ Registros obtidos: {len(resultado['dados'])}")
        print(f"✓ Temperatura incluída: {resultado['metadata']['dados_incluidos']['temperatura']}")
        print(f"✓ Umidade incluída: {resultado['metadata']['dados_incluidos']['umidade']}")
        
        # Verificar se realmente não há dados de temp/umidade
        tem_temp = any(r['temperatura'] is not None for r in resultado['dados'])
        tem_umid = any(r['umidade'] is not None for r in resultado['dados'])
        
        print(f"✓ Dados têm temperatura: {tem_temp}")
        print(f"✓ Dados têm umidade: {tem_umid}")
        
        print("\n✅ EXEMPLO SOMENTE VENTO EXECUTADO!")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")


def exemplo_validacao_alturas():
    """Exemplo mostrando validação de alturas."""
    print("\n" + "=" * 50)
    print("EXEMPLO VALIDAÇÃO DE ALTURAS")
    print("=" * 50)
    
    client = NASAPowerClient()
    
    # Alturas válidas
    print("ALTURAS VÁLIDAS:")
    alturas_validas = client.ALTURAS_SUPORTADAS
    print(f"  NASA POWER suporta apenas: {alturas_validas}")
    
    # Testar altura inválida
    print("\nTESTANDO ALTURA INVÁLIDA:")
    try:
        resultado = client.obter_dados_historicos_vento(
            latitude=0,
            longitude=0,
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 1, 1),
            alturas=[100]  # Altura não suportada
        )
        print("❌ Não deveria ter funcionado!")
    except ValueError as e:
        print(f"✅ Erro esperado: {e}")


def main():
    print("EXEMPLOS DE USO - NASA POWER API CORRIGIDA")
    print(f"Data: {date.today()}")
    print()
    
    # Executar exemplos
    exemplo_basico()
    exemplo_somente_vento()
    exemplo_validacao_alturas()
    
    print("\n" + "=" * 50)
    print("TODOS OS EXEMPLOS CONCLUÍDOS")
    print("=" * 50)
    print("\nRESUMO DAS CORREÇÕES APLICADAS:")
    print("1. ✅ Metadata agora retorna booleans corretos")
    print("2. ✅ Temperatura e umidade são processadas corretamente")
    print("3. ✅ Código duplicado foi removido")
    print("4. ✅ Validação de parâmetros melhorada")
    print("5. ✅ Tratamento de erros robusto")
    
    print("\nA NASA POWER API está pronta para uso na interface!")


if __name__ == "__main__":
    main()
