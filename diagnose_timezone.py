"""
Script de Diagnóstico para Problemas de Timezone

Este script identifica onde estão os problemas de timezone misto nos dados.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def diagnosticar_timezone_problema():
    """Diagnostica problemas de timezone nos dados meteorológicos."""
    
    print("🔍 Diagnosticando problemas de timezone...")
    print("=" * 60)
    
    try:
        # Importar repositórios
        from meteorological.meteorological_data.repository import MeteorologicalDataRepository
        from meteorological.meteorological_data_source.repository import MeteorologicalDataSourceRepository
        
        # Buscar dados
        met_repo = MeteorologicalDataRepository()
        fonte_repo = MeteorologicalDataSourceRepository()
        
        # Buscar cidades com dados
        print("1️⃣ Verificando cidades com dados...")
        cidades_com_dados = met_repo.buscar_cidades_com_dados()
        print(f"   Cidades encontradas: {len(cidades_com_dados)}")
        
        if not cidades_com_dados:
            print("❌ Nenhuma cidade com dados encontrada.")
            return
        
        # Testar primeira cidade
        cidade_id = cidades_com_dados[0]
        print(f"2️⃣ Testando cidade ID: {cidade_id}")
        
        # Buscar dados da cidade
        dados_cidade = met_repo.buscar_por_cidade(cidade_id)
        print(f"   Registros encontrados: {len(dados_cidade)}")
        
        if not dados_cidade:
            print("❌ Nenhum dado encontrado para a cidade.")
            return
        
        # Analisar tipos de datetime
        print("3️⃣ Analisando tipos de datetime...")
        
        tipos_datetime = []
        for i, dado in enumerate(dados_cidade[:10]):  # Apenas primeiros 10 para teste
            dt = dado.data_hora
            if dt:
                tem_timezone = dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None
                tipos_datetime.append({
                    'index': i,
                    'datetime': dt,
                    'type': type(dt).__name__,
                    'has_timezone': tem_timezone,
                    'tzinfo': str(dt.tzinfo) if dt.tzinfo else 'None',
                    'timestamp': dt.timestamp() if hasattr(dt, 'timestamp') else 'N/A'
                })
                
                print(f"   [{i}] {dt} - TZ: {tem_timezone} - {dt.tzinfo}")
        
        # Tentar conversão para DataFrame
        print("4️⃣ Testando conversão para DataFrame...")
        
        try:
            # Simular código do 4_meteorological_analysis.py
            fontes = {f.id: f for f in fonte_repo.listar_todos()}
            
            df_data = []
            for dado in dados_cidade[:5]:  # Apenas primeiros 5 para teste
                df_data.append({
                    'id': dado.id,
                    'data_hora': dado.data_hora,
                    'fonte': fontes.get(dado.meteorological_data_source_id, {}).name if dado.meteorological_data_source_id in fontes else 'Desconhecida',
                    'altura_captura': dado.altura_captura,
                    'velocidade_vento': dado.velocidade_vento,
                })
            
            df = pd.DataFrame(df_data)
            print(f"   DataFrame criado com {len(df)} registros")
            
            # Tentar conversão original (que dá erro)
            print("5️⃣ Testando conversão original (pode dar erro)...")
            try:
                df['data_hora_original'] = pd.to_datetime(df['data_hora'])
                print("   ✅ Conversão original funcionou!")
            except Exception as e:
                print(f"   ❌ Erro na conversão original: {e}")
            
            # Tentar conversão com normalização UTC
            print("6️⃣ Testando conversão com normalização UTC...")
            try:
                df['data_hora_normalizada'] = pd.to_datetime(df['data_hora'], utc=True).dt.tz_localize(None)
                print("   ✅ Conversão normalizada funcionou!")
            except Exception as e:
                print(f"   ❌ Erro na conversão normalizada: {e}")
                
        except Exception as e:
            print(f"❌ Erro na criação do DataFrame: {e}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar_timezone_problema()
