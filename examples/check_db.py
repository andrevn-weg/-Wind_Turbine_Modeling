import sqlite3

# Conecta ao banco de dados
conn = sqlite3.connect('data/wind_turbine.db')
cursor = conn.cursor()

# Lista todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=== TABELAS DO BANCO DE DADOS ===")
for table in tables:
    print(f"- {table[0]}")

print("\n=== ESTRUTURA DAS TABELAS ===")
for table in tables:
    table_name = table[0]
    print(f"\n📋 Tabela: {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")

conn.close()
