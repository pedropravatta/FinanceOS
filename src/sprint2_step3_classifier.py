import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def run_classifier():
    # Carregar dados
    df = pd.read_csv(BASE_DIR / 'compras_saneada.csv')
    df_palavras = pd.read_csv(BASE_DIR / 'palavras.csv')
    df_estab = pd.read_csv(BASE_DIR / 'estabelecimentos.csv')
    
    # Criar dicionários para busca rápida
    palavras_map = dict(zip(df_palavras['palavra'], df_palavras['estabelecimento']))
    estab_map = df_estab.set_index('estabelecimento').to_dict('index')
    
    # Colunas de saída
    df['estabelecimento'] = "Não Identificado"
    df['categoria'] = "Outros"
    df['subcategoria'] = "Geral"
    df['confianca_classificacao'] = 0
    
    # Motor de Classificação
    for idx, row in df.iterrows():
        desc_norm = row['descricao_normalizada']
        
        # 1. Tentar encontrar estabelecimento por palavra-chave
        found_estab = None
        for key, value in palavras_map.items():
            if key in desc_norm:
                found_estab = value
                break
        
        if found_estab:
            df.at[idx, 'estabelecimento'] = found_estab
            df.at[idx, 'confianca_classificacao'] = 90 # Baseado em palavra-chave exata
            
            # 2. Tentar encontrar categoria e subcategoria
            if found_estab in estab_map:
                df.at[idx, 'categoria'] = estab_map[found_estab]['categoria']
                df.at[idx, 'subcategoria'] = estab_map[found_estab]['subcategoria']
                df.at[idx, 'confianca_classificacao'] = 100 # Confiança máxima se mapeado completo
        else:
            # Caso não identificado
            df.at[idx, 'confianca_classificacao'] = 10 # Baixa confiança
            
    # Salvar resultado
    df.to_csv(BASE_DIR / 'compras_classificadas.csv', index=False, encoding='utf-8-sig')
    
    # Gerar métricas para o relatório
    total = len(df)
    classificados = len(df[df['estabelecimento'] != "Não Identificado"])
    cobertura = (classificados / total) * 100
    confianca_media = df['confianca_classificacao'].mean()
    nao_classificados = df[df['estabelecimento'] == "Não Identificado"]
    
    report_data = {
        "total_compras": total,
        "classificadas_automaticamente": classificados,
        "percentual_cobertura": round(cobertura, 2),
        "percentual_confianca_media": round(confianca_media, 2),
        "quantidade_nao_classificadas": total - classificados,
        "exemplos_revisao": nao_classificados['descricao'].head(20).tolist()
    }
    
    with open(BASE_DIR / 'classification_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_classifier()
