"""
Testes do servico de exportacao (Excel, PPT).
"""
import pytest

from export_service import export_pptx


def test_export_pptx_retorna_bytes_nao_vazio():
    """export_pptx deve retornar BytesIO com conteudo."""
    survey = {"company_name": "Empresa Teste"}
    respondents_data = []
    dim_scores = [
        {"name": "Exigencias", "score": 2.5, "status": "yellow", "type": "risk", "category": "Trabalho", "description": ""},
    ]
    kpis = {
        "safety_index": {"label": "Indice Seguranca", "value": 3.2, "status": "Favoravel", "color": "green"},
    }
    summary = {"green": 5, "yellow": 3, "red": 2, "total": 10}
    recommendations = [{"priority": "imediata", "title": "Teste", "description": "Desc"}]
    recommendations_prose = {
        "imediata": "Reunir equipe para diagnostico.",
        "curto_prazo": "Implementar acoes de curto prazo.",
        "medio_prazo": "Acompanhar metricas em 6 meses.",
    }
    buf = export_pptx(
        survey, respondents_data, dim_scores, kpis, summary,
        recommendations, recommendations_prose,
    )
    assert buf is not None
    data = buf.read()
    assert len(data) > 0


def test_export_pptx_arquivo_valido():
    """O conteudo retornado deve ser um PPTX valido (ZIP com assinatura PK)."""
    survey = {"company_name": "Teste"}
    respondents_data = []
    dim_scores = []
    kpis = {}
    summary = {"green": 0, "yellow": 0, "red": 0, "total": 0}
    recommendations = []
    recommendations_prose = {}
    buf = export_pptx(
        survey, respondents_data, dim_scores, kpis, summary,
        recommendations, recommendations_prose,
    )
    data = buf.read()
    assert data[:2] == b"PK", "PPTX e um arquivo ZIP; deve comecar com assinatura PK"
    assert b"[Content_Types].xml" in data or b"ppt/" in data, "PPTX deve conter estrutura OOXML"
