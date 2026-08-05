import pandas as pd
import numpy as np
import os
import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class FinanceExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.xl = pd.ExcelFile(file_path)
        self.monthly_sheets = self._identify_monthly_sheets()
        self.raw_data = []
        self.report = {
            "sheets_processed": [],
            "inconsistencies": []
        }

    def _identify_monthly_sheets(self):
        # Meses em português para identificar as abas
        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        pattern = re.compile(f"({'|'.join(months)})(\\d{{2}})?", re.IGNORECASE)
        
        monthly_sheets = []
        for sheet in self.xl.sheet_names:
            if pattern.search(sheet):
                monthly_sheets.append(sheet)
        return monthly_sheets

    def _find_block_coordinates(self, df):
        """Identifica as coordenadas de início de blocos conhecidos na planilha."""
        coords = {}
        # Procurar por marcadores de blocos
        for r in range(min(len(df), 20)):
            for c in range(len(df.columns)):
                val = str(df.iloc[r, c]).strip()
                if "Data" in val and "Descrição" in str(df.iloc[r, c+1]):
                    coords['contas_fixas'] = (r, c)
                if "Lista Cartão" in val or "Nubank" in val or "Cartão de Crédito" in val:
                    # Encontrar onde a lista de transações do cartão começa (geralmente tem Data/Descrição ou só itens)
                    coords['cartao'] = (r, c)
        return coords

    def extract_sheet(self, sheet_name):
        df = self.xl.parse(sheet_name, header=None)
        sheet_report = {
            "sheet": sheet_name,
            "blocks_found": [],
            "transactions_count": 0
        }

        # 1. Bloco de Contas Fixas (Geralmente no topo à esquerda)
        # Procuramos a linha que contém "Data" e "Descrição"
        header_row = None
        for r in range(len(df)):
            row_vals = [str(x).strip() for x in df.iloc[r].values]
            if "Data" in row_vals and "Descrição" in row_vals:
                header_row = r
                break
        
        if header_row is not None:
            sheet_report["blocks_found"].append("Contas Fixas / Compartilhadas")
            # Extrair contas fixas
            # Colunas: Data, Descrição, Total, Pedro, Rafael, Renan...
            cols = df.iloc[header_row].values
            temp_df = df.iloc[header_row+1:].copy()
            temp_df.columns = cols
            
            # Pegar apenas até encontrar uma linha vazia na descrição ou o fim do bloco
            for _, row in temp_df.iterrows():
                if pd.isna(row['Descrição']) or str(row['Descrição']).strip() == "" or "Total" in str(row['Descrição']):
                    break
                
                self.raw_data.append({
                    "origem_aba": sheet_name,
                    "bloco": "Contas Fixas",
                    "data_original": row.get('Data'),
                    "descricao": row.get('Descrição'),
                    "valor_total": row.get('Total'),
                    "pedro": row.get('Pedro'),
                    "rafael": row.get('Rafael'),
                    "renan": row.get('Renan'),
                    "extra_info": ""
                })
                sheet_report["transactions_count"] += 1

        # 2. Bloco de Cartão de Crédito (Geralmente à direita ou abaixo)
        # Este bloco é mais irregular. Vamos procurar por colunas que pareçam transações de cartão
        # Frequentemente começa com "Lista Cartão de Crédito" ou "Nubank"
        card_header = None
        for r in range(len(df)):
            for c in range(len(df.columns)):
                val = str(df.iloc[r, c])
                if "Lista Cartão" in val or "Nubank" in val or "Inter" in val:
                    # Tentar identificar o cabeçalho logo abaixo ou na mesma linha
                    # Geralmente: Descrição | Valor
                    for r_search in range(r, r+3):
                        if r_search >= len(df): break
                        row_slice = df.iloc[r_search, c:c+5].values
                        # Se encontrarmos algo que parece uma descrição e um valor
                        if any(isinstance(x, (int, float)) for x in row_slice):
                            card_header = (r_search, c, val)
                            break
                    if card_header: break
            if card_header: break

        if card_header:
            r_start, c_start, block_name = card_header
            sheet_report["blocks_found"].append(f"Cartão ({block_name})")
            
            # Extrair até o fim da planilha ou linha de "Saldo"
            for r in range(r_start, len(df)):
                desc = df.iloc[r, c_start]
                valor = df.iloc[r, c_start+1] if c_start+1 < len(df.columns) else None
                
                if pd.isna(desc) or "Saldo" in str(desc) or "Fatura" in str(desc) or "Total" in str(desc) or "Resumo" in str(desc):
                    if r > r_start:
                        # Pequena heurística: se a próxima linha tiver dados, talvez seja só uma linha vazia no meio
                        next_r = r + 1
                        if next_r < len(df) and not pd.isna(df.iloc[next_r, c_start]):
                            continue
                        break
                    else:
                        continue
                
                if isinstance(valor, (int, float)) or (isinstance(valor, str) and "R$" in valor):
                    self.raw_data.append({
                        "origem_aba": sheet_name,
                        "bloco": f"Cartão ({block_name})",
                        "data_original": "", # Cartão nem sempre tem data na linha
                        "descricao": desc,
                        "valor_total": valor,
                        "pedro": "",
                        "rafael": "",
                        "renan": "",
                        "extra_info": f"Posição: L{r}C{c_start}"
                    })
                    sheet_report["transactions_count"] += 1

        self.report["sheets_processed"].append(sheet_report)

    def run(self):
        for sheet in self.monthly_sheets:
            try:
                self.extract_sheet(sheet)
            except Exception as e:
                self.report["inconsistencies"].append(f"Erro na aba {sheet}: {str(e)}")
        
        # Salvar CSV
        output_df = pd.DataFrame(self.raw_data)
        output_df.to_csv(BASE_DIR / 'compras_raw.csv', index=False, encoding='utf-8-sig')
        
        # Salvar Relatório
        with open(BASE_DIR / 'extraction_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    extractor = FinanceExtractor(BASE_DIR / 'Contas Pedro.xlsx')
    extractor.run()
    print("Extração concluída com sucesso.")
