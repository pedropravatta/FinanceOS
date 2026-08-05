import streamlit as st
import pandas as pd
from pathlib import Path

# Configurações do diretório base
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "compras_comparativo.csv"

st.set_page_config(page_title="FinanceOS - Motor de Cashback", layout="centered")

st.title("FinanceOS - Motor de Cashback 💰")
st.write("Visualize os benefícios e o comparativo de cashback para seus cartões de crédito.")

if not CSV_PATH.exists():
    st.warning("⚠️ Arquivo `compras_comparativo.csv` não encontrado.")
    st.info(
        """
        Para gerar os dados comparativos, execute o pipeline completo do FinanceOS a partir do seu terminal:

        ```bash
        python run.py
        ```

        Certifique-se de que a planilha `Contas Pedro.xlsx` esteja na raiz do projeto antes de rodar o pipeline.
        """
    )
else:
    try:
        df = pd.read_csv(CSV_PATH)

        # Encontrar dinamicamente as colunas de cashback de cada cartão
        cashback_cols = [col for col in df.columns if col.startswith("cashback_") and col != "cashback_melhor_cartao"]

        if not cashback_cols:
            st.error("Nenhuma coluna de cashback de cartão encontrada no arquivo.")
        else:
            # Mapear os nomes reais dos cartões
            card_sums = {}
            for col in cashback_cols:
                card_name = col.replace("cashback_", "")
                card_sums[card_name] = df[col].sum()

            # Organizar o ranking
            df_ranking = pd.DataFrame(
                list(card_sums.items()),
                columns=["Cartão", "Cashback Total (R$)"]
            ).sort_values(by="Cashback Total (R$)", ascending=False).reset_index(drop=True)

            # Melhor cartão individual (se fosse usar apenas um cartão para tudo)
            best_single_card = df_ranking.iloc[0]["Cartão"]
            best_single_cashback = df_ranking.iloc[0]["Cashback Total (R$)"]

            # Cashback otimizado (se usasse o melhor cartão para cada compra)
            optimized_cashback = df["cashback_melhor_cartao"].sum()

            # Exibir métricas principais
            st.subheader("Métricas de Destaque")
            col1, col2, col3 = st.columns(3)

            col1.metric(
                label="Melhor Cartão Geral",
                value=best_single_card
            )
            col2.metric(
                label="Maior Cashback (Único)",
                value=f"R$ {best_single_cashback:.2f}"
            )
            col3.metric(
                label="Cashback Otimizado",
                value=f"R$ {optimized_cashback:.2f}",
                help="Se você usar o melhor cartão para cada categoria de compra individualmente."
            )

            # Exibir ranking completo
            st.subheader("Ranking de Cashback por Cartão")
            st.dataframe(
                df_ranking.style.format({"Cashback Total (R$)": "R$ {:.2f}"}),
                use_container_width=True
            )

            # Exibir transações e o melhor cartão para cada uma
            st.subheader("Detalhamento de Transações")
            st.write("Abaixo estão listadas as transações com a recomendação do melhor cartão para cada gasto:")

            # Selecionar e renomear colunas para exibição amigável
            cols_to_show = ["descricao", "valor_total", "categoria", "melhor_cartao", "cashback_melhor_cartao"]
            df_show = df[cols_to_show].copy()
            df_show.columns = ["Descrição", "Valor (R$)", "Categoria", "Recomendação", "Cashback Gerado (R$)"]

            st.dataframe(
                df_show.style.format({
                    "Valor (R$)": "R$ {:.2f}",
                    "Cashback Gerado (R$)": "R$ {:.2f}"
                }),
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Erro ao carregar ou processar os dados: {e}")
