"""
Testes unitarios do motor de calculo COPSOQ II.
"""
import pytest
from copsoq_calculator import (
    get_status,
    calc_dimension_scores,
    calc_kpis,
    calc_summary,
    LOWER_TERCILE,
    UPPER_TERCILE,
)


class TestGetStatus:
    """Testes da funcao get_status (tercis: green, yellow, red)."""

    def test_risk_green_abaixo_limite(self):
        assert get_status(2.0, "risk") == "green"

    def test_risk_yellow_no_intervalo(self):
        assert get_status(3.0, "risk") == "yellow"

    def test_risk_red_acima_limite(self):
        assert get_status(4.0, "risk") == "red"

    def test_risk_limite_inferior_exato_amarelo(self):
        """No valor exato do limite inferior (2.33), usa operador < logo cai em yellow."""
        assert get_status(LOWER_TERCILE, "risk") == "yellow"

    def test_risk_limite_superior_exato_amarelo(self):
        """No valor exato do limite superior (3.66), usa operador > logo cai em yellow."""
        assert get_status(UPPER_TERCILE, "risk") == "yellow"

    def test_protective_green_acima_limite(self):
        assert get_status(4.0, "protective") == "green"

    def test_protective_yellow_no_intervalo(self):
        assert get_status(3.0, "protective") == "yellow"

    def test_protective_red_abaixo_limite(self):
        assert get_status(2.0, "protective") == "red"


class TestCalcDimensionScores:
    """Testes do calculo de scores por dimensao."""

    def test_respostas_completas_41_itens(self):
        responses = {i: 3 for i in range(1, 42)}
        scores = calc_dimension_scores(responses)
        assert len(scores) > 0
        for d in scores:
            assert "dimension_id" in d
            assert "name" in d
            assert "score" in d
            assert "status" in d
            assert d["status"] in ("green", "yellow", "red")

    def test_respostas_string_keys(self):
        responses = {str(i): 3 for i in range(1, 42)}
        scores = calc_dimension_scores(responses)
        assert len(scores) > 0

    def test_score_medio_quando_todas_3(self):
        responses = {i: 3 for i in range(1, 42)}
        scores = calc_dimension_scores(responses)
        for d in scores:
            assert d["score"] == 3.0

    def test_score_alto_quando_todas_5(self):
        responses = {i: 5 for i in range(1, 42)}
        scores = calc_dimension_scores(responses)
        for d in scores:
            assert d["score"] >= 4.0


class TestCalcKpis:
    """Testes dos 4 KPIs agregados."""

    def test_retorna_quatro_kpis(self):
        responses = {i: 3 for i in range(1, 42)}
        dim_scores = calc_dimension_scores(responses)
        kpis = calc_kpis(dim_scores)
        assert "safety_index" in kpis
        assert "wellbeing_index" in kpis
        assert "support_index" in kpis
        assert "development_index" in kpis

    def test_kpi_tem_value_label_status_color(self):
        responses = {i: 3 for i in range(1, 42)}
        dim_scores = calc_dimension_scores(responses)
        kpis = calc_kpis(dim_scores)
        for k, v in kpis.items():
            assert "value" in v
            assert "label" in v
            assert "status" in v
            assert "color" in v
            assert "percentage" in v


class TestCalcSummary:
    """Testes do resumo geral (contagem green/yellow/red)."""

    def test_soma_igual_total(self):
        responses = {i: 3 for i in range(1, 42)}
        dim_scores = calc_dimension_scores(responses)
        s = calc_summary(dim_scores)
        assert s["green"] + s["yellow"] + s["red"] == s["total"]

    def test_health_score_percentual(self):
        responses = {i: 3 for i in range(1, 42)}
        dim_scores = calc_dimension_scores(responses)
        s = calc_summary(dim_scores)
        assert 0 <= s["health_score"] <= 100
