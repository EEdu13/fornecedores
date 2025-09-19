#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import sys
import traceback

def test_order_api():
    """Test the save order API using urllib"""
    try:
        print("🧪 Testando API de salvar pedidos...")
        
        # Sample order data
        order_data = {
            'data_refeicao': '2025-09-18',
            'cnpj': '12323430000123',
            'fornecedor': 'AGUINALDO JOSE DA SILVA - REST E ESPETINHO DO IRMÃO',
            'cafe': 3,
            'almoco_marmitex': 2,
            'almoco_local': 0,
            'janta_marmitex': 0,
            'janta_local': 1,
            'gelo': 1,
            'valor_cafe': 15.00,
            'valor_almoco_marmitex': 25.00,
            'valor_almoco_local': 0.00,
            'valor_janta_marmitex': 0.00,
            'valor_janta_local': 25.00,
            'valor_gelo': 5.00
        }
        
        print("📋 Dados do pedido:")
        print(f"  Fornecedor: {order_data['fornecedor']}")
        print(f"  Data: {order_data['data_refeicao']}")
        print(f"  Café: {order_data['cafe']} × R$ {order_data['valor_cafe']:.2f}")
        print(f"  Almoço Marmitex: {order_data['almoco_marmitex']} × R$ {order_data['valor_almoco_marmitex']:.2f}")
        print(f"  Janta Local: {order_data['janta_local']} × R$ {order_data['valor_janta_local']:.2f}")
        print(f"  Gelo: {order_data['gelo']} × R$ {order_data['valor_gelo']:.2f}")
        
        # Prepare request
        data = json.dumps(order_data).encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:8000/api/save-order',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Content-Length': str(len(data))
            },
            method='POST'
        )
        
        print("\n🔄 Enviando pedido para API...")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            
            if status_code == 201:
                result = json.loads(response_data)
                print("✅ Pedido salvo com sucesso!")
                print(f"📄 Resposta: {result}")
                print(f"🆔 ID do pedido: {result.get('id')}")
                print(f"📝 Mensagem: {result.get('message')}")
            else:
                print(f"❌ Erro ao salvar pedido: {status_code}")
                print(f"Response: {response_data}")
                
    except urllib.error.URLError as e:
        print(f"❌ Erro de URL: {e}")
        print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("📊 Traceback:")
        traceback.print_exc()

def test_suppliers_api():
    """Test the suppliers API using urllib"""
    try:
        print("🔍 Testando API de fornecedores...")
        
        with urllib.request.urlopen('http://localhost:8000/api/suppliers', timeout=10) as response:
            status_code = response.getcode()
            
            if status_code == 200:
                data = response.read().decode('utf-8')
                suppliers = json.loads(data)
                print(f"✅ API funcionando! Encontrados {len(suppliers)} fornecedores")
                
                # Show first supplier as example
                if suppliers:
                    supplier = suppliers[0]
                    print(f"\n📋 Exemplo de fornecedor:")
                    print(f"  Nome: {supplier.get('fornecedor')}")
                    print(f"  CNPJ: {supplier.get('cpf_cnpj')}")
            else:
                print(f"❌ Erro na API de fornecedores: {status_code}")
                
    except Exception as e:
        print(f"❌ Erro ao testar API de fornecedores: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes das APIs...")
    test_suppliers_api()
    print("\n" + "="*50 + "\n")
    test_order_api()
    print("\n✨ Testes concluídos!")