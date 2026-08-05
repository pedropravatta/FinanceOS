import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class DecisionEngine:
    def __init__(self, comparativo_csv_path=None):
        self.csv_path = Path(comparativo_csv_path) if comparativo_csv_path else BASE_DIR / "compras_comparativo.csv"
        self.df = None
        self.report = {}

    def load_data(self):
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Arquivo comparativo de cashback não encontrado em: {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        return self.df

    def analyze(self):
        if self.df is None:
            self.load_data()

        # Encontrar as colunas de cashback por cartão
        cashback_cols = [col for col in self.df.columns if col.startswith("cashback_") and col != "cashback_melhor_cartao"]
        card_names = [col.replace("cashback_", "") for col in cashback_cols]

        if not card_names:
            raise ValueError("Nenhuma coluna de cashback de cartão encontrada no arquivo comparativo.")

        # 1. Cashback total por cartão
        card_totals = {}
        for card in card_names:
            card_totals[card] = round(float(self.df[f"cashback_{card}"].sum()), 4)

        # 2. Ranking dos cartões por cashback total
        sorted_cards = sorted(card_totals.items(), key=lambda x: x[1], reverse=True)
        ranking = [card for card, _ in sorted_cards]
        best_single_card = ranking[0]
        best_single_cashback = card_totals[best_single_card]

        # Cashback otimizado (usando o melhor cartão para cada compra)
        optimized_cashback = round(float(self.df["cashback_melhor_cartao"].sum()), 4)

        # 3. Diferenças absolutas e percentuais
        resumo_cartoes = {}
        for card in card_names:
            card_cashback = card_totals[card]

            # Diferença vs o melhor cartão único
            dif_abs_vs_melhor = round(best_single_cashback - card_cashback, 4)
            dif_pct_vs_melhor = round((dif_abs_vs_melhor / best_single_cashback * 100), 2) if best_single_cashback > 0 else 0.0

            # Diferença vs o cenário otimizado
            dif_abs_vs_otimizado = round(optimized_cashback - card_cashback, 4)
            dif_pct_vs_otimizado = round((dif_abs_vs_otimizado / optimized_cashback * 100), 2) if optimized_cashback > 0 else 0.0

            resumo_cartoes[card] = {
                "cashback_total": card_cashback,
                "diferenca_absoluta_vs_melhor_unico": dif_abs_vs_melhor,
                "diferenca_percentual_vs_melhor_unico": dif_pct_vs_melhor,
                "diferenca_absoluta_vs_otimizado": dif_abs_vs_otimizado,
                "diferenca_percentual_vs_otimizado": dif_pct_vs_otimizado
            }

        # 4. Melhor cartão por categoria e perda potencial por categoria
        # Agrupar por categoria e somar o cashback de cada cartão
        cat_groups = self.df.groupby("categoria")
        melhor_cartao_por_categoria = {}
        perda_potencial_por_categoria = {}

        for category, group in cat_groups:
            # Encontrar o melhor cartão para esta categoria
            cat_totals = {}
            for card in card_names:
                cat_totals[card] = round(float(group[f"cashback_{card}"].sum()), 4)

            best_card_for_cat = max(cat_totals, key=cat_totals.get)
            melhor_cartao_por_categoria[category] = best_card_for_cat

            # Calcular perdas potenciais para cada cartão comparado ao otimizado na categoria
            cat_optimized = round(float(group["cashback_melhor_cartao"].sum()), 4)
            perda_por_cartao = {}
            for card in card_names:
                perda_por_cartao[f"perda_{card}"] = round(cat_optimized - cat_totals[card], 4)

            perda_potencial_por_categoria[category] = {
                "cashback_otimizado": cat_optimized,
                **perda_por_cartao
            }

        # Montar o relatório final
        self.report = {
            "melhor_cartao_geral": best_single_card,
            "cashback_otimizado_total": optimized_cashback,
            "ranking_cartoes": ranking,
            "resumo_cartoes": resumo_cartoes,
            "melhor_cartao_por_categoria": melhor_cartao_por_categoria,
            "perda_potencial_por_categoria": perda_potencial_por_categoria
        }
        return self.report

    def save_report(self, output_path=None):
        out_path = Path(output_path) if output_path else BASE_DIR / "decision_report.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)
        return out_path

if __name__ == "__main__":
    try:
        engine = DecisionEngine()
        engine.analyze()
        report_path = engine.save_report()
        print(f"Relatório de decisão gerado com sucesso em: {report_path}")
    except FileNotFoundError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
