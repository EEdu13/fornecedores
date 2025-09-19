#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

def test_save_order_api():
    """Test the save order API"""
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
        print(f"  Café: {order_data['cafe']} × R$ {order_data['valor_cafe']:.2f} = R$ {order_data['cafe'] * order_data['valor_cafe']:.2f}")
        print(f"  Almoço Marmitex: {order_data['almoco_marmitex']} × R$ {order_data['valor_almoco_marmitex']:.2f} = R$ {order_data['almoco_marmitex'] * order_data['valor_almoco_marmitex']:.2f}")
        print(f"  Janta Local: {order_data['janta_local']} × R$ {order_data['valor_janta_local']:.2f} = R$ {order_data['janta_local'] * order_data['valor_janta_local']:.2f}")
        print(f"  Gelo: {order_data['gelo']} × R$ {order_data['valor_gelo']:.2f} = R$ {order_data['gelo'] * order_data['valor_gelo']:.2f}")
        
        total_expected = (
            order_data['cafe'] * order_data['valor_cafe'] +
            order_data['almoco_marmitex'] * order_data['valor_almoco_marmitex'] +
            order_data['janta_local'] * order_data['valor_janta_local'] +
            order_data['gelo'] * order_data['valor_gelo']
        )
        print(f"  💰 Total esperado: R$ {total_expected:.2f}")
        
        # Make POST request
        print("\n🔄 Enviando pedido para API...")
        response = requests.post(
            "http://localhost:8000/api/save-order",
            json=order_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Pedido salvo com sucesso!")
            print(f"📄 Resposta: {result}")
            print(f"🆔 ID do pedido: {result.get('id')}")
            print(f"📝 Mensagem: {result.get('message')}")
        else:
            print(f"❌ Erro ao salvar pedido: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_suppliers_api():
    """Test the suppliers API"""
    try:
        print("\n🔍 Testando API de fornecedores...")
        
        response = requests.get("http://localhost:8000/api/suppliers", timeout=10)
        
        if response.status_code == 200:
            suppliers = response.json()
            print(f"✅ API funcionando! Encontrados {len(suppliers)} fornecedores")
            
            # Show first supplier as example for orders
            if suppliers:
                supplier = suppliers[0]
                print(f"\n📋 Exemplo de fornecedor para pedidos:")
                print(f"  Nome: {supplier.get('fornecedor')}")
                print(f"  CNPJ: {supplier.get('cpf_cnpj')}")
                print(f"  Preços:")
                print(f"    Café: R$ {supplier.get('cafe', 0):.2f}")
                print(f"    Almoço Marmitex: R$ {supplier.get('almoco_marmitex', 0):.2f}")
                print(f"    Almoço Local: R$ {supplier.get('almoco_local', 0):.2f}")
                print(f"    Janta Marmitex: R$ {supplier.get('janta_marmitex', 0):.2f}")
                print(f"    Janta Local: R$ {supplier.get('janta_local', 0):.2f}")
                print(f"    Gelo: R$ {supplier.get('gelo', 0):.2f}")
        else:
            print(f"❌ Erro na API de fornecedores: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API de fornecedores: {e}")

if __name__ == "__main__":
    test_suppliers_api()
    test_save_order_api()