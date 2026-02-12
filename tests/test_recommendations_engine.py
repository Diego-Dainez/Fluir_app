"""
Testes unitarios do motor de recomendacoes.
"""
from recommendations_engine import generate_recommendations


def test_retorna_lista():
    """Deve retornar lista de dicionarios."""
    dim_scores = [
        {"dimension_id": "burnout", "status": "red"},
        {"dimension_id": "stress", "status": "red"},
    ]
    recs = generate_recommendations(dim_scores)
    assert isinstance(recs, list)


def test_recomendacao_tem_campos_esperados():
    """Cada recomendacao deve ter dimension_ids, priority, title, description."""
    dim_scores = [{"dimension_id": "burnout", "status": "red"}]
    recs = generate_recommendations(dim_scores)
    for r in recs:
        assert "dimension_ids" in r
        assert "priority" in r
        assert "title" in r
        assert "description" in r
        assert r["priority"] in ("imediata", "curto", "medio")


def test_lista_vazia_quando_tudo_green():
    """Se todas dimensoes green, nao ha recomendacoes."""
    dim_scores = [
        {"dimension_id": "exigencias_quantitativas", "status": "green"},
        {"dimension_id": "ritmo_trabalho", "status": "green"},
    ]
    recs = generate_recommendations(dim_scores)
    assert recs == []
