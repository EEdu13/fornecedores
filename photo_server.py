#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
print("🔄 Iniciando imports...")

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pymssql
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
        
        # Extrair dados do pedido
        funcionario = data.get('funcionario', '')
        cpf = data.get('cpf', '')
        data_pedido = data.get('data', '')
        pedidos = data.get('pedidos', [])
        
        if not pedidos:
            return jsonify({
                'success': False,
                'error': 'Nenhum pedido especificado'
            }), 400
        
        print(f"💾 Salvando pedido para {funcionario} - {len(pedidos)} itens")
        
        # Conectar ao banco para salvar
        connection = conectar_azure_sql()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Erro de conexão com o banco de dados'
            }), 500
        
        cursor = connection.cursor()
        
        # Salvar cada item do pedido
        itens_salvos = 0
        for pedido in pedidos:
            try:
                fornecedor = pedido.get('fornecedor', '')
                cafe_qtd = pedido.get('cafe', 0)
                almoco_marmitex_qtd = pedido.get('almoco_marmitex', 0)
                almoco_local_qtd = pedido.get('almoco_local', 0)
                janta_marmitex_qtd = pedido.get('janta_marmitex', 0)
                janta_local_qtd = pedido.get('janta_local', 0)
                gelo_qtd = pedido.get('gelo', 0)
                
                # Inserir pedido na tabela (assumindo que existe uma tabela tb_pedidos)
                query = """
                INSERT INTO tb_pedidos 
                (funcionario, cpf, data_pedido, fornecedor, cafe_qtd, almoco_marmitex_qtd, 
                 almoco_local_qtd, janta_marmitex_qtd, janta_local_qtd, gelo_qtd, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                """
                
                cursor.execute(query, (
                    funcionario, cpf, data_pedido, fornecedor,
                    cafe_qtd, almoco_marmitex_qtd, almoco_local_qtd,
                    janta_marmitex_qtd, janta_local_qtd, gelo_qtd
                ))
                
                itens_salvos += 1
                print(f"✅ Item salvo: {fornecedor} - CAFÉ:{cafe_qtd}, ALMOÇO MARMITEX:{almoco_marmitex_qtd}, ALMOÇO LOCAL:{almoco_local_qtd}")
                
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
            'funcionario': funcionario
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
    print(f"   Server: {SQL_SERVER}")
    print(f"   Database: {SQL_DATABASE}")
    print(f"   User: {SQL_USERNAME}")
    print("✅ Iniciando servidor...")
    
    # Usar porta do Railway se disponível, senão usar 5000
    port = int(os.environ.get('PORT', 5000))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()