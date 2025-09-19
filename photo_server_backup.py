#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import json
import os
import json
import socket
import pyodbc
import psycopg2
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def validate_env_vars():
    """Validate required environment variables"""
    required_vars = ['SQL_SERVER', 'SQL_DATABASE', 'SQL_USERNAME', 'SQL_PASSWORD', 
                    'PGHOST', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Sistema funcionará com funcionalidade limitada")
        return False
    
    print("✅ Todas as variáveis de ambiente estão configuradas")
    return True

# Validate environment variables on startup
env_valid = validate_env_vars()

# SQL Server Azure Configuration
SQL_CONFIG = {
    'server': os.getenv('SQL_SERVER'),
    'database': os.getenv('SQL_DATABASE'),
    'username': os.getenv('SQL_USERNAME'),
    'password': os.getenv('SQL_PASSWORD'),
    'driver': os.getenv('SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')
}

# PostgreSQL Railway Configuration
PG_CONFIG = {
    'host': os.getenv('PGHOST'),
    'port': int(os.getenv('PGPORT', 21526)),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'database': os.getenv('PGDATABASE')
}

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
            print(f"Cleaned up old photo for session: {session_id}")

class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def get_sql_connection(self):
        """Create and return SQL Server Azure connection"""
        try:
            # Check if required config is available
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
        """Create and return PostgreSQL Railway connection"""
        try:
            # Check if required config is available
            if not PG_CONFIG.get('host') or not PG_CONFIG.get('password'):
                raise Exception("PostgreSQL credentials not configured")
                
            conn = psycopg2.connect(
                host=PG_CONFIG['host'],
                port=PG_CONFIG['port'],
                user=PG_CONFIG['user'],
                password=PG_CONFIG['password'],
                database=PG_CONFIG['database']
            )
            print("✅ Connected to PostgreSQL Railway successfully")
            return conn
            
        except Exception as e:
            print(f"❌ Error connecting to PostgreSQL Railway: {e}")
            raise
            
        except Exception as e:
            print(f"Error connecting to PostgreSQL Railway: {e}")
            print(traceback.format_exc())
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
            print(f"Cleaned up old photo for session: {session_id}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Parse URL to remove query parameters
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/suppliers':
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
                    
                    print(f"Mapped: {fornecedor} - {tipo_forn} = R$ {valor}")
                
                suppliers = list(suppliers_dict.values())
                
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(suppliers, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                print(f"Error fetching suppliers: {e}")
                print(traceback.format_exc())
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
        elif path == '/':
            # Health check endpoint for Railway - sempre retorna 200
            try:
                # Test basic functionality
                status = {
                    'status': 'healthy',
                    'service': 'Fornecedores API',
                    'version': '1.0.0',
                    'timestamp': datetime.now().isoformat(),
                    'endpoints': {
                        'suppliers': '/api/suppliers',
                        'photos': '/api/photo/{session_id}',
                        'save_order': '/api/save-order'
                    },
                    'environment': {
                        'sql_configured': bool(SQL_CONFIG.get('server') and SQL_CONFIG.get('password')),
                        'postgres_configured': bool(PG_CONFIG.get('host') and PG_CONFIG.get('password'))
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(status, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                # Even if there's an error, return 200 for health check
                print(f"Health check error (but still returning 200): {e}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'healthy',
                    'service': 'Fornecedores API',
                    'note': 'Basic health check passed'
                }).encode('utf-8'))
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        # Parse URL to remove query parameters
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/save-order':
            # Save order to PostgreSQL
            try:
                if not PG_CONFIG.get('host') or not PG_CONFIG.get('password'):
                    self.send_response(503)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'PostgreSQL not configured',
                        'message': 'Database credentials not available'
                    }).encode('utf-8'))
                    return
                
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
                
                conn = self.get_pg_connection()
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
                
                # Insert order
                insert_sql = """
                INSERT INTO fornecedores.refeicoes (
                    data_refeicao, cnpj, fornecedor,
                    cafe, almoco_marmitex, almoco_local, janta_marmitex, janta_local, gelo,
                    valor_cafe, valor_almoco_marmitex, valor_almoco_local, 
                    valor_janta_marmitex, valor_janta_local, valor_gelo,
                    total_cafe, total_almoco_marmitex, total_almoco_local,
                    total_janta_marmitex, total_janta_local, total_gelo
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                ) RETURNING id;
                """
                
                cursor.execute(insert_sql, (
                    order_data['data_refeicao'], order_data['cnpj'], order_data['fornecedor'],
                    cafe_qty, almoco_marmitex_qty, almoco_local_qty, janta_marmitex_qty, janta_local_qty, gelo_qty,
                    valor_cafe, valor_almoco_marmitex, valor_almoco_local, valor_janta_marmitex, valor_janta_local, valor_gelo,
                    total_cafe, total_almoco_marmitex, total_almoco_local, total_janta_marmitex, total_janta_local, total_gelo
                ))
                
                new_id = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                
                print(f"Order saved successfully with ID: {new_id}")
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'id': new_id,
                    'message': 'Pedido salvo com sucesso!'
                }, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                print(f"Error saving order: {e}")
                print(traceback.format_exc())
                self.send_error(500, f"Database error: {str(e)}")
                
        elif path.startswith('/api/photo/'):
            # Extract session ID from path
            session_id = self.path.split('/')[-1]
            
            # Read photo data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                photo_data = data.get('photo')
                
                if photo_data:
                    # Store photo with timestamp for cleanup
                    PhotoHandler.photos[session_id] = {
                        'photo': photo_data,
                        'timestamp': datetime.now()
                    }
                    
                    print(f"Photo stored for session: {session_id}")
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                else:
                    self.send_error(400, "No photo data provided")
            except Exception as e:
                print(f"Error storing photo: {e}")
                self.send_error(500, str(e))
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
    HOST = os.getenv('HOST', '0.0.0.0')  # Default to 0.0.0.0 for Railway
    
    print("=" * 50)
    print("🚀 INICIANDO FORNECEDORES API")
    print("=" * 50)
    print(f"🌐 Host: {HOST}")
    print(f"🔌 Porta: {PORT}")
    print(f"📝 Environment Variables Loaded: {env_valid}")
    print(f"🗄️  SQL Server Config: {bool(SQL_CONFIG.get('server'))}")
    print(f"🐘 PostgreSQL Config: {bool(PG_CONFIG.get('host'))}")
    print("=" * 50)
    
    try:
        # Test if we can bind to the port
        httpd = socketserver.TCPServer((HOST, PORT), HTTPHandler)
        httpd.allow_reuse_address = True
        
        print(f"✅ Servidor rodando em http://{HOST}:{PORT}")
        print(f"🏥 Health Check: http://{HOST}:{PORT}/")
        print(f"📊 API de fornecedores: http://{HOST}:{PORT}/api/suppliers")
        print(f"📷 API de fotos: http://{HOST}:{PORT}/api/photo/[session_id]")
        print(f"💾 API de pedidos: http://{HOST}:{PORT}/api/save-order")
        print("📱 Sistema de QR Code e sincronização de fotos ativo")
        print("🔄 Servidor pronto para receber requests...")
        print("=" * 50)
        
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
            except Exception as backup_error:
                print(f"❌ Erro crítico: {backup_error}")
                raise
        else:
            raise
    except KeyboardInterrupt:
        print("\n� Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        traceback.print_exc()
        raise