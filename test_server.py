#!/usr/bin/env python3
import http.server
import socketserver
import json
import os

PORT = int(os.getenv('PORT', 8000))
HOST = '0.0.0.0'

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({'status': 'ok', 'message': 'Railway test server'})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_error(404)

if __name__ == "__main__":
    print(f"🚀 Test server starting on {HOST}:{PORT}")
    with socketserver.TCPServer((HOST, PORT), SimpleHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"✅ Server running on http://{HOST}:{PORT}")
        httpd.serve_forever()