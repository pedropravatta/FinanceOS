import pytest
import pandas as pd
import json
import os
from decision_engine import DecisionEngine

@pytest.fixture
def temp_comparativo_csv(tmpdir):
    data = {
        "descricao": ["Almoço", "Supermercado", "Netflix", "Uber"],
        "valor_total": [100.0, 200.0, 50.0, 30.0],
        "categoria": ["Restaurante", "Mercado", "Assinaturas", "Transporte"],
        "cashback_Nubank": [0.5, 1.0, 0.25, 0.15],
        "cashback_Inter": [5.0, 2.0, 0.5, 0.3],
        "cashback_XP": [0.8, 1.6, 2.5, 0.24],
        "melhor_cartao": ["Inter", "Inter", "XP", "Inter"],
        "cashback_melhor_cartao": [5.0, 2.0, 2.5, 0.3]
    }
    df = pd.DataFrame(data)
    filepath = tmpdir.join("compras_comparativo_test.csv")
    df.to_csv(str(filepath), index=False)
    return str(filepath)

def test_decision_engine_analysis(temp_comparativo_csv):
    engine = DecisionEngine(temp_comparativo_csv)
    report = engine.analyze()

    # Verificar melhor cartão geral
    # Totais: Nubank: 1.9, Inter: 7.8, XP: 5.14
    assert report["melhor_cartao_geral"] == "Inter"
    assert report["ranking_cartoes"] == ["Inter", "XP", "Nubank"]

    # Verificar cashback otimizado total
    # Soma de [5.0, 2.0, 2.5, 0.3] = 9.8
    assert report["cashback_otimizado_total"] == pytest.approx(9.8)

    # Verificar resumo dos cartões
    resumo = report["resumo_cartoes"]
    assert resumo["Inter"]["cashback_total"] == pytest.approx(7.8)
    assert resumo["Nubank"]["cashback_total"] == pytest.approx(1.9)
    assert resumo["XP"]["cashback_total"] == pytest.approx(5.14)

    # Diferença absoluta vs melhor único
    assert resumo["Inter"]["diferenca_absoluta_vs_melhor_unico"] == pytest.approx(0.0)
    assert resumo["XP"]["diferenca_absoluta_vs_melhor_unico"] == pytest.approx(7.8 - 5.14)

    # Diferença absoluta vs otimizado
    assert resumo["Inter"]["diferenca_absoluta_vs_otimizado"] == pytest.approx(9.8 - 7.8)
    assert resumo["Nubank"]["diferenca_absoluta_vs_otimizado"] == pytest.approx(9.8 - 1.9)

    # Verificar melhor cartão por categoria
    best_by_cat = report["melhor_cartao_por_categoria"]
    assert best_by_cat["Restaurante"] == "Inter"
    assert best_by_cat["Assinaturas"] == "XP"

    # Verificar perda potencial por categoria
    losses = report["perda_potencial_por_categoria"]
    # Na categoria Restaurante: otimizado = 5.0, Nubank = 0.5 (perda = 4.5), Inter = 5.0 (perda = 0.0)
    assert losses["Restaurante"]["cashback_otimizado"] == pytest.approx(5.0)
    assert losses["Restaurante"]["perda_Nubank"] == pytest.approx(4.5)
    assert losses["Restaurante"]["perda_Inter"] == pytest.approx(0.0)

def test_decision_engine_save_report(temp_comparativo_csv, tmpdir):
    engine = DecisionEngine(temp_comparativo_csv)
    engine.analyze()
    report_output = tmpdir.join("decision_report_test.json")

    saved_path = engine.save_report(str(report_output))
    assert os.path.exists(saved_path)

    with open(saved_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["melhor_cartao_geral"] == "Inter"
    assert data["cashback_otimizado_total"] == pytest.approx(9.8)
