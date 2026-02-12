"""
Fluir — Motor de Cálculo COPSOQ II
Tercis, scores por dimensão e KPIs agregados.
"""

from copsoq_data import DIMENSIONS

LOWER_TERCILE = 2.33
UPPER_TERCILE = 3.66


def get_status(score: float, dim_type: str) -> str:
    """Retorna 'green', 'yellow' ou 'red' baseado nos tercis."""
    if dim_type == "risk":
        if score < LOWER_TERCILE:
            return "green"
        elif score > UPPER_TERCILE:
            return "red"
        return "yellow"
    else:
        if score > UPPER_TERCILE:
            return "green"
        elif score < LOWER_TERCILE:
            return "red"
        return "yellow"


def calc_dimension_scores(responses: dict) -> list:
    """
    Calcula scores para todas as 26 dimensões.
    responses: {question_id(int): value(int 1-5)}
    Retorna lista de dicts com dados de cada dimensão.
    """
    results = []
    for dim_id, dim in DIMENSIONS.items():
        q_ids = dim["questions"]
        values = [responses.get(q, responses.get(str(q))) for q in q_ids]
        values = [v for v in values if v is not None]
        if not values:
            continue
        score = round(sum(values) / len(values), 2)
        status = get_status(score, dim["type"])
        results.append({
            "dimension_id": dim_id,
            "name": dim["name"],
            "score": score,
            "status": status,
            "type": dim["type"],
            "category": dim["category"],
            "description": dim["description"],
        })
    return results


def calc_kpis(dim_scores: list) -> dict:
    """
    Calcula 4 KPIs a partir dos scores das dimensões.
    Retorna dict com cada KPI contendo value, status e color.
    """
    scores_map = {d["dimension_id"]: d["score"] for d in dim_scores}

    def _avg(ids):
        vals = [scores_map[i] for i in ids if i in scores_map]
        return round(sum(vals) / len(vals), 2) if vals else 3.0

    safety = round(5.0 - _avg(["burnout", "stress", "conflito_trabalho_familia", "inseguranca_laboral"]), 2)
    wellbeing = _avg(["saude_geral", "satisfacao_laboral"])
    support = _avg(["qualidade_lideranca", "apoio_superiores", "comunidade_social", "confianca_vertical"])
    development = _avg(["influencia_trabalho", "possibilidades_desenvolvimento", "significado_trabalho"])

    def _kpi_obj(value, label):
        if value >= UPPER_TERCILE:
            status, color = "Excelente", "green"
        elif value >= LOWER_TERCILE:
            status, color = "Adequado", "yellow"
        else:
            status, color = "Crítico", "red"
        return {"label": label, "value": value, "status": status, "color": color, "percentage": round((value / 5.0) * 100, 1)}

    return {
        "safety_index": _kpi_obj(safety, "Segurança Psicossocial"),
        "wellbeing_index": _kpi_obj(wellbeing, "Bem-Estar"),
        "support_index": _kpi_obj(support, "Apoio Organizacional"),
        "development_index": _kpi_obj(development, "Desenvolvimento"),
    }


def calc_summary(dim_scores: list) -> dict:
    """Resumo geral: contagem de verdes, amarelos, vermelhos."""
    green = sum(1 for d in dim_scores if d["status"] == "green")
    yellow = sum(1 for d in dim_scores if d["status"] == "yellow")
    red = sum(1 for d in dim_scores if d["status"] == "red")
    total = len(dim_scores)
    health = round((green / total) * 100, 1) if total else 0
    return {"green": green, "yellow": yellow, "red": red, "total": total, "health_score": health}
