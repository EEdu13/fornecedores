#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import traceback
from datetime import datetime

# PostgreSQL Railway Configuration
PG_CONFIG = {
    'host': 'ballast.proxy.rlwy.net',
    'port': 21526,
    'user': 'postgres',
    'password': 'CqdPHkjnPksiOYxCKVZtFUUOIGDIlPNr',
    'database': 'railway'
}

def test_postgresql_connection():
    """Test PostgreSQL Railway connection"""
    try:
        print("🐘 Tentando conectar ao PostgreSQL Railway...")
        print(f"Host: {PG_CONFIG['host']}")
        print(f"Database: {PG_CONFIG['database']}")
        print(f"User: {PG_CONFIG['user']}")
        
        # Create connection
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
            database=PG_CONFIG['database']
        )
        
        print("✅ Conexão estabelecida com sucesso!")
        
        cursor = conn.cursor()
        
        # Test basic query
        print("\nTestando consulta básica...")
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        # Check if table exists
        print("\nVerificando se a tabela de refeições existe...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'fornecedores'
                AND table_name = 'refeicoes'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ Tabela 'fornecedores.refeicoes' encontrada!")
            
            # Get table structure
            print("\nEstrutura da tabela:")
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale
                FROM information_schema.columns 
                WHERE table_schema = 'fornecedores'
                AND table_name = 'refeicoes'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Test data query
            print("\nTestando consulta de dados...")
            cursor.execute("SELECT COUNT(*) FROM fornecedores.refeicoes;")
            count = cursor.fetchone()[0]
            print(f"Total de registros: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM fornecedores.refeicoes LIMIT 3;")
                rows = cursor.fetchall()
                print("\nPrimeiros registros:")
                for i, row in enumerate(rows):
                    print(f"  {i+1}. {row}")
        else:
            print("❌ Tabela 'fornecedores.refeicoes' não encontrada!")
            print("\n🔧 Verificando se o schema 'fornecedores' existe...")
            
            # Check if schema exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.schemata 
                    WHERE schema_name = 'fornecedores'
                );
            """)
            schema_exists = cursor.fetchone()[0]
            
            if not schema_exists:
                print("🔧 Criando schema 'fornecedores'...")
                cursor.execute("CREATE SCHEMA fornecedores;")
                conn.commit()
                print("✅ Schema 'fornecedores' criado!")
            
            print("🔧 Criando tabela 'fornecedores.refeicoes'...")
            
            create_table_sql = """
            CREATE TABLE fornecedores.refeicoes (
                id SERIAL PRIMARY KEY,
                data_refeicao DATE NOT NULL,
                cnpj CHAR(14) NOT NULL,
                fornecedor TEXT NOT NULL,
                cafe NUMERIC(10,2) DEFAULT 0,
                almoco_marmitex NUMERIC(10,2) DEFAULT 0,
                almoco_local NUMERIC(10,2) DEFAULT 0,
                janta_marmitex NUMERIC(10,2) DEFAULT 0,
                janta_local NUMERIC(10,2) DEFAULT 0,
                gelo NUMERIC(10,2) DEFAULT 0,
                valor_cafe NUMERIC(12,2) DEFAULT 0,
                valor_almoco_marmitex NUMERIC(12,2) DEFAULT 0,
                valor_almoco_local NUMERIC(12,2) DEFAULT 0,
                valor_janta_marmitex NUMERIC(12,2) DEFAULT 0,
                valor_janta_local NUMERIC(12,2) DEFAULT 0,
                valor_gelo NUMERIC(12,2) DEFAULT 0,
                total_cafe NUMERIC(14,2) DEFAULT 0,
                total_almoco_marmitex NUMERIC(14,2) DEFAULT 0,
                total_almoco_local NUMERIC(14,2) DEFAULT 0,
                total_janta_marmitex NUMERIC(14,2) DEFAULT 0,
                total_janta_local NUMERIC(14,2) DEFAULT 0,
                total_gelo NUMERIC(14,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            print("✅ Tabela 'fornecedores.refeicoes' criada com sucesso!")
            
            # Create index for performance
            cursor.execute("CREATE INDEX idx_refeicoes_data_cnpj ON fornecedores.refeicoes(data_refeicao, cnpj);")
            conn.commit()
            print("✅ Índice criado para performance!")
        
        conn.close()
        print("\n✅ Teste de conexão PostgreSQL concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na conexão PostgreSQL: {e}")
        print("\nDetalhes do erro:")
        print(traceback.format_exc())
        
        # Check for common issues
        if "could not connect" in str(e).lower():
            print("\n💡 Possíveis soluções:")
            print("1. Verificar se o host 'postgres.railway.internal' está acessível")
            print("2. Verificar se está executando dentro do Railway")
            print("3. Tentar com host externo se disponível")
        elif "authentication failed" in str(e).lower():
            print("\n💡 Possível solução:")
            print("1. Verificar se as credenciais estão corretas")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            print("\n💡 Possível solução:")
            print("1. Verificar se o banco 'railway' existe")

def test_insert_sample_data():
    """Test inserting sample data"""
    try:
        print("\n🧪 Testando inserção de dados de exemplo...")
        
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
            database=PG_CONFIG['database']
        )
        
        cursor = conn.cursor()
        
        # Insert sample data
        sample_data = {
            'data_refeicao': '2025-09-18',
            'cnpj': '12323430000123',
            'fornecedor': 'AGUINALDO JOSE DA SILVA - REST E ESPETINHO DO IRMÃO',
            'cafe': 2,
            'almoco_marmitex': 1,
            'almoco_local': 0,
            'janta_marmitex': 0,
            'janta_local': 1,
            'gelo': 0,
            'valor_cafe': 15.00,
            'valor_almoco_marmitex': 25.00,
            'valor_almoco_local': 0.00,
            'valor_janta_marmitex': 0.00,
            'valor_janta_local': 25.00,
            'valor_gelo': 0.00,
            'total_cafe': 30.00,  # 2 * 15.00
            'total_almoco_marmitex': 25.00,  # 1 * 25.00
            'total_almoco_local': 0.00,
            'total_janta_marmitex': 0.00,
            'total_janta_local': 25.00,  # 1 * 25.00
            'total_gelo': 0.00
        }
        
        insert_sql = """
        INSERT INTO fornecedores.refeicoes (
            data_refeicao, cnpj, fornecedor,
            cafe, almoco_marmitex, almoco_local, janta_marmitex, janta_local, gelo,
            valor_cafe, valor_almoco_marmitex, valor_almoco_local, 
            valor_janta_marmitex, valor_janta_local, valor_gelo,
            total_cafe, total_almoco_marmitex, total_almoco_local,
            total_janta_marmitex, total_janta_local, total_gelo
        ) VALUES (
            %(data_refeicao)s, %(cnpj)s, %(fornecedor)s,
            %(cafe)s, %(almoco_marmitex)s, %(almoco_local)s, 
            %(janta_marmitex)s, %(janta_local)s, %(gelo)s,
            %(valor_cafe)s, %(valor_almoco_marmitex)s, %(valor_almoco_local)s,
            %(valor_janta_marmitex)s, %(valor_janta_local)s, %(valor_gelo)s,
            %(total_cafe)s, %(total_almoco_marmitex)s, %(total_almoco_local)s,
            %(total_janta_marmitex)s, %(total_janta_local)s, %(total_gelo)s
        ) RETURNING id;
        """
        
        cursor.execute(insert_sql, sample_data)
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Dados de exemplo inseridos com ID: {new_id}")
        
        # Query the inserted data
        cursor.execute("SELECT * FROM fornecedores.refeicoes WHERE id = %s;", (new_id,))
        row = cursor.fetchone()
        print(f"📋 Dados inseridos: {row}")
        
        conn.close()
        print("✅ Teste de inserção concluído!")
        
    except Exception as e:
        print(f"❌ Erro na inserção: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_postgresql_connection()
    test_insert_sample_data()