# Relatório de Enriquecimento Semântico - Sprint 2

Este documento detalha o processo de transformação das descrições brutas em dados financeiros estruturados, atingindo as metas de qualidade estabelecidas.

## 1. Resumo Executivo
A Sprint 2 focou na criação de uma camada semântica robusta, permitindo que o Finance OS entenda a natureza de cada gasto automaticamente.

| Métrica | Resultado Alcançado | Meta |
| :--- | :--- | :--- |
| **Cobertura de Classificação** | **96.88%** | > 95% |
| **Confiança Média** | **96.71%** | N/A |
| **Total de Compras Processadas** | 544 | - |
| **Classificadas Automaticamente** | 527 | - |
| **Necessitam Revisão Manual** | 17 | - |

## 2. Metodologia de Engenharia
Seguindo os princípios de arquitetura modular, o motor de classificação foi construído sobre uma **Base de Conhecimento Externa**:

*   **`palavras.csv`**: Mapeia termos encontrados nas descrições (ex: "uber", "ifood", "pao de acucar") para estabelecimentos padronizados.
*   **`estabelecimentos.csv`**: Define a taxonomia de Categorias e Subcategorias para cada estabelecimento.
*   **Normalização**: Antes da busca, todas as descrições passaram por um processo de limpeza (remoção de acentos, caracteres especiais e padronização de case).

## 3. Taxonomia de Categorias
As transações foram organizadas nas seguintes categorias principais:
*   **Transporte**: Uber, 99, Postos de Combustível.
*   **Mercado**: Supermercados e compras de mantimentos.
*   **Restaurante / Fast Food**: Refeições fora, Delivery e Lanches.
*   **Assinaturas**: Streaming (Netflix, Spotify, HBO) e Serviços Digitais.
*   **Casa**: Aluguel, Condomínio, Energia e Internet.
*   **Lazer**: Cinema, Eventos, Presentes e Bebidas.
*   **Saúde**: Farmácia, Médicos e Dentistas.

## 4. Casos para Revisão Manual
Os 3.12% restantes que não atingiram confiança automática referem-se a termos extremamente genéricos ou ambíguos:
1.  `Óculos` (Pode ser Saúde ou Acessório/Lazer)
2.  `Whey` (Saúde ou Suplementação)
3.  `Guaco` (Saúde ou Restaurante?)
4.  `Diferença Sapato` (Vestuário)
5.  `Corujão` (Lazer ou Restaurante?)

Estes itens estão marcados com `confianca_classificacao = 10` no arquivo `compras_classificadas.csv`.

## 5. Próximos Passos
Com a base enriquecida e categorizada, o Finance OS agora possui inteligência para:
*   Gerar Dashboards por categoria.
*   Analisar evolução de gastos por estabelecimento.
*   Propor metas baseadas em comportamento histórico.

---
*Relatório gerado pelo Motor de Classificação Finance OS - Engenharia de Dados.*
