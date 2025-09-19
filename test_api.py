#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_suppliers_api():
    """Test the suppliers API"""
    try:
        print("🔍 Testando API de fornecedores...")
        
        # Make request to the suppliers API
        response = requests.get("http://localhost:8000/api/suppliers", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            suppliers = response.json()
            print(f"✅ API funcionando! Encontrados {len(suppliers)} fornecedores:")
            
            # Show first few suppliers
            for i, supplier in enumerate(suppliers[:3]):
                print(f"\n{i+1}. {supplier.get('fornecedor', 'N/A')}")
                print(f"   CPF/CNPJ: {supplier.get('cpf_cnpj', 'N/A')}")
                print(f"   Café: R$ {supplier.get('cafe', 0):.2f}")
                print(f"   Almoço Marmitex: R$ {supplier.get('almoco_marmitex', 0):.2f}")
                print(f"   Almoço Local: R$ {supplier.get('almoco_local', 0):.2f}")
                print(f"   Janta Marmitex: R$ {supplier.get('janta_marmitex', 0):.2f}")
                print(f"   Janta Local: R$ {supplier.get('janta_local', 0):.2f}")
                print(f"   Gelo: R$ {supplier.get('gelo', 0):.2f}")
            
            if len(suppliers) > 3:
                print(f"\n... e mais {len(suppliers) - 3} fornecedores")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_suppliers_api()