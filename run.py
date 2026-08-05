#!/usr/bin/env python3
import sys
from pathlib import Path

# Adiciona o diretório 'src' ao PATH do sistema para importações corretas
BASE_DIR = Path(__file__).resolve().parent
src_dir = BASE_DIR / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from extract_pipeline import FinanceExtractor
    from validate_ingestion import IngestionValidator
    from sprint2_step1_normalization import run_saneamento
    from sprint2_step2_kb_generator import generate_kb_suggestions
    from sprint2_step3_classifier import run_classifier
    from beneficios import BenefitsEngine
except ImportError as e:
    print(f"Erro ao importar módulos do diretório 'src': {e}")
    sys.exit(1)

def main():
    print("=" * 60)
    print("              INICIANDO PIPELINE FINANCEOS              ")
    print("=" * 60)

    # Verificar se a planilha de entrada existe
    excel_path = BASE_DIR / 'Contas Pedro.xlsx'
    if not excel_path.exists():
        print(f"\n[Aviso/Erro] Arquivo de entrada '{excel_path.name}' não encontrado na raiz do projeto.")
        print("Para rodar o pipeline completo a partir do zero, certifique-se de que")
        print("o arquivo 'Contas Pedro.xlsx' esteja presente no diretório raiz do projeto.\n")
        print("Encerrando execução.")
        sys.exit(1)

    try:
        # Etapa 1: Ingestão de dados (Extração)
        print("\n[Etapa 1/6] Executando extração de dados (extract_pipeline)...")
        extractor = FinanceExtractor(excel_path)
        extractor.run()
        print(" -> Sucesso: Dados extraídos para 'compras_raw.csv' e relatório gerado.")

        # Etapa 2: Validação da ingestão
        print("\n[Etapa 2/6] Validando dados ingeridos (validate_ingestion)...")
        raw_csv_path = BASE_DIR / 'compras_raw.csv'
        validator = IngestionValidator(excel_path, raw_csv_path)
        validator.run_validation()
        print(" -> Sucesso: Validação concluída. Planilha 'validacao_ingestao.xlsx' gerada.")

        # Etapa 3: Saneamento e Normalização
        print("\n[Etapa 3/6] Saneando e normalizando dados (sprint2_step1_normalization)...")
        run_saneamento()
        print(" -> Sucesso: Dados limpos e salvos em 'compras_saneada.csv'.")

        # Etapa 4: Geração da Base de Conhecimento
        print("\n[Etapa 4/6] Gerando base de conhecimento (sprint2_step2_kb_generator)...")
        generate_kb_suggestions()
        print(" -> Sucesso: Dicionários 'palavras.csv' e 'estabelecimentos.csv' gerados.")

        # Etapa 5: Classificação Semântica
        print("\n[Etapa 5/6] Executando classificador semântico (sprint2_step3_classifier)...")
        run_classifier()
        print(" -> Sucesso: Compras classificadas salvas em 'compras_classificadas.csv'.")

        # Etapa 6: Motor de Cashback e Comparação de Benefícios
        print("\n[Etapa 6/6] Calculando cashback e comparando benefícios (beneficios)...")
        engine = BenefitsEngine(
            classified_data_path=BASE_DIR / 'compras_classificadas.csv',
            card_rules_dir=BASE_DIR / 'rules'
        )
        engine.run_comparison()
        print(" -> Sucesso: Comparativo de cashback gerado em 'compras_comparativo.csv'.")

        print("\n" + "=" * 60)
        print("        PIPELINE FINANCEOS EXECUTADO COM SUCESSO!        ")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n[ERRO] Ocorreu uma falha inesperada durante a execução do pipeline:")
        print(f" -> {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
