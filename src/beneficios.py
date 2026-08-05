import pandas as pd
import json
import os

class BenefitsEngine:
    def __init__(self, classified_data_path, card_rules_dir):
        self.df_classified = pd.read_csv(classified_data_path)
        self.card_rules_dir = card_rules_dir
        self.card_configs = self._load_card_configs()

    def _load_card_configs(self):
        card_configs = {}
        for filename in os.listdir(self.card_rules_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.card_rules_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    card_configs[config["nome"]] = config
        return card_configs

    def calculate_cashback(self, row, card_name):
        card_config = self.card_configs.get(card_name)
        if not card_config:
            return 0.0

        value = pd.to_numeric(row["valor_total"], errors=\'coerce\')
        if pd.isna(value): return 0.0 # Retorna 0 se o valor não for numérico
        category = row["categoria"]
        
        cashback_rate = card_config["cashback"]["geral"]
        
        # Verificar categorias bonificadas
        if "categorias" in card_config["cashback"]:
            if category in card_config["cashback"]["categorias"]:
                cashback_rate = card_config["cashback"]["categorias"][category]
        
        return value * cashback_rate

    def run_comparison(self):
        # Adicionar colunas para o cashback de cada cartão
        for card_name in self.card_configs.keys():
            self.df_classified[f"cashback_{card_name}"] = self.df_classified.apply(
                lambda row: self.calculate_cashback(row, card_name), axis=1
            )
        
        # Identificar o melhor cartão para cada transação
        self.df_classified["melhor_cartao"] = ""
        self.df_classified["cashback_melhor_cartao"] = 0.0

        for idx, row in self.df_classified.iterrows():
            best_card = ""
            max_cashback = -1.0
            
            for card_name in self.card_configs.keys():
                current_cashback = row[f"cashback_{card_name}"]
                if current_cashback > max_cashback:
                    max_cashback = current_cashback
                    best_card = card_name
            
            self.df_classified.at[idx, "melhor_cartao"] = best_card
            self.df_classified.at[idx, "cashback_melhor_cartao"] = max_cashback

        # Salvar o resultado
        self.df_classified.to_csv(
            '/home/ubuntu/projects/finance-os-e55f724c/compras_comparativo.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        return self.df_classified

if __name__ == "__main__":
    engine = BenefitsEngine(
        classified_data_path='/home/ubuntu/projects/finance-os-e55f724c/compras_classificadas.csv',
        card_rules_dir='/home/ubuntu/projects/finance-os-e55f724c/regras/cartoes'
    )
    engine.run_comparison()
    print("Comparativo de cashback gerado com sucesso.")
