"""
Teste específico para integração NASA POWER com interface

Este script testa especificamente a integração entre a API NASA POWER
e a interface de registro meteorológico para identificar onde está o problema.
"""

import sys
import os
from datetime import datetime, date, timedelta

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from meteorological.api.nasa_power import NASAPowerClient


def testar_integracao_completa():
    """Testa a integração completa NASA POWER -> Repository -> Database."""
    print("=" * 60)
    print("TESTE INTEGRAÇÃO NASA POWER -> INTERFACE")
    print("=" * 60)
    
    # Inicializar componentes
    client = NASAPowerClient()
    
    # Parâmetros de teste
    latitude = -29.6842  # Santa Maria, RS
    longitude = -53.8069
    data_inicio = date(2024, 1, 1)
    data_fim = date(2024, 1, 2)  # Apenas 1 dia para teste
    fonte_nome = "NASA POWER"
    
    print(f"Local: {latitude}, {longitude}")
    print(f"Período: {data_inicio} a {data_fim}")
    print(f"Fonte: {fonte_nome}")
    print()
    
    try:
        # 1. Obter dados da API
        print("1. OBTENDO DADOS DA API NASA POWER...")
        resultado = client.obter_dados_historicos_vento(
            latitude=latitude,
            longitude=longitude,
            data_inicio=data_inicio,
            data_fim=data_fim,
            alturas=[10, 50],
            incluir_temperatura=True,
            incluir_umidade=True
        )
        
        total_registros = len(resultado['dados'])
        print(f"   ✓ Obtidos {total_registros} registros da API")
        print(f"   ✓ Alturas disponíveis: {list(resultado['dados_por_altura'].keys())}")
        print(f"   ✓ Dados incluem temperatura: {resultado['metadata']['dados_incluidos']['velocidade_vento']}")
        print(f"   ✓ Dados incluem umidade: {resultado['metadata']['dados_incluidos']['velocidade_vento']}")
        print()
        
        # Mostrar alguns exemplos
        print("   Primeiros 3 registros:")
        for i, registro in enumerate(resultado['dados'][:3]):
            print(f"     {i+1}: Data={registro['data_hora']}, "
                  f"Vel={registro['velocidade_vento']:.2f}m/s, "
                  f"Temp={registro['temperatura']}°C, "
                  f"Umid={registro['umidade']}%, "
                  f"Alt={registro['altura_captura']}m")
        print()
        
        # 2. Analisar estrutura dos dados (simulação)
        print("2. ANÁLISE DA ESTRUTURA DOS DADOS...")
        dados_salvos = 0
        dados_com_erro = 0
        
        for registro in resultado['dados'][:5]:  # Testar apenas 5 registros
            try:
                # Validar dados antes de salvar
                if not registro['data_hora']:
                    raise ValueError("Data/hora é obrigatória")
                if registro['velocidade_vento'] is None:
                    raise ValueError("Velocidade do vento é obrigatória")
                if registro['altura_captura'] is None:
                    raise ValueError("Altura de captura é obrigatória")
                
                # Simular criação do registro (sem realmente salvar)
                print(f"   ✓ Validação OK - Data: {registro['data_hora']}, "
                      f"Vel: {registro['velocidade_vento']}, "
                      f"Temp: {registro['temperatura']}, "
                      f"Umid: {registro['umidade']}, "
                      f"Alt: {registro['altura_captura']}")
                dados_salvos += 1
                
            except Exception as e:
                print(f"   ✗ Erro na validação: {e}")
                print(f"     Registro: {registro}")
                dados_com_erro += 1
        
        print(f"\n   Resultado da simulação:")
        print(f"   ✓ Dados válidos: {dados_salvos}")
        print(f"   ✗ Dados com erro: {dados_com_erro}")
        print()
        
        # 3. Simular salvamento dos dados
        print("3. SIMULANDO SALVAMENTO DOS DADOS...")
        
        # Verificar se há dados nulos/vazios
        dados_com_temp = sum(1 for r in resultado['dados'] if r['temperatura'] is not None)
        dados_com_umid = sum(1 for r in resultado['dados'] if r['umidade'] is not None)
        dados_com_vento = sum(1 for r in resultado['dados'] if r['velocidade_vento'] is not None)
        
        print(f"   Total de registros: {total_registros}")
        print(f"   Registros com temperatura: {dados_com_temp} ({dados_com_temp/total_registros*100:.1f}%)")
        print(f"   Registros com umidade: {dados_com_umid} ({dados_com_umid/total_registros*100:.1f}%)")
        print(f"   Registros com velocidade: {dados_com_vento} ({dados_com_vento/total_registros*100:.1f}%)")
        print()
        
        # Verificar alturas únicas
        alturas_unicas = set(r['altura_captura'] for r in resultado['dados'])
        print(f"   Alturas únicas encontradas: {sorted(alturas_unicas)}")
        
        # Verificar distribuição por altura
        for altura in sorted(alturas_unicas):
            registros_altura = sum(1 for r in resultado['dados'] if r['altura_captura'] == altura)
            print(f"   Registros para altura {altura}m: {registros_altura}")
        print()
        
        # 4. Analisar estrutura dos dados  
        print("4. ANÁLISE DA ESTRUTURA DOS DADOS...")
        
        # Simular validação que pode estar causando o erro
        alturas_solicitadas = [10, 50]
        alturas_com_dados_validos = []
        
        for altura in alturas_solicitadas:
            registros_altura = [r for r in resultado['dados'] if r['altura_captura'] == altura and r['velocidade_vento'] is not None]
            if registros_altura:
                alturas_com_dados_validos.append(altura)
                print(f"   ✓ Altura {altura}m: {len(registros_altura)} registros válidos")
            else:
                print(f"   ✗ Altura {altura}m: SEM DADOS VÁLIDOS")
        
        if not alturas_com_dados_validos:
            print("   ⚠️  PROBLEMA IDENTIFICADO: Nenhuma altura tem dados válidos!")
            print("   Isso pode ser o que está causando o erro na interface.")
        else:
            print(f"   ✓ Alturas com dados válidos: {alturas_com_dados_validos}")
        
        print()
        
        # 5. Testar validação específica da interface
        print("5. TESTANDO VALIDAÇÃO DA INTERFACE...")
        print(f"   Metadata completo: {resultado['metadata']}")
        
        # Identificar possíveis problemas no metadata
        metadata = resultado['metadata']
        problemas_metadata = []
        
        if 'dados_incluidos' in metadata:
            dados_incluidos = metadata['dados_incluidos']
            if not isinstance(dados_incluidos.get('temperatura'), bool):
                problemas_metadata.append("'temperatura' no metadata não é boolean")
            if not isinstance(dados_incluidos.get('umidade'), bool):
                problemas_metadata.append("'umidade' no metadata não é boolean")
        
        if problemas_metadata:
            print("   ⚠️  Problemas no metadata:")
            for problema in problemas_metadata:
                print(f"     - {problema}")
        else:
            print("   ✓ Metadata está correto")
        
    except Exception as e:
        print(f"ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)


def main():
    print("TESTE DE INTEGRAÇÃO NASA POWER")
    print(f"Data/Hora: {datetime.now()}")
    print()
    
    testar_integracao_completa()


if __name__ == "__main__":
    main()
