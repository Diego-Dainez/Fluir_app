import json
import os
from typing import Dict, List, Literal, TypedDict


class RecommendationItem(TypedDict, total=False):
    """Tipo simples para representar uma recomendacao estruturada vinda do motor existente.

    Esperado (mas nao obrigatorio) que cada item tenha:
    - id: identificador interno
    - priority: 'imediata', 'curto_prazo' ou 'medio_prazo'
    - title: titulo sintetico
    - description: descricao em texto corrido
    """

    id: int
    priority: str
    title: str
    description: str


PriorityKey = Literal["imediata", "curto_prazo", "medio_prazo"]


def _group_by_priority(recommendations: List[RecommendationItem]) -> Dict[PriorityKey, List[RecommendationItem]]:
    """Agrupa as recomendacoes por prazo de aplicacao, padronizando as chaves.

    Caso alguma recomendacao venha com um valor de prioridade inesperado,
    ela sera tratada como 'medio_prazo' para nao ser perdida.
    """
    grouped: Dict[PriorityKey, List[RecommendationItem]] = {
        "imediata": [],
        "curto_prazo": [],
        "medio_prazo": [],
    }

    for rec in recommendations or []:
        raw_priority = (rec.get("priority") or "").lower()

        if "imediat" in raw_priority:
            key: PriorityKey = "imediata"
        elif "curto" in raw_priority:
            key = "curto_prazo"
        elif "medio" in raw_priority or "médio" in raw_priority:
            key = "medio_prazo"
        else:
            # Fallback seguro: se o backend nao marcou a prioridade corretamente,
            # assumimos medio prazo para nao perder a recomendacao.
            key = "medio_prazo"

        grouped[key].append(rec)

    return grouped


def _build_prompt(grouped: Dict[PriorityKey, List[RecommendationItem]]) -> str:
    """Monta o texto de entrada para o Gemini em PT-BR, com orientacoes claras.

    Importante: o prompt explica exatamente o formato de saida desejado (JSON),
    para que o backend possa fazer o parse de forma robusta.
    """
    lines: List[str] = []

    lines.append(
        (
            "Voce e uma psicologa organizacional da empresa Fluir, especializada em saude mental "
            "e clima no trabalho. A seguir, recebera um conjunto de recomendacoes estruturadas, "
            "ja analisadas pelo motor da pesquisa, separadas por prazo de aplicacao "
            "(imediata, curto prazo, medio prazo)."
        )
    )
    lines.append("")
    lines.append(
        "Seu objetivo e transformar essas recomendacoes em um texto corrido, consultivo, "
        "em portugues do Brasil, como se estivesse orientando a lideranca da empresa."
    )
    lines.append(
        "Evite listas numeradas ou marcadores; escreva em paragrafo(s) corrido(s), com tom profissional, "
        "acolhedor e objetivo, explicando o porque das acoes e como podem ser implementadas."
    )
    lines.append("")
    lines.append(
        "IMPORTANTE: responda EXCLUSIVAMENTE em JSON valido, no seguinte formato exato (sem comentarios):"
    )
    lines.append(
        '{"imediata": "<texto corrido para acoes imediatas>", '
        '"curto_prazo": "<texto corrido para curto prazo>", '
        '"medio_prazo": "<texto corrido para medio prazo>"}'
    )
    lines.append("")
    lines.append("Abaixo estao as recomendacoes estruturadas:")

    def _section(title: str, key: PriorityKey) -> None:
        items = grouped.get(key) or []
        lines.append("")
        lines.append(f"[{title}]")
        if not items:
            lines.append("Nenhuma recomendacao especifica para este prazo.")
            return
        for idx, rec in enumerate(items, start=1):
            rec_title = rec.get("title") or ""
            rec_desc = rec.get("description") or ""
            lines.append(f"{idx}. Titulo: {rec_title}")
            lines.append(f"   Descricao: {rec_desc}")

    _section("Acoes de aplicacao imediata", "imediata")
    _section("Acoes de curto prazo", "curto_prazo")
    _section("Acoes de medio prazo", "medio_prazo")

    return "\n".join(lines)


def _fallback_prose(grouped: Dict[PriorityKey, List[RecommendationItem]]) -> Dict[PriorityKey, str]:
    """Gera um texto corrido simples quando o Gemini nao puder ser usado.

    Este fallback garante que o painel admin nunca fique em branco, mesmo que
    a API de IA esteja indisponivel ou mal configurada.
    """
    result: Dict[PriorityKey, str] = {
        "imediata": "",
        "curto_prazo": "",
        "medio_prazo": "",
    }

    templates: Dict[PriorityKey, str] = {
        "imediata": (
            "Como prioridades imediatas, recomenda-se concentrar esforcos nas seguintes frentes: {acoes}. "
            "Essas intervencoes visam conter riscos mais urgentes e criar condicoes minimas de seguranca "
            "psicologica e organizacao do trabalho."
        ),
        "curto_prazo": (
            "No curto prazo, sugere-se aprofundar as iniciativas voltadas a {acoes}, estruturando planos "
            "de acao claros, com responsabilidades, prazos e indicadores de acompanhamento."
        ),
        "medio_prazo": (
            "Em uma perspectiva de medio prazo, e importante consolidar uma agenda de desenvolvimento "
            "organizacional focada em {acoes}, de forma a sustentar as mudancas e fortalecer a cultura "
            "da empresa ao longo do tempo."
        ),
    }

    for key, items in grouped.items():
        if not items:
            continue
        # Gera uma frase simples concatenando titulos e, se houver, descricoes.
        partes: List[str] = []
        for rec in items:
            title = (rec.get("title") or "").strip()
            desc = (rec.get("description") or "").strip()
            if title and desc:
                partes.append(f"{title.lower()}: {desc}")
            elif title:
                partes.append(title.lower())
            elif desc:
                partes.append(desc)

        if not partes:
            continue

        joined = "; ".join(partes)
        template = templates[key]
        result[key] = template.format(acoes=joined)

    return result


def generate_recommendations_prose(
    recommendations: List[RecommendationItem],
) -> Dict[PriorityKey, str]:
    """Gera texto corrido de recomendacoes usando Google Gemini, com fallback seguro.

    - Nao faz nenhuma chamada se nao houver recomendacoes.
    - Se a chave FLUIR_GEMINI_API_KEY nao estiver configurada, utiliza apenas o fallback.
    - Se ocorrer qualquer erro na API ou no parse do JSON, retorna o fallback.
    """
    grouped = _group_by_priority(recommendations or [])

    # Se nao ha nenhuma recomendacao em nenhum prazo, nao ha o que gerar.
    if not any(grouped.values()):
        return {
            "imediata": "",
            "curto_prazo": "",
            "medio_prazo": "",
        }

    api_key = os.getenv("FLUIR_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # Sem chave configurada, nao tentamos chamar a API externa.
        return _fallback_prose(grouped)

    prompt = _build_prompt(grouped)

    try:
        # Import lazily para evitar quebrar o import do projeto
        # caso a dependencia ainda nao tenha sido instalada.
        from google import genai  # type: ignore

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        raw_text = (response.text or "").strip()
        if not raw_text:
            return _fallback_prose(grouped)

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # Alguns modelos devolvem JSON envolto em markdown (```json ... ```).
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                # remove possivel prefixo "json" na primeira linha
                cleaned = "\n".join(
                    line for line in cleaned.splitlines() if not line.lstrip().lower().startswith("json")
                ).strip()
            try:
                data = json.loads(cleaned)
            except Exception:
                return _fallback_prose(grouped)

        # Monta estrutura final garantindo todas as chaves.
        result: Dict[PriorityKey, str] = {
            "imediata": str(data.get("imediata", "")).strip(),
            "curto_prazo": str(data.get("curto_prazo", "")).strip(),
            "medio_prazo": str(data.get("medio_prazo", "")).strip(),
        }
        return result

    except Exception:
        # Qualquer problema (rede, autenticacao, mudanca de API) cai no fallback.
        return _fallback_prose(grouped)

