import sqlite3

conn = sqlite3.connect("mercado_educacional_local.db")
cursor = conn.cursor()

# Executa o comando que traz os metadados da tabela
cursor.execute("PRAGMA table_info(escolas_privadas_potenciais);")
colunas = cursor.fetchall()

print("\n--- COLUNAS ENCONTRADAS NA TABELA ---")
for col in colunas:
    # col[1] é o nome da coluna
    print(f"- {col[1]}")

conn.close()