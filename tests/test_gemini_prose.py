"""
Testes do servico de prosa de recomendacoes (fallback quando Gemini nao esta configurado).
"""
import os
import pytest

# Garante que nao ha chave de API para forcar o fallback
@pytest.fixture(autouse=True)
def clear_gemini_key(monkeypatch):
    """Remove chaves de API para que os testes usem o fallback."""
    monkeypatch.delenv("FLUIR_GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)


def test_fallback_quando_sem_chave():
    """Sem FLUIR_GEMINI_API_KEY, deve retornar prosa gerada pelo fallback."""
    from gemini_prose_service import generate_recommendations_prose

    recs = [
        {"priority": "imediata", "title": "Acao Urgente", "description": "Fazer X e Y."},
        {"priority": "curto", "title": "Curto Prazo", "description": "Planejar Z."},
    ]
    result = generate_recommendations_prose(recs)
    assert "imediata" in result
    assert "curto_prazo" in result
    assert "medio_prazo" in result
    assert len(result["imediata"]) > 0
    assert "acao urgente" in result["imediata"].lower() or "urgente" in result["imediata"].lower()


def test_retorno_vazio_quando_sem_recomendacoes():
    """Sem recomendacoes, retorna dicionario com strings vazias."""
    from gemini_prose_service import generate_recommendations_prose

    result = generate_recommendations_prose([])
    assert result == {"imediata": "", "curto_prazo": "", "medio_prazo": ""}


def test_group_by_priority_medio():
    """Recomendacoes com prioridade 'medio' sao agrupadas corretamente."""
    from gemini_prose_service import generate_recommendations_prose

    recs = [{"priority": "medio", "title": "Médio Prazo", "description": "Desc."}]
    result = generate_recommendations_prose(recs)
    assert len(result["medio_prazo"]) > 0
