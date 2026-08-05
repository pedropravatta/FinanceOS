import pandas as pd
import unicodedata
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def normalize_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    # Remover acentos
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    # Padronizar para minúsculas
    text = text.lower()
    # Remover caracteres especiais desnecessários (manter apenas letras, números e espaços simples)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Remover espaços duplicados
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def run_saneamento():
    input_path = BASE_DIR / 'compras_raw.csv'
    output_path = BASE_DIR / 'compras_saneada.csv'
    
    df = pd.read_csv(input_path)
    initial_count = len(df)
    
    # 1. Saneamento: Remover o que comprovadamente NÃO é compra
    # Filtros baseados nas instruções: cabeçalhos, títulos, linhas vazias, separadores
    palavras_filtro = [
        'fatura cartão', 'saldo inicial', 'saldo final', 'fatura final', 
        'deduções cc', 'adições cc', 'total contas', 'total outros', 
        'total final', 'não conciliados', 'lista reembolso', 'resumo cartão',
        'lista cartão de crédito', 'nubank', 'inter', 'conta corrente',
        'página1', 'página14', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto'
    ]
    
    # Criar máscara para remoção
    mask_remove = df['descricao'].str.lower().str.strip().isin(palavras_filtro)
    
    # Remover linhas onde o valor é nulo ou a descrição é nula
    mask_null = df['descricao'].isna() | df['valor_total'].isna()
    
    df_clean = df[~(mask_remove | mask_null)].copy()
    
    # 2. Normalização
    df_clean['descricao_normalizada'] = df_clean['descricao'].apply(normalize_text)
    
    # Remover linhas onde a descrição normalizada ficou vazia
    df_clean = df_clean[df_clean['descricao_normalizada'] != ""]
    
    final_count = len(df_clean)
    print(f"Saneamento concluído. Registros iniciais: {initial_count}, Registros após saneamento: {final_count}")
    
    df_clean.to_csv(output_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_saneamento()
