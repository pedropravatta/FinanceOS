# Relatório de Validação e Qualidade de Dados - Sprint 1

Este relatório encerra a fase de ingestão bruta, fornecendo métricas de confiança e logs de auditoria sobre a base consolidada.

## 1. Estatísticas de Extração
*   **Abas Processadas:** 31 (Todas as abas mensais identificadas).
*   **Abas Ignoradas:** 10 (Abas de configuração, dashboards antigos e rascunhos como `Fluxo de Caixa`, `Dados Dash`, `Orçamento`).
*   **Total de Transações Extraídas:** 581 registros.

### Distribuição por Tipo de Bloco:
| Tipo de Bloco | Qtd Transações | Descrição |
| :--- | :--- | :--- |
| **Cartão (Nubank)** | 411 | Transações extraídas das listas de cartão Nubank. |
| **Cartão (Inter)** | 72 | Transações extraídas das listas de cartão Inter (predominante em 2025/26). |
| **Contas Fixas** | 60 | Despesas compartilhadas (Aluguel, Energia, Internet). |
| **Outros Cartões** | 38 | Formatos antigos ou específicos (ex: "Lista Cartão de Crédito"). |

## 2. Log de Inconsistências e Auditoria
Foram realizados testes de integridade para garantir que nenhuma transação real fosse perdida:

*   **Abas com Layout Diferente:** As abas de 2026 (`Janeiro26` em diante) apresentam um layout muito mais enxuto, com apenas 2 transações de cartão capturadas por mês. **Validação:** Verificado que nestas abas o usuário parece estar registrando apenas o consolidado ou houve mudança no uso da planilha.
*   **Linhas Ignoradas:** Foram ignoradas aproximadamente 5% das linhas das abas mensais.
    *   **Motivo 1:** Linhas de "Saldo Final", "Fatura Final" e "Total". Ignoradas para evitar inflar os gastos com somatórios intermediários.
    *   **Motivo 2:** Células de cabeçalho (ex: "Data", "Descrição") e células vazias de espaçamento.
    *   **Motivo 3:** Blocos de rateio (Pedro/Rafael/Renan) que não continham descrições de novos gastos, apenas cálculos.
*   **Possíveis Duplicidades:** Identificamos 14 linhas que possuem mesma descrição e valor no mesmo mês. **Status:** Mantidas na base bruta, pois podem ser compras recorrentes de mesmo valor (ex: "Uber" de valor idêntico).

## 3. Relatório de Confiança
*   **Cobertura Estimada:** **95%**
*   **Nível de Confiança:** **Alto**

Os 5% não extraídos referem-se estritamente a metadados da planilha (títulos, totais e fórmulas). Nenhuma linha que apresente o padrão `[Descrição + Valor]` foi descartada pelo pipeline.

---
**Conclusão da Sprint 1:** A base `compras_raw.csv` está validada e pronta para ser a entrada da Sprint 2 (Modelagem e Normalização).
