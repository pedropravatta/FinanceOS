import streamlit as st
import pandas as pd
from pathlib import Path

# Configurações do diretório base
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "compras_comparativo.csv"

st.set_page_config(page_title="FinanceOS - Painel de Decisão", layout="centered")

st.title("FinanceOS - Painel de Tomada de Decisão 💳💰")
st.write("Análise avançada de gastos e inteligência de cashback para cartões de crédito.")

if not CSV_PATH.exists():
    st.warning("⚠️ Arquivo `compras_comparativo.csv` não encontrado.")
    st.info(
        """
        Para gerar os dados comparativos e de recomendação, execute o pipeline completo do FinanceOS a partir do seu terminal:

        ```bash
        python run.py
        ```

        Certifique-se de que a planilha `Contas Pedro.xlsx` esteja na raiz do projeto antes de rodar o pipeline.
        """
    )
else:
    try:
        df = pd.read_csv(CSV_PATH)

        # 1. Validar as colunas básicas esperadas
        required_cols = ["descricao", "valor_total", "categoria", "melhor_cartao", "cashback_melhor_cartao"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        # Encontrar dinamicamente as colunas de cashback de cada cartão
        cashback_cols = [col for col in df.columns if col.startswith("cashback_") and col != "cashback_melhor_cartao"]

        if missing_cols or not cashback_cols:
            st.error("⚠️ Estrutura de dados incompatível detectada em `compras_comparativo.csv`.")

            if missing_cols:
                st.write("**Colunas obrigatórias ausentes:**")
                for col in missing_cols:
                    st.markdown(f"- `{col}`")

            if not cashback_cols:
                st.write("- **Nenhuma coluna de cashback de cartão encontrada** (esperado colunas no padrão `cashback_<NomeDoCartao>`).")

            st.info(
                """
                Por favor, execute o pipeline completo para gerar novamente o arquivo com todas as colunas necessárias:

                ```bash
                python run.py
                ```
                """
            )
        else:
            # Forçar conversão de tipo numérica para valores de transação
            df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce").fillna(0.0)
            df["cashback_melhor_cartao"] = pd.to_numeric(df["cashback_melhor_cartao"], errors="coerce").fillna(0.0)

            # Mapear os nomes reais dos cartões e somar os valores de cashback
            card_sums = {}
            for col in cashback_cols:
                card_name = col.replace("cashback_", "")
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
                card_sums[card_name] = df[col].sum()

            # Organizar o ranking de cartões de forma descendente
            sorted_cards = sorted(card_sums.items(), key=lambda x: x[1], reverse=True)
            ranking = [card for card, _ in sorted_cards]
            best_card = ranking[0]
            best_cashback = card_sums[best_card]
            worst_card = ranking[-1]
            worst_cashback = card_sums[worst_card]

            # Segundo colocado (se houver mais de um cartão)
            second_card = ranking[1] if len(ranking) > 1 else None
            second_cashback = card_sums[second_card] if second_card else 0.0
            diff_to_second = best_cashback - second_cashback

            # ========================
            # 1. Seção "Recomendação"
            # ========================
            st.header("Recomendação")
            recommendation_text = (
                f"Com base no seu histórico financeiro, o cartão **{best_card}** gerou o maior cashback total, "
                f"acumulando **R\\$ {best_cashback:.2f}**. "
            )
            if second_card:
                recommendation_text += (
                    f"Em relação ao segundo colocado (**{second_card}**), a diferença foi de aproximadamente "
                    f"**R\\$ {diff_to_second:.2f}**. "
                )

            recommendation_text += (
                f"Caso você utilize o cartão recomendado em todas as compras futuras, sua economia estimada será maior, "
                f"especialmente em categorias otimizadas."
            )
            st.info(recommendation_text)

            # ========================
            # 2. Tabela Comparativa de Cartões
            # ========================
            st.subheader("Comparativo de Cashback")

            comparison_rows = []
            for card in ranking:
                card_cashback = card_sums[card]
                diff_to_best = best_cashback - card_cashback
                diff_to_worst = card_cashback - worst_cashback

                comparison_rows.append({
                    "Cartão": card,
                    "Cashback Total": card_cashback,
                    "Diferença para o Melhor Cartão": diff_to_best,
                    "Diferença para o Pior Cartão": diff_to_worst
                })

            df_comparison = pd.DataFrame(comparison_rows)
            st.dataframe(
                df_comparison.style.format({
                    "Cashback Total": "R$ {:.2f}",
                    "Diferença para o Melhor Cartão": "R$ {:.2f}",
                    "Diferença para o Pior Cartão": "R$ {:.2f}"
                }),
                use_container_width=True
            )

            # ========================
            # 3. Ranking por Categoria
            # ========================
            st.subheader("Melhor Cartão por Categoria")
            st.write("Saiba qual cartão utilizar especificamente para cada tipo de gasto:")

            category_ranking_rows = []
            grouped_cats = df.groupby("categoria")

            for category, group in grouped_cats:
                cat_card_sums = {}
                for col in cashback_cols:
                    card_name = col.replace("cashback_", "")
                    cat_card_sums[card_name] = group[col].sum()

                best_card_for_cat = max(cat_card_sums, key=cat_card_sums.get)
                best_cashback_for_cat = cat_card_sums[best_card_for_cat]

                category_ranking_rows.append({
                    "Categoria": category,
                    "Melhor cartão": best_card_for_cat,
                    "Cashback obtido": best_cashback_for_cat
                })

            df_category_ranking = pd.DataFrame(category_ranking_rows).sort_values(by="Cashback obtido", ascending=False).reset_index(drop=True)
            st.dataframe(
                df_category_ranking.style.format({
                    "Cashback obtido": "R$ {:.2f}"
                }),
                use_container_width=True
            )

            # ========================
            # 4. Seção "Insights"
            # ========================
            st.header("Insights")

            # Cálculo de estatísticas básicas via Pandas
            cat_spending = df.groupby("categoria")["valor_total"].sum()
            max_spending_cat = cat_spending.idxmax()
            max_spending_val = cat_spending.max()

            cat_cashback = df.groupby("categoria")["cashback_melhor_cartao"].sum()
            max_cashback_cat = cat_cashback.idxmax()
            max_cashback_val = cat_cashback.max()

            total_purchases = len(df)
            average_ticket = df["valor_total"].mean()

            # Encontrar categoria onde trocar o cartão gera maior benefício:
            # (categoria com a maior diferença absoluta entre o melhor e o pior cashback de cartão)
            max_cat_benefit_name = "Nenhuma"
            max_cat_benefit_val = 0.0

            for category, group in grouped_cats:
                cat_card_cashbacks = [group[col].sum() for col in cashback_cols]
                benefit_diff = max(cat_card_cashbacks) - min(cat_card_cashbacks)
                if benefit_diff > max_cat_benefit_val:
                    max_cat_benefit_val = benefit_diff
                    max_cat_benefit_name = category

            # Exibir os insights usando métricas ou bullet points elegantes
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Geral**")
                st.write(f"- 🛒 **Quantidade total de compras:** {total_purchases}")
                st.write(f"- 🏷️ **Ticket médio por compra:** R\\$ {average_ticket:.2f}")
                st.write(f"- 📈 **Categoria com maior gasto:** **{max_spending_cat}** (R\\$ {max_spending_val:.2f})")

            with col2:
                st.write("**Otimização de Cashback**")
                st.write(f"- 💎 **Categoria que mais gera cashback:** **{max_cashback_cat}** (R\\$ {max_cashback_val:.2f})")
                st.write(f"- 🔄 **Maior benefício de troca de cartão:** na categoria **{max_cat_benefit_name}** (ganho potencial adicional de R\\$ {max_cat_benefit_val:.2f})")

            # ========================
            # Detalhes das transações individuais
            # ========================
            st.subheader("Detalhamento de Transações")
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
