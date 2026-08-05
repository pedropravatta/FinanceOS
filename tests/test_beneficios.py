import pytest
import pandas as pd
import json
import os
from beneficios import BenefitsEngine

# Setup para os testes
@pytest.fixture(scope="module")
def setup_test_environment(tmpdir_factory):
    # Criar diretório temporário para as regras dos cartões
    rules_dir = tmpdir_factory.mktemp("regras_cartoes_test")
    
    # Criar arquivos de configuração de cartões de teste
    nubank_config = {
        "nome": "Nubank",
        "cashback": {
            "geral": 0.005,
            "categorias": {}
        }
    }
    inter_config = {
        "nome": "Inter",
        "cashback": {
            "geral": 0.01,
            "categorias": {
                "Restaurante": 0.05,
                "Delivery": 0.05
            }
        }
    }
    xp_config = {
        "nome": "XP",
        "cashback": {
            "geral": 0.008,
            "categorias": {
                "Streaming": 0.05,
                "Lazer": 0.03
            }
        }
    }

    with open(os.path.join(rules_dir, "nubank.json"), "w") as f:
        json.dump(nubank_config, f)
    with open(os.path.join(rules_dir, "inter.json"), "w") as f:
        json.dump(inter_config, f)
    with open(os.path.join(rules_dir, "xp.json"), "w") as f:
        json.dump(xp_config, f)

    # Criar um DataFrame de compras classificadas para teste
    test_data = {
        "descricao": [
            "Almoço Restaurante", 
            "Supermercado", 
            "Netflix Assinatura", 
            "Uber Viagem", 
            "Cinema Ingresso",
            "Farmácia"
        ],
        "descricao_normalizada": [
            "almoco restaurante", 
            "supermercado", 
            "netflix assinatura", 
            "uber viagem", 
            "cinema ingresso",
            "farmacia"
        ],
        "valor_total": [100.0, 200.0, 50.0, 30.0, 80.0, 40.0],
        "categoria": [
            "Restaurante", 
            "Mercado", 
            "Assinaturas", 
            "Transporte", 
            "Lazer",
            "Saúde"
        ],
        "subcategoria": [
            "Geral", 
            "Supermercado", 
            "Streaming", 
            "Uber", 
            "Geral",
            "Farmácia"
        ],
        "confianca_classificacao": [100, 100, 100, 100, 100, 100]
    }
    df_classified_test = pd.DataFrame(test_data)
    classified_data_path = tmpdir_factory.mktemp("data").join("compras_classificadas_test.csv")
    df_classified_test.to_csv(str(classified_data_path), index=False)

    return str(classified_data_path), str(rules_dir)

# Testes
def test_cashback_geral(setup_test_environment):
    classified_data_path, rules_dir = setup_test_environment
    engine = BenefitsEngine(classified_data_path, rules_dir)
    df_result = engine.run_comparison()

    # Testar cashback geral para Nubank (0.5%)
    # Supermercado (200.0) * 0.005 = 1.0
    assert df_result.loc[df_result["descricao"] == "Supermercado", "cashback_Nubank"].iloc[0] == pytest.approx(1.0)
    # Farmácia (40.0) * 0.005 = 0.2
    assert df_result.loc[df_result["descricao"] == "Farmácia", "cashback_Nubank"].iloc[0] == pytest.approx(0.2)

def test_cashback_categoria_bonificada(setup_test_environment):
    classified_data_path, rules_dir = setup_test_environment
    engine = BenefitsEngine(classified_data_path, rules_dir)
    df_result = engine.run_comparison()

    # Testar cashback bonificado para Inter (Restaurante 5%)
    # Almoço Restaurante (100.0) * 0.05 = 5.0
    assert df_result.loc[df_result["descricao"] == "Almoço Restaurante", "cashback_Inter"].iloc[0] == pytest.approx(5.0)
    
    # Testar cashback bonificado para XP (Streaming 5%)
    # Netflix Assinatura (50.0) * 0.05 = 2.5
    assert df_result.loc[df_result["descricao"] == "Netflix Assinatura", "cashback_XP"].iloc[0] == pytest.approx(2.5)

def test_cashback_categoria_sem_bonus(setup_test_environment):
    classified_data_path, rules_dir = setup_test_environment
    engine = BenefitsEngine(classified_data_path, rules_dir)
    df_result = engine.run_comparison()

    # Inter não tem bônus para Mercado, deve usar o geral de 1%
    # Supermercado (200.0) * 0.01 = 2.0
    assert df_result.loc[df_result["descricao"] == "Supermercado", "cashback_Inter"].iloc[0] == pytest.approx(2.0)
    
    # XP não tem bônus para Restaurante, deve usar o geral de 0.8%
    # Almoço Restaurante (100.0) * 0.008 = 0.8
    assert df_result.loc[df_result["descricao"] == "Almoço Restaurante", "cashback_XP"].iloc[0] == pytest.approx(0.8)

def test_comparacao_multiplos_cartoes(setup_test_environment):
    classified_data_path, rules_dir = setup_test_environment
    engine = BenefitsEngine(classified_data_path, rules_dir)
    df_result = engine.run_comparison()

    # Almoço Restaurante (100.0):
    # Nubank: 100 * 0.005 = 0.5
    # Inter: 100 * 0.05 = 5.0 (melhor)
    # XP: 100 * 0.008 = 0.8
    assert df_result.loc[df_result["descricao"] == "Almoço Restaurante", "melhor_cartao"].iloc[0] == "Inter"
    assert df_result.loc[df_result["descricao"] == "Almoço Restaurante", "cashback_melhor_cartao"].iloc[0] == pytest.approx(5.0)

    # Supermercado (200.0):
    # Nubank: 200 * 0.005 = 1.0
    # Inter: 200 * 0.01 = 2.0 (melhor)
    # XP: 200 * 0.008 = 1.6
    assert df_result.loc[df_result["descricao"] == "Supermercado", "melhor_cartao"].iloc[0] == "Inter"
    assert df_result.loc[df_result["descricao"] == "Supermercado", "cashback_melhor_cartao"].iloc[0] == pytest.approx(2.0)

    # Netflix Assinatura (50.0):
    # Nubank: 50 * 0.005 = 0.25
    # Inter: 50 * 0.01 = 0.5
    # XP: 50 * 0.05 = 2.5 (melhor)
    assert df_result.loc[df_result["descricao"] == "Netflix Assinatura", "melhor_cartao"].iloc[0] == "XP"
    assert df_result.loc[df_result["descricao"] == "Netflix Assinatura", "cashback_melhor_cartao"].iloc[0] == pytest.approx(2.5)

    # Uber Viagem (30.0):
    # Nubank: 30 * 0.005 = 0.15
    # Inter: 30 * 0.01 = 0.3 (melhor)
    # XP: 30 * 0.008 = 0.24
    assert df_result.loc[df_result["descricao"] == "Uber Viagem", "melhor_cartao"].iloc[0] == "Inter"
    assert df_result.loc[df_result["descricao"] == "Uber Viagem", "cashback_melhor_cartao"].iloc[0] == pytest.approx(0.3)

    # Cinema Ingresso (80.0):
    # Nubank: 80 * 0.005 = 0.4
    # Inter: 80 * 0.01 = 0.8
    # XP: 80 * 0.03 = 2.4 (melhor, Lazer bonificado)
    assert df_result.loc[df_result["descricao"] == "Cinema Ingresso", "melhor_cartao"].iloc[0] == "XP"
    assert df_result.loc[df_result["descricao"] == "Cinema Ingresso", "cashback_melhor_cartao"].iloc[0] == pytest.approx(2.4)

    # Farmácia (40.0):
    # Nubank: 40 * 0.005 = 0.2
    # Inter: 40 * 0.01 = 0.4 (melhor)
    # XP: 40 * 0.008 = 0.32
    assert df_result.loc[df_result["descricao"] == "Farmácia", "melhor_cartao"].iloc[0] == "Inter"
    assert df_result.loc[df_result["descricao"] == "Farmácia", "cashback_melhor_cartao"].iloc[0] == pytest.approx(0.4)
