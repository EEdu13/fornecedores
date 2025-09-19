#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SQL Server Azure Configuration
SQL_CONFIG = {
    'server': os.getenv('SQL_SERVER'),
    'database': os.getenv('SQL_DATABASE'),
    'username': os.getenv('SQL_USERNAME'),
    'password': os.getenv('SQL_PASSWORD'),
    'driver': os.getenv('SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')
}

def get_suppliers_data():
    """Get suppliers data from SQL Server Azure"""
    try:
        # Connect to SQL Server Azure
        connection_string = (
            f"Driver={SQL_CONFIG['driver']};"
            f"Server=tcp:{SQL_CONFIG['server']},1433;"
            f"Database={SQL_CONFIG['database']};"
            f"Uid={SQL_CONFIG['username']};"
            f"Pwd={SQL_CONFIG['password']};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        
        print("🔗 Conectando ao SQL Server Azure...")
        conn = pyodbc.connect(connection_string)
        print("✅ Conectado com sucesso!")
        
        cursor = conn.cursor()
        
        # Query tb_fornecedores table
        query = """
        SELECT FORNECEDOR, CPF_CNPJ, VALOR, TIPO_FORN, PROJETO, LOCAL
        FROM tb_fornecedores
        ORDER BY FORNECEDOR, TIPO_FORN
        """
        
        print("📊 Executando consulta...")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"📋 Encontrados {len(rows)} registros")
        
        # Group by supplier and organize by meal type
        suppliers_dict = {}
        for row in rows:
            fornecedor = row[0] if row[0] else ''
            cpf_cnpj = row[1] if row[1] else ''
            valor = float(row[2]) if row[2] else 0.0
            tipo_forn = row[3] if row[3] else ''
            
            if fornecedor not in suppliers_dict:
                suppliers_dict[fornecedor] = {
                    'fornecedor': fornecedor,
                    'cpf_cnpj': cpf_cnpj,
                    'cafe': 0.0,
                    'almoco_marmitex': 0.0,
                    'almoco_local': 0.0,
                    'janta_marmitex': 0.0,
                    'janta_local': 0.0,
                    'gelo': 0.0
                }
            
            # Map meal types to the expected structure
            tipo_lower = tipo_forn.lower()
            if 'café' in tipo_lower or 'cafe' in tipo_lower:
                suppliers_dict[fornecedor]['cafe'] = valor
            elif 'almoço marmitex' in tipo_lower or 'almoco marmitex' in tipo_lower:
                suppliers_dict[fornecedor]['almoco_marmitex'] = valor
            elif 'almoço local' in tipo_lower or 'almoco local' in tipo_lower:
                suppliers_dict[fornecedor]['almoco_local'] = valor
            elif 'janta marmitex' in tipo_lower:
                suppliers_dict[fornecedor]['janta_marmitex'] = valor
            elif 'janta local' in tipo_lower:
                suppliers_dict[fornecedor]['janta_local'] = valor
            elif 'gelo' in tipo_lower:
                suppliers_dict[fornecedor]['gelo'] = valor
        
        suppliers = list(suppliers_dict.values())
        
        print(f"🏢 Processados {len(suppliers)} fornecedores únicos")
        
        # Show first few suppliers
        print("\n📋 Primeiros fornecedores:")
        for i, supplier in enumerate(suppliers[:3]):
            print(f"\n{i+1}. {supplier['fornecedor']}")
            print(f"   CPF/CNPJ: {supplier['cpf_cnpj']}")
            print(f"   Café: R$ {supplier['cafe']:.2f}")
            print(f"   Almoço Marmitex: R$ {supplier['almoco_marmitex']:.2f}")
            print(f"   Almoço Local: R$ {supplier['almoco_local']:.2f}")
            print(f"   Janta Marmitex: R$ {supplier['janta_marmitex']:.2f}")
            print(f"   Janta Local: R$ {supplier['janta_local']:.2f}")
            print(f"   Gelo: R$ {supplier['gelo']:.2f}")
        
        # Save to JSON file for testing
        output_file = "fornecedores_sql.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(suppliers, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados salvos em: {output_file}")
        
        conn.close()
        print("✅ Processamento concluído!")
        
        return suppliers
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return []

if __name__ == "__main__":
    get_suppliers_data()