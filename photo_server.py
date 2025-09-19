#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import json
import os
import socket
import pyodbc
import sqlite3
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("🔍 DEBUG: Carregando variáveis de ambiente...")

# SQL Server Azure Configuration
SQL_CONFIG = {
    'server': os.getenv('SQL_SERVER'),
    'database': os.getenv('SQL_DATABASE'),
    'username': os.getenv('SQL_USERNAME'),
    'password': os.getenv('SQL_PASSWORD'),
    'driver': os.getenv('SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')
}

# PostgreSQL Railway Configuration
try:
    pgport = int(os.getenv('PGPORT', 21526))
except (ValueError, TypeError):
    pgport = 21526
    print(f"⚠️  PGPORT inválido, usando padrão: {pgport}")

PG_CONFIG = {
    'host': os.getenv('PGHOST'),
    'port': pgport,
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'database': os.getenv('PGDATABASE')
}

print(f"🔍 SQL_SERVER: {'✅' if SQL_CONFIG.get('server') else '❌'}")
print(f"🔍 PGHOST: {'✅' if PG_CONFIG.get('host') else '❌'}")
print(f"🔍 PORT env: {os.getenv('PORT', 'não definida')}")

class PhotoHandler:
    # In-memory storage for photos (temporary)
    photos = {}
    
    @staticmethod
    def cleanup_old_photos():
        """Remove photos older than 1 hour"""
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
        to_remove = []
        
        for session_id, data in PhotoHandler.photos.items():
            if data['timestamp'].timestamp() < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del PhotoHandler.photos[session_id]
        
        if to_remove:
            print(f"Cleaned up {len(to_remove)} old photos")

class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    
    def get_sql_connection(self):
        """Create and return SQL Server Azure connection"""
        try:
            if not SQL_CONFIG.get('server') or not SQL_CONFIG.get('password'):
                raise Exception("SQL Server credentials not configured")
                
            connection_string = (
                f"Driver={SQL_CONFIG['driver']};"
                f"Server={SQL_CONFIG['server']};"
                f"Database={SQL_CONFIG['database']};"
                f"Uid={SQL_CONFIG['username']};"
                f"Pwd={SQL_CONFIG['password']};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
            )
            
            conn = pyodbc.connect(connection_string)
            print("✅ Connected to SQL Server Azure successfully")
            return conn
            
        except Exception as e:
            print(f"❌ Error connecting to SQL Server Azure: {e}")
            raise

    def get_pg_connection(self):
        """Create and return PostgreSQL Railway connection or SQLite fallback"""
        try:
            # First try PostgreSQL if configured
            if PG_CONFIG.get('host') and PG_CONFIG.get('password'):
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=PG_CONFIG['host'],
                        port=PG_CONFIG['port'],
                        user=PG_CONFIG['user'],
                        password=PG_CONFIG['password'],
                        database=PG_CONFIG['database']
                    )
                    print("✅ Connected to PostgreSQL Railway successfully")
                    return conn, 'postgresql'
                except ImportError:
                    print("⚠️  psycopg2 not available, falling back to SQLite")
                except Exception as e:
                    print(f"⚠️  PostgreSQL failed ({e}), falling back to SQLite")
            
            # Fallback to SQLite
            db_path = 'orders.db'
            conn = sqlite3.connect(db_path)
            
            # Create table if it doesn't exist
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS refeicoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_refeicao TEXT NOT NULL,
                    cnpj TEXT NOT NULL,
                    fornecedor TEXT NOT NULL,
                    cafe_qty REAL DEFAULT 0,
                    cafe_valor_unitario REAL DEFAULT 0,
                    cafe_total REAL DEFAULT 0,
                    almoco_marmitex_qty REAL DEFAULT 0,
                    almoco_marmitex_valor_unitario REAL DEFAULT 0,
                    almoco_marmitex_total REAL DEFAULT 0,
                    almoco_local_qty REAL DEFAULT 0,
                    almoco_local_valor_unitario REAL DEFAULT 0,
                    almoco_local_total REAL DEFAULT 0,
                    janta_marmitex_qty REAL DEFAULT 0,
                    janta_marmitex_valor_unitario REAL DEFAULT 0,
                    janta_marmitex_total REAL DEFAULT 0,
                    janta_local_qty REAL DEFAULT 0,
                    janta_local_valor_unitario REAL DEFAULT 0,
                    janta_local_total REAL DEFAULT 0,
                    gelo_qty REAL DEFAULT 0,
                    gelo_valor_unitario REAL DEFAULT 0,
                    gelo_total REAL DEFAULT 0,
                    total_geral REAL DEFAULT 0,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
            print("✅ Connected to SQLite fallback successfully")
            return conn, 'sqlite'
            
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            raise

    def cleanup_old_photos(self):
        """Remove photos older than 1 hour"""
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
        to_remove = []
        
        for session_id, data in PhotoHandler.photos.items():
            if data['timestamp'].timestamp() < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del PhotoHandler.photos[session_id]

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Parse URL to remove query parameters
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        print(f"🔍 Received GET request: {path}")
        
        if path == '/':
            # Health check endpoint for Railway - sempre retorna 200
            print("💚 Health check endpoint accessed")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Simple response for health check
            response = json.dumps({
                'status': 'healthy',
                'service': 'Fornecedores API'
            })
            self.wfile.write(response.encode('utf-8'))
            return
                
        elif path == '/api/suppliers':
            # Fetch suppliers from SQL Server Azure
            try:
                if not SQL_CONFIG.get('server') or not SQL_CONFIG.get('password'):
                    self.send_response(503)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'SQL Server not configured',
                        'message': 'Database credentials not available'
                    }).encode('utf-8'))
                    return
                
                conn = self.get_sql_connection()
                cursor = conn.cursor()
                
                # Query tb_fornecedores table
                query = """
                SELECT FORNECEDOR, CPF_CNPJ, VALOR, TIPO_FORN, PROJETO, LOCAL
                FROM tb_fornecedores
                ORDER BY FORNECEDOR, TIPO_FORN
                """
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
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
                    
                    # Direct mapping based on exact SQL values
                    if tipo_forn == 'CAFÉ':
                        suppliers_dict[fornecedor]['cafe'] = valor
                    elif tipo_forn == 'ALMOÇO MARMITEX':
                        suppliers_dict[fornecedor]['almoco_marmitex'] = valor
                    elif tipo_forn == 'ALMOÇO LOCAL':
                        suppliers_dict[fornecedor]['almoco_local'] = valor
                    elif tipo_forn == 'JANTA MARMITEX':
                        suppliers_dict[fornecedor]['janta_marmitex'] = valor
                    elif tipo_forn == 'JANTA LOCAL':
                        suppliers_dict[fornecedor]['janta_local'] = valor
                    elif tipo_forn == 'GELO':
                        suppliers_dict[fornecedor]['gelo'] = valor
                
                suppliers = list(suppliers_dict.values())
                
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(suppliers, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                print(f"Error fetching suppliers: {e}")
                self.send_error(500, f"Database error: {str(e)}")
                
        elif path.startswith('/api/photo/'):
            # Extract session ID from path
            session_id = path.split('/')[-1]
            
            # Check if photo exists
            photo_data = PhotoHandler.photos.get(session_id)
            
            if photo_data:
                # Clean up old photos (older than 1 hour)
                self.cleanup_old_photos()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'found',
                    'photo': photo_data['photo']
                }).encode('utf-8'))
                
                # Clean up after retrieval
                del PhotoHandler.photos[session_id]
                print(f"Photo retrieved and cleaned up for session: {session_id}")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'not_found'}).encode('utf-8'))
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        # Parse URL to remove query parameters
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/save-order':
            # Save order to database (PostgreSQL or SQLite fallback)
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self.send_error(400, "No data provided")
                    return
                
                post_data = self.rfile.read(content_length)
                order_data = json.loads(post_data.decode('utf-8'))
                
                # Validate required fields
                required_fields = ['data_refeicao', 'cnpj', 'fornecedor']
                for field in required_fields:
                    if field not in order_data:
                        self.send_error(400, f"Missing required field: {field}")
                        return
                
                conn, db_type = self.get_pg_connection()
                cursor = conn.cursor()
                
                # Calculate totals
                cafe_qty = float(order_data.get('cafe', 0))
                almoco_marmitex_qty = float(order_data.get('almoco_marmitex', 0))
                almoco_local_qty = float(order_data.get('almoco_local', 0))
                janta_marmitex_qty = float(order_data.get('janta_marmitex', 0))
                janta_local_qty = float(order_data.get('janta_local', 0))
                gelo_qty = float(order_data.get('gelo', 0))
                
                valor_cafe = float(order_data.get('valor_cafe', 0))
                valor_almoco_marmitex = float(order_data.get('valor_almoco_marmitex', 0))
                valor_almoco_local = float(order_data.get('valor_almoco_local', 0))
                valor_janta_marmitex = float(order_data.get('valor_janta_marmitex', 0))
                valor_janta_local = float(order_data.get('valor_janta_local', 0))
                valor_gelo = float(order_data.get('valor_gelo', 0))
                
                total_cafe = cafe_qty * valor_cafe
                total_almoco_marmitex = almoco_marmitex_qty * valor_almoco_marmitex
                total_almoco_local = almoco_local_qty * valor_almoco_local
                total_janta_marmitex = janta_marmitex_qty * valor_janta_marmitex
                total_janta_local = janta_local_qty * valor_janta_local
                total_gelo = gelo_qty * valor_gelo
                
                total_geral = (total_cafe + total_almoco_marmitex + total_almoco_local + 
                             total_janta_marmitex + total_janta_local + total_gelo)
                
                # Insert into database (PostgreSQL or SQLite)
                if db_type == 'postgresql':
                    insert_query = """
                    INSERT INTO fornecedores.refeicoes (
                        data_refeicao, cnpj, fornecedor,
                        cafe_qty, cafe_valor_unitario, cafe_total,
                        almoco_marmitex_qty, almoco_marmitex_valor_unitario, almoco_marmitex_total,
                        almoco_local_qty, almoco_local_valor_unitario, almoco_local_total,
                        janta_marmitex_qty, janta_marmitex_valor_unitario, janta_marmitex_total,
                        janta_local_qty, janta_local_valor_unitario, janta_local_total,
                        gelo_qty, gelo_valor_unitario, gelo_total,
                        total_geral, data_criacao
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, NOW()
                    )
                    """
                    
                    cursor.execute(insert_query, (
                        order_data['data_refeicao'], order_data['cnpj'], order_data['fornecedor'],
                        cafe_qty, valor_cafe, total_cafe,
                        almoco_marmitex_qty, valor_almoco_marmitex, total_almoco_marmitex,
                        almoco_local_qty, valor_almoco_local, total_almoco_local,
                        janta_marmitex_qty, valor_janta_marmitex, total_janta_marmitex,
                        janta_local_qty, valor_janta_local, total_janta_local,
                        gelo_qty, valor_gelo, total_gelo,
                        total_geral
                    ))
                else:  # SQLite
                    insert_query = """
                    INSERT INTO refeicoes (
                        data_refeicao, cnpj, fornecedor,
                        cafe_qty, cafe_valor_unitario, cafe_total,
                        almoco_marmitex_qty, almoco_marmitex_valor_unitario, almoco_marmitex_total,
                        almoco_local_qty, almoco_local_valor_unitario, almoco_local_total,
                        janta_marmitex_qty, janta_marmitex_valor_unitario, janta_marmitex_total,
                        janta_local_qty, janta_local_valor_unitario, janta_local_total,
                        gelo_qty, gelo_valor_unitario, gelo_total,
                        total_geral
                    ) VALUES (
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?
                    )
                    """
                    
                    cursor.execute(insert_query, (
                        order_data['data_refeicao'], order_data['cnpj'], order_data['fornecedor'],
                        cafe_qty, valor_cafe, total_cafe,
                        almoco_marmitex_qty, valor_almoco_marmitex, total_almoco_marmitex,
                        almoco_local_qty, valor_almoco_local, total_almoco_local,
                        janta_marmitex_qty, valor_janta_marmitex, total_janta_marmitex,
                        janta_local_qty, valor_janta_local, total_janta_local,
                        gelo_qty, valor_gelo, total_gelo,
                        total_geral
                    ))
                
                conn.commit()
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': 'Order saved successfully',
                    'total': total_geral
                }).encode('utf-8'))
                
            except Exception as e:
                print(f"Error saving order: {e}")
                self.send_error(500, f"Database error: {str(e)}")
                
        elif path == '/api/photo':
            # Store photo temporarily
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self.send_error(400, "No data provided")
                    return
                
                post_data = self.rfile.read(content_length)
                photo_data = json.loads(post_data.decode('utf-8'))
                
                if 'session_id' not in photo_data or 'photo' not in photo_data:
                    self.send_error(400, "Missing session_id or photo data")
                    return
                
                # Store photo with timestamp
                PhotoHandler.photos[photo_data['session_id']] = {
                    'photo': photo_data['photo'],
                    'timestamp': datetime.now()
                }
                
                # Clean up old photos
                PhotoHandler.cleanup_old_photos()
                
                print(f"Photo stored for session: {photo_data['session_id']}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'stored'}).encode('utf-8'))
                
            except Exception as e:
                print(f"Error storing photo: {e}")
                self.send_error(500, f"Error: {str(e)}")
        else:
            self.send_error(404)

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

if __name__ == "__main__":
    # Change to the script directory to serve files from there
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Get port and host from environment variables
    PORT = int(os.getenv('PORT', 8000))
    HOST = '0.0.0.0'  # Always use 0.0.0.0 for Railway deployment
    
    print("=" * 50)
    print("🚀 INICIANDO FORNECEDORES API")
    print("=" * 50)
    print(f"🌐 Host: {HOST}")
    print(f"🔌 Porta: {PORT}")
    print(f"🗄️  SQL Server Config: {bool(SQL_CONFIG.get('server'))}")
    print(f"🐘 PostgreSQL Config: {bool(PG_CONFIG.get('host'))}")
    print("🔍 Railway PORT env:", os.getenv('PORT'))
    print("=" * 50)
    
    try:
        # Test if we can bind to the port
        print(f"🔄 Tentando bind em {HOST}:{PORT}")
        httpd = socketserver.TCPServer((HOST, PORT), HTTPHandler)
        httpd.allow_reuse_address = True
        httpd.timeout = 30  # Add socket timeout
        print(f"✅ Servidor inicializado com sucesso em http://{HOST}:{PORT}")
        print(f"🔗 Health check em: http://{HOST}:{PORT}/")
        print(f"📊 API de fornecedores: http://{HOST}:{PORT}/api/suppliers")
        print(f"📷 API de fotos: http://{HOST}:{PORT}/api/photo/[session_id]")
        print(f"💾 API de pedidos: http://{HOST}:{PORT}/api/save-order")
        print("📱 Sistema de QR Code e sincronização de fotos ativo")
        print("🔄 Servidor pronto para receber requests...")
        print("=" * 50)
        
        # Flush stdout to ensure Railway sees the logs
        import sys
        sys.stdout.flush()
        
        # Start the server
        httpd.serve_forever()
        
    except OSError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        if hasattr(e, 'errno') and e.errno == 10048:  # Port already in use on Windows
            PORT = get_free_port()
            try:
                httpd = socketserver.TCPServer((HOST, PORT), HTTPHandler)
                httpd.allow_reuse_address = True
                print(f"⚠️  Porta original ocupada, usando porta {PORT}")
                print(f"✅ Servidor rodando em http://{HOST}:{PORT}")
                httpd.serve_forever()
            except Exception as backup_error:
                print(f"❌ Erro crítico: {backup_error}")
                raise
        else:
            print(f"❌ Erro de bind: {e}")
            raise
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        traceback.print_exc()
        raise