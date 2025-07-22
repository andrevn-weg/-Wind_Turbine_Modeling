"""
Script de migração para alterar o campo 'data' para 'data_hora' (TIMESTAMP)

Este script migra a tabela meteorological_data para usar TIMESTAMP em vez de DATE
no campo de data/hora das medições meteorológicas.

Procedimento para SQLite:
1. Criar nova tabela com estrutura atualizada
2. Migrar dados existentes (convertendo DATE para TIMESTAMP)
3. Remover tabela antiga
4. Renomear nova tabela
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def executar_migracao(db_path: str = "data/wind_turbine.db"):
    """
    Executa a migração do campo data (DATE) para data_hora (TIMESTAMP)
    
    Args:
        db_path: Caminho para o banco de dados
    """
    
    # Verificar se o banco existe
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    # Fazer backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível criar backup: {e}")
    
    conn = None
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migração...")
        
        # 1. Verificar se a tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='meteorological_data'
        """)
        
        if not cursor.fetchone():
            print("ℹ️ Tabela meteorological_data não existe. Nada a migrar.")
            return True
        
        # 2. Verificar se já foi migrada (campo data_hora existe)
        cursor.execute("PRAGMA table_info(meteorological_data)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'data_hora' in colunas:
            print("ℹ️ Migração já foi executada anteriormente.")
            return True
        
        # 3. Criar nova tabela com estrutura atualizada
        print("📝 Criando nova tabela com estrutura atualizada...")
        cursor.execute('''
            CREATE TABLE meteorological_data_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meteorological_data_source_id INTEGER NOT NULL,
                cidade_id INTEGER NOT NULL,
                data_hora TIMESTAMP NOT NULL,
                altura_captura REAL,
                velocidade_vento REAL,
                temperatura REAL,
                umidade REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meteorological_data_source_id) REFERENCES meteorological_data_source (id),
                FOREIGN KEY (cidade_id) REFERENCES cidades (id)
            )
        ''')
        
        # 4. Migrar dados existentes
        print("📦 Migrando dados existentes...")
        cursor.execute("SELECT COUNT(*) FROM meteorological_data")
        total_registros = cursor.fetchone()[0]
        
        if total_registros > 0:
            # Migrar dados convertendo DATE para TIMESTAMP (assumindo meio-dia como hora padrão)
            cursor.execute('''
                INSERT INTO meteorological_data_new 
                (id, meteorological_data_source_id, cidade_id, data_hora, 
                 altura_captura, velocidade_vento, temperatura, umidade, created_at)
                SELECT 
                    id, 
                    meteorological_data_source_id, 
                    cidade_id, 
                    CASE 
                        WHEN data IS NOT NULL THEN datetime(data || ' 12:00:00')
                        ELSE NULL 
                    END as data_hora,
                    altura_captura, 
                    velocidade_vento, 
                    temperatura, 
                    umidade, 
                    created_at
                FROM meteorological_data
            ''')
            
            registros_migrados = cursor.rowcount
            print(f"✅ {registros_migrados} registros migrados")
        else:
            print("ℹ️ Nenhum registro para migrar")
        
        # 5. Remover tabela antiga
        print("🗑️ Removendo tabela antiga...")
        cursor.execute("DROP TABLE meteorological_data")
        
        # 6. Renomear nova tabela
        print("🔄 Renomeando nova tabela...")
        cursor.execute("ALTER TABLE meteorological_data_new RENAME TO meteorological_data")
        
        # 7. Commit das alterações
        conn.commit()
        
        print("🎉 Migração concluída com sucesso!")
        print(f"📊 Total de registros migrados: {total_registros}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

def verificar_migracao(db_path: str = "data/wind_turbine.db"):
    """
    Verifica se a migração foi executada corretamente
    
    Args:
        db_path: Caminho para o banco de dados
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(meteorological_data)")
        colunas = cursor.fetchall()
        
        print("\n📋 Estrutura atual da tabela meteorological_data:")
        for col in colunas:
            nome_coluna = col[1]
            tipo_coluna = col[2]
            print(f"  • {nome_coluna}: {tipo_coluna}")
        
        # Verificar se campo data_hora existe
        colunas_nomes = [col[1] for col in colunas]
        if 'data_hora' in colunas_nomes:
            print("✅ Campo 'data_hora' encontrado")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM meteorological_data")
            total = cursor.fetchone()[0]
            print(f"📊 Total de registros: {total}")
            
            if total > 0:
                # Mostrar exemplo de registro
                cursor.execute("SELECT id, data_hora, velocidade_vento, altura_captura FROM meteorological_data LIMIT 1")
                registro = cursor.fetchone()
                if registro:
                    print(f"📝 Exemplo de registro: ID={registro[0]}, Data/Hora={registro[1]}, Vento={registro[2]}m/s, Altura={registro[3]}m")
        else:
            print("❌ Campo 'data_hora' não encontrado")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando migração do campo data para data_hora...")
    
    # Executar migração
    if executar_migracao():
        print("\n🔍 Verificando resultado da migração...")
        verificar_migracao()
    else:
        print("❌ Migração falhou")
