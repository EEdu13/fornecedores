#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import traceback

# SQL Server Azure Configuration
SQL_CONFIG = {
    'server': 'alrflorestal.database.windows.net',
    'database': 'Tabela_teste',
    'username': 'sqladmin',
    'password': 'SenhaForte123!',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def test_sql_connection():
    """Test SQL Server Azure connection"""
    try:
        print("Tentando conectar ao SQL Server Azure...")
        print(f"Servidor: {SQL_CONFIG['server']}")
        print(f"Database: {SQL_CONFIG['database']}")
        print(f"Usuário: {SQL_CONFIG['username']}")
        
        # Try different connection string formats
        connection_strings = [
            # Format 1: Standard Azure SQL
            (
                f"Driver={SQL_CONFIG['driver']};"
                f"Server=tcp:{SQL_CONFIG['server']},1433;"
                f"Database={SQL_CONFIG['database']};"
                f"Uid={SQL_CONFIG['username']};"
                f"Pwd={SQL_CONFIG['password']};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
            ),
            # Format 2: Alternative format
            (
                f"DRIVER={SQL_CONFIG['driver']};"
                f"SERVER={SQL_CONFIG['server']};"
                f"DATABASE={SQL_CONFIG['database']};"
                f"UID={SQL_CONFIG['username']};"
                f"PWD={SQL_CONFIG['password']};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            ),
            # Format 3: SQL Server driver
            (
                f"Driver={{SQL Server}};"
                f"Server={SQL_CONFIG['server']};"
                f"Database={SQL_CONFIG['database']};"
                f"Uid={SQL_CONFIG['username']};"
                f"Pwd={SQL_CONFIG['password']};"
            )
        ]
        
        for i, connection_string in enumerate(connection_strings, 1):
            try:
                print(f"\nTentativa {i}:")
                print(f"Connection string: {connection_string.replace(SQL_CONFIG['password'], '***')}")
                conn = pyodbc.connect(connection_string)
                print(f"✅ Conexão {i} bem-sucedida!")
                break
            except Exception as e:
                print(f"❌ Tentativa {i} falhou: {str(e)[:100]}...")
                if i == len(connection_strings):
                    raise e
                continue
        
        print("✅ Conexão estabelecida com sucesso!")
        
        cursor = conn.cursor()
        
        # Test basic query
        print("\nTestando consulta básica...")
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"Teste básico: {result[0]}")
        
        # Test table exists
        print("\nVerificando se a tabela tb_fornecedores existe...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'tb_fornecedores'
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ Tabela tb_fornecedores encontrada!")
            
            # Get table structure
            print("\nEstrutura da tabela:")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'tb_fornecedores'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Test data query
            print("\nTestando consulta de dados...")
            cursor.execute("""
                SELECT TOP 3 FORNECEDOR, CPF_CNPJ, VALOR, TIPO_FORN, PROJETO, LOCAL
                FROM tb_fornecedores
                ORDER BY FORNECEDOR
            """)
            rows = cursor.fetchall()
            
            print(f"✅ Encontrados {len(rows)} registros (primeiros 3):")
            for i, row in enumerate(rows):
                print(f"  {i+1}. {row[0]} - Valor: R$ {row[2]} - Tipo: {row[3]}")
        else:
            print("❌ Tabela tb_fornecedores não encontrada!")
            
            # List available tables
            print("\nTabelas disponíveis:")
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            for table in tables:
                print(f"  - {table[0]}")
        
        conn.close()
        print("\n✅ Teste de conexão concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\nDetalhes do erro:")
        print(traceback.format_exc())
        
        # Check for common issues
        if "Login failed" in str(e):
            print("\n💡 Possíveis soluções:")
            print("1. Verificar se o usuário e senha estão corretos")
            print("2. Verificar se o usuário tem permissão para acessar o banco")
            print("3. Verificar se o firewall do Azure permite conexões")
        elif "Cannot open server" in str(e):
            print("\n💡 Possíveis soluções:")
            print("1. Verificar se o nome do servidor está correto")
            print("2. Verificar conectividade de rede")
            print("3. Verificar se o servidor Azure SQL está ativo")
        elif "driver" in str(e).lower():
            print("\n💡 Possível solução:")
            print("1. Instalar o ODBC Driver 17 for SQL Server")
            print("2. Ou tentar '{SQL Server}' como driver alternativo")

if __name__ == "__main__":
    test_sql_connection()