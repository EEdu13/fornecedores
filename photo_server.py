#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
print("🔄 Iniciando imports...")

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pymssql
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
print("✅ Imports OK")

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configurações do banco Azure SQL - usando variáveis de ambiente
SQL_SERVER = os.getenv('SQL_SERVER', 'alrflorestal.database.windows.net')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'Tabela_teste')
SQL_USERNAME = os.getenv('SQL_USERNAME', 'sqladmin')
SQL_PASSWORD = os.getenv('SQL_PASSWORD', '')

# Configurações do PostgreSQL Railway - usando variáveis de ambiente
PG_HOST = os.getenv('PGHOST', 'ballast.proxy.rlwy.net')
PG_PORT = os.getenv('PGPORT', '21526')
PG_USER = os.getenv('PGUSER', 'postgres')
PG_PASSWORD = os.getenv('PGPASSWORD', '')
PG_DATABASE = os.getenv('PGDATABASE', 'railway')

print("✅ Configurações carregadas")

def conectar_azure_sql():
    """Conecta ao Azure SQL Server"""
    try:
        print(f"🔌 Conectando ao {SQL_SERVER}...")
        connection = pymssql.connect(
            server=SQL_SERVER,
            user=SQL_USERNAME,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
            timeout=30,
            login_timeout=30
        )
        print("✅ Conexão estabelecida!")
        return connection
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def conectar_postgresql():
    """Conecta ao PostgreSQL Railway"""
    try:
        print(f"🔌 Conectando ao PostgreSQL {PG_HOST}:{PG_PORT}...")
        connection = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DATABASE,
            connect_timeout=30
        )
        print("✅ Conexão PostgreSQL estabelecida!")
        return connection
    except Exception as e:
        print(f"❌ Erro ao conectar PostgreSQL: {e}")
        return None

def criar_tabela_pedidos_postgresql():
    """Cria a tabela tb_pedidos no PostgreSQL se não existir"""
    try:
        connection = conectar_postgresql()
        if not connection:
            print("❌ Erro: Não foi possível conectar ao PostgreSQL")
            return False
        
        cursor = connection.cursor()
        
        # Criar tabela com a estrutura correta
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tb_pedidos (
            id SERIAL PRIMARY KEY,
            data_refeicao DATE,
            cnpj CHAR(14),
            fornecedor TEXT,
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
            data_criacao TIMESTAMP DEFAULT NOW()
        );
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Tabela tb_pedidos criada/verificada no PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela PostgreSQL: {e}")
        return False

def buscar_valores_fornecedor(fornecedor_nome):
    """Busca os valores unitários de um fornecedor no SQL Azure"""
    try:
        connection = conectar_azure_sql()
        if not connection:
            return None

        cursor = connection.cursor(as_dict=True)
        cursor.execute("""
            SELECT FORNECEDOR, CPF_CNPJ, VALOR, TIPO_FORN
            FROM tb_fornecedores
            WHERE FORNECEDOR = %s
            ORDER BY TIPO_FORN
        """, (fornecedor_nome,))
        
        dados = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Organizar valores por tipo
        valores = {
            'fornecedor': fornecedor_nome,
            'cnpj': '',
            'cafe': 0.0,
            'almoco_marmitex': 0.0,
            'almoco_local': 0.0,
            'janta_marmitex': 0.0,
            'janta_local': 0.0,
            'gelo': 0.0
        }
        
        for row in dados:
            if row['CPF_CNPJ']:
                valores['cnpj'] = row['CPF_CNPJ']
            
            valor = float(row['VALOR']) if row['VALOR'] else 0.0
            tipo_clean = row['TIPO_FORN'].strip().upper() if row['TIPO_FORN'] else ''
            
            if tipo_clean in ['CAFÉ', 'CAFE']:
                valores['cafe'] = valor
            elif tipo_clean == 'ALMOÇO MARMITEX':
                valores['almoco_marmitex'] = valor
            elif tipo_clean == 'ALMOÇO LOCAL':
                valores['almoco_local'] = valor
            elif tipo_clean == 'JANTA MARMITEX':
                valores['janta_marmitex'] = valor
            elif tipo_clean == 'JANTA LOCAL':
                valores['janta_local'] = valor
            elif tipo_clean == 'GELO':
                valores['gelo'] = valor
        
        return valores
        
    except Exception as e:
        print(f"❌ Erro ao buscar valores do fornecedor: {e}")
        return None

@app.route('/favicon.ico')
def favicon():
    """Retorna um favicon vazio para evitar erro 404"""
    return '', 204

@app.route('/health')
def health_check():
    """Health check para Railway"""
    return jsonify({'status': 'healthy', 'service': 'fornecedores-api'}), 200

@app.route('/')
def index():
    """Serve o HTML principal"""
    print("📄 Servindo index.html")
    try:
        return send_file('index.html')
    except FileNotFoundError:
        return jsonify({'error': 'index.html não encontrado'}), 404

@app.route('/api/suppliers')
def get_suppliers():
    """API para buscar fornecedores da tabela tb_fornecedores"""
    print("🔍 Buscando dados da tabela tb_fornecedores...")
    
    try:
        # Conectar ao banco
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Erro de conexão com o banco de dados'
            }), 500

        # Executar query
        cursor = connection.cursor(as_dict=True)
        cursor.execute("""
            SELECT FORNECEDOR, CPF_CNPJ, VALOR, TIPO_FORN, PROJETO, LOCAL
            FROM tb_fornecedores
            ORDER BY FORNECEDOR, TIPO_FORN
        """)
        
        # Buscar todos os resultados
        dados = cursor.fetchall()
        
        # Fechar conexão
        cursor.close()
        connection.close()
        
        print(f"✅ Consulta executada: {len(dados)} registros")
        
        # Organizar dados por fornecedor
        suppliers_dict = {}
        for row in dados:
            fornecedor = row['FORNECEDOR'] if row['FORNECEDOR'] else ''
            cpf_cnpj = row['CPF_CNPJ'] if row['CPF_CNPJ'] else ''
            valor = float(row['VALOR']) if row['VALOR'] else 0.0
            tipo_forn = row['TIPO_FORN'] if row['TIPO_FORN'] else ''
            
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
            
            # Mapear tipos de fornecimento - aceitar variações
            tipo_clean = tipo_forn.strip().upper() if tipo_forn else ''
            
            if tipo_clean in ['CAFÉ', 'CAFE']:
                suppliers_dict[fornecedor]['cafe'] = valor
            elif tipo_clean == 'ALMOÇO MARMITEX':
                suppliers_dict[fornecedor]['almoco_marmitex'] = valor
            elif tipo_clean == 'ALMOÇO LOCAL':
                suppliers_dict[fornecedor]['almoco_local'] = valor
            elif tipo_clean == 'JANTA MARMITEX':
                suppliers_dict[fornecedor]['janta_marmitex'] = valor
            elif tipo_clean == 'JANTA LOCAL':
                suppliers_dict[fornecedor]['janta_local'] = valor
            elif tipo_clean == 'GELO':
                suppliers_dict[fornecedor]['gelo'] = valor
        
        suppliers = list(suppliers_dict.values())
        print(f"📊 Retornando {len(suppliers)} fornecedores com valores reais")
        return jsonify(suppliers)
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/photo/<session_id>')
def get_photo(session_id):
    """API para fotos (placeholder)"""
    return jsonify({'message': 'Photo API - implementar se necessário'})

@app.route('/api/save-order', methods=['POST'])
def save_order():
    """API para salvar pedidos com quantidades no banco"""
    try:
        data = request.get_json()
        print(f"📋 Pedido recebido: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Verificar se é formato novo (individual) ou antigo (múltiplos)
        if 'pedidos' in data:
            # Formato antigo com múltiplos pedidos
            funcionario = data.get('funcionario', '')
            cpf = data.get('cpf', '')
            data_pedido = data.get('data', '')
            pedidos = data.get('pedidos', [])
        else:
            # Formato novo - pedido individual
            funcionario = data.get('funcionario', 'Usuario')
            cpf = data.get('cnpj', '')  # Interface envia 'cnpj' em vez de 'cpf'
            data_pedido = data.get('data_refeicao', '')
            
            # Criar array de pedidos com um item
            pedidos = [{
                'fornecedor': data.get('fornecedor', ''),
                'cafe': data.get('cafe', 0),
                'almoco_marmitex': data.get('almoco_marmitex', 0),
                'almoco_local': data.get('almoco_local', 0),
                'janta_marmitex': data.get('janta_marmitex', 0),
                'janta_local': data.get('janta_local', 0),
                'gelo': data.get('gelo', 0)
            }]
        
        if not pedidos or len(pedidos) == 0:
            return jsonify({
                'success': False,
                'error': 'Nenhum pedido especificado'
            }), 400
        
        print(f"💾 Salvando pedido para {funcionario} (CPF: {cpf}) - {len(pedidos)} itens - Data: {data_pedido}")
        
        # Conectar ao PostgreSQL para salvar pedidos
        connection = conectar_postgresql()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Erro de conexão com o banco PostgreSQL'
            }), 500
        
        cursor = connection.cursor()
        
        # Salvar cada item do pedido
        itens_salvos = 0
        for pedido in pedidos:
            try:
                fornecedor = pedido.get('fornecedor', '')
                cnpj = cpf  # usar o CNPJ do pedido
                data_refeicao = data_pedido
                
                # Quantidades
                cafe_qtd = float(pedido.get('cafe', 0))
                almoco_marmitex_qtd = float(pedido.get('almoco_marmitex', 0))
                almoco_local_qtd = float(pedido.get('almoco_local', 0))
                janta_marmitex_qtd = float(pedido.get('janta_marmitex', 0))
                janta_local_qtd = float(pedido.get('janta_local', 0))
                gelo_qtd = float(pedido.get('gelo', 0))
                
                # Buscar valores unitários do SQL Azure
                sql_conn = conectar_azure_sql()
                if sql_conn:
                    sql_cursor = sql_conn.cursor(as_dict=True)
                    sql_cursor.execute("""
                        SELECT TIPO_FORN, VALOR 
                        FROM tb_fornecedores 
                        WHERE FORNECEDOR = %s
                    """, (fornecedor,))
                    
                    valores = sql_cursor.fetchall()
                    sql_cursor.close()
                    sql_conn.close()
                    
                    # Mapear valores unitários
                    valor_cafe = 0.0
                    valor_almoco_marmitex = 0.0
                    valor_almoco_local = 0.0
                    valor_janta_marmitex = 0.0
                    valor_janta_local = 0.0
                    valor_gelo = 0.0
                    
                    for row in valores:
                        tipo = row['TIPO_FORN'].strip().upper() if row['TIPO_FORN'] else ''
                        valor = float(row['VALOR']) if row['VALOR'] else 0.0
                        
                        if tipo in ['CAFÉ', 'CAFE']:
                            valor_cafe = valor
                        elif tipo == 'ALMOÇO MARMITEX':
                            valor_almoco_marmitex = valor
                        elif tipo == 'ALMOÇO LOCAL':
                            valor_almoco_local = valor
                        elif tipo == 'JANTA MARMITEX':
                            valor_janta_marmitex = valor
                        elif tipo == 'JANTA LOCAL':
                            valor_janta_local = valor
                        elif tipo == 'GELO':
                            valor_gelo = valor
                
                # Calcular totais
                total_cafe = cafe_qtd * valor_cafe
                total_almoco_marmitex = almoco_marmitex_qtd * valor_almoco_marmitex
                total_almoco_local = almoco_local_qtd * valor_almoco_local
                total_janta_marmitex = janta_marmitex_qtd * valor_janta_marmitex
                total_janta_local = janta_local_qtd * valor_janta_local
                total_gelo = gelo_qtd * valor_gelo
                
                # Inserir no PostgreSQL
                query = """
                INSERT INTO tb_pedidos 
                (data_refeicao, cnpj, fornecedor, cafe, almoco_marmitex, almoco_local, 
                 janta_marmitex, janta_local, gelo, valor_cafe, valor_almoco_marmitex,
                 valor_almoco_local, valor_janta_marmitex, valor_janta_local, valor_gelo,
                 total_cafe, total_almoco_marmitex, total_almoco_local, 
                 total_janta_marmitex, total_janta_local, total_gelo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    data_refeicao, cnpj, fornecedor,
                    cafe_qtd, almoco_marmitex_qtd, almoco_local_qtd,
                    janta_marmitex_qtd, janta_local_qtd, gelo_qtd,
                    valor_cafe, valor_almoco_marmitex, valor_almoco_local,
                    valor_janta_marmitex, valor_janta_local, valor_gelo,
                    total_cafe, total_almoco_marmitex, total_almoco_local,
                    total_janta_marmitex, total_janta_local, total_gelo
                ))
                
                itens_salvos += 1
                print(f"✅ Item salvo: {fornecedor} - Total: R$ {total_cafe + total_almoco_marmitex + total_almoco_local + total_janta_marmitex + total_janta_local + total_gelo:.2f}")
                
            except Exception as e:
                print(f"❌ Erro ao salvar item {fornecedor}: {e}")
                continue
        
        # Confirmar transação
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"✅ Pedido salvo: {itens_salvos} itens para {funcionario}")
        
        return jsonify({
            'success': True,
            'message': f'Pedido salvo com sucesso! {itens_salvos} itens processados',
            'itens_salvos': itens_salvos,
            'funcionario': funcionario,
            'data_pedido': data_pedido
        })
        
    except Exception as e:
        print(f"❌ Erro ao salvar pedido: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📊 Interface: http://localhost:5000")
    print("🔌 APIs disponíveis:")
    print("   GET  /api/suppliers - Buscar fornecedores")
    print("   GET  /api/photo/<id> - Fotos")
    print("   POST /api/save-order - Salvar pedidos")
    print("🔧 Configurações:")
    print(f"   SQL Server: {SQL_SERVER}")
    print(f"   SQL Database: {SQL_DATABASE}")
    print(f"   SQL User: {SQL_USERNAME}")
    print(f"   PostgreSQL: {PG_HOST}:{PG_PORT}")
    print(f"   PostgreSQL Database: {PG_DATABASE}")
    
    # Inicializar tabela de pedidos no PostgreSQL
    print("🔧 Inicializando tabela de pedidos no PostgreSQL...")
    criar_tabela_pedidos_postgresql()
    
    print("✅ Iniciando servidor...")
    
    # Usar porta do Railway se disponível, senão usar 5000
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()