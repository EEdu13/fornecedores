#!/usr/bin/env python3
"""
Script para converter Results.xlsx para results.json
Para usar antes do deploy no Netlify
"""

import pandas as pd
import json

def convert_excel_to_json():
    try:
        # Ler o arquivo Excel
        df = pd.read_excel('Results.xlsx')
        
        # Converter para formato JSON
        data = df.to_dict('records')
        
        # Salvar como JSON
        with open('results.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ Arquivo convertido com sucesso!")
        print("📁 results.json criado")
        print(f"📊 {len(data)} registros convertidos")
        
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")

if __name__ == "__main__":
    convert_excel_to_json()
