"""
Fluir — Motor de Recomendações Combinatórias
Gera recomendações priorizadas baseadas em combinações de dimensões.
"""

# ──────────────────────────────────────────────
# RECOMENDAÇÕES INDIVIDUAIS POR DIMENSÃO
# ──────────────────────────────────────────────

INDIVIDUAL_RECOMMENDATIONS = {
    "exigencias_quantitativas": {
        "red": {"title": "Sobrecarga de trabalho crítica", "description": "Redistribuir tarefas e revisar prioridades. Avaliar necessidade de novas contratações. Implementar sistema de gestão de demandas com revisão semanal."},
        "yellow": {"title": "Carga de trabalho em atenção", "description": "Monitorar distribuição de tarefas. Promover reuniões de priorização semanais com as equipes."},
    },
    "ritmo_trabalho": {
        "red": {"title": "Ritmo de trabalho insustentável", "description": "Revisar prazos e metas. Implementar pausas estruturadas. Avaliar automação de processos repetitivos."},
        "yellow": {"title": "Ritmo de trabalho elevado", "description": "Mapear processos para identificar gargalos. Equilibrar picos de demanda com planejamento antecipado."},
    },
    "exigencias_cognitivas": {
        "red": {"title": "Sobrecarga cognitiva", "description": "Reduzir multitarefa. Criar ambientes livres de interrupções. Oferecer suporte para tomada de decisões complexas."},
        "yellow": {"title": "Exigências cognitivas elevadas", "description": "Fornecer ferramentas de apoio à decisão. Promover formação em gestão de prioridades."},
    },
    "exigencias_emocionais": {
        "red": {"title": "Desgaste emocional significativo", "description": "Implementar programa de apoio psicológico. Promover supervisão e espaços de partilha emocional. Avaliar rotação de funções."},
        "yellow": {"title": "Demanda emocional moderada", "description": "Oferecer formação em inteligência emocional. Criar espaços seguros de diálogo."},
    },
    "influencia_trabalho": {
        "red": {"title": "Baixa autonomia no trabalho", "description": "Ampliar participação dos colaboradores nas decisões. Delegar responsabilidades com acompanhamento. Implementar gestão participativa."},
        "yellow": {"title": "Autonomia limitada", "description": "Incentivar sugestões da equipe. Criar canais de participação nas decisões do setor."},
    },
    "possibilidades_desenvolvimento": {
        "red": {"title": "Ausência de desenvolvimento profissional", "description": "Criar plano de desenvolvimento individual (PDI). Investir em formação e capacitação. Implementar programa de mentoria."},
        "yellow": {"title": "Oportunidades de desenvolvimento limitadas", "description": "Mapear competências e lacunas. Promover job rotation e aprendizagem contínua."},
    },
    "significado_trabalho": {
        "red": {"title": "Perda de sentido no trabalho", "description": "Reconectar o trabalho individual ao propósito da organização. Promover storytelling organizacional. Oferecer projetos com impacto visível."},
        "yellow": {"title": "Significado do trabalho em atenção", "description": "Reforçar a missão e valores da organização. Comunicar o impacto do trabalho de cada equipa."},
    },
    "compromisso_trabalho": {
        "red": {"title": "Baixo compromisso organizacional", "description": "Investigar causas de desengajamento. Implementar programa de endomarketing. Fortalecer cultura organizacional."},
        "yellow": {"title": "Compromisso moderado", "description": "Promover eventos de integração. Fortalecer comunicação dos valores organizacionais."},
    },
    "auto_eficacia": {
        "red": {"title": "Baixa auto-eficácia", "description": "Oferecer feedback positivo e construtivo. Criar oportunidades de sucessos progressivos. Investir em coaching."},
        "yellow": {"title": "Auto-eficácia moderada", "description": "Reconhecer conquistas individuais. Promover partilha de boas práticas entre a equipa."},
    },
    "previsibilidade": {
        "red": {"title": "Falta de previsibilidade organizacional", "description": "Implementar comunicação transparente sobre mudanças. Criar calendário de informações. Envolver equipas no planeamento."},
        "yellow": {"title": "Previsibilidade limitada", "description": "Melhorar canais de comunicação interna. Antecipar informações sobre mudanças relevantes."},
    },
    "transparencia_papel": {
        "red": {"title": "Ambiguidade de papéis", "description": "Definir descrições de funções claras. Alinhar expectativas entre chefia e equipa. Realizar reuniões de alinhamento."},
        "yellow": {"title": "Clareza de papel em atenção", "description": "Revisar descrições de funções periodicamente. Promover diálogo sobre expectativas."},
    },
    "recompensas": {
        "red": {"title": "Déficit de reconhecimento", "description": "Implementar programa de reconhecimento estruturado. Treinar lideranças em feedback positivo. Criar rituais de celebração."},
        "yellow": {"title": "Reconhecimento insuficiente", "description": "Ampliar práticas de reconhecimento formal e informal. Valorizar conquistas da equipa."},
    },
    "qualidade_lideranca": {
        "red": {"title": "Déficit na qualidade da liderança", "description": "Investir em programa de desenvolvimento de lideranças. Realizar assessment de competências gerenciais. Promover coaching executivo."},
        "yellow": {"title": "Liderança em desenvolvimento", "description": "Oferecer formação contínua para líderes. Implementar feedback 360° para gestores."},
    },
    "apoio_superiores": {
        "red": {"title": "Falta de apoio da chefia", "description": "Treinar lideranças em escuta ativa e suporte. Implementar reuniões individuais (1:1) regulares. Criar cultura de porta aberta."},
        "yellow": {"title": "Apoio da chefia limitado", "description": "Incentivar reuniões periódicas entre líder e equipa. Fortalecer proximidade com a gestão."},
    },
    "comunidade_social": {
        "red": {"title": "Ambiente social deteriorado", "description": "Implementar programa de team building. Mediar conflitos existentes. Promover atividades de integração social."},
        "yellow": {"title": "Relações sociais em atenção", "description": "Fomentar momentos de convivência. Criar espaços de interação informal."},
    },
    "confianca_vertical": {
        "red": {"title": "Crise de confiança organizacional", "description": "Aumentar transparência nas decisões gerenciais. Cumprir compromissos assumidos. Abrir canais de comunicação bidirecional."},
        "yellow": {"title": "Confiança vertical moderada", "description": "Melhorar comunicação entre gestão e equipas. Demonstrar coerência entre discurso e prática."},
    },
    "justica_respeito": {
        "red": {"title": "Percepção de injustiça organizacional", "description": "Revisar critérios de distribuição de trabalho. Implementar processos transparentes de resolução de conflitos. Garantir equidade."},
        "yellow": {"title": "Justiça em atenção", "description": "Comunicar critérios de decisão com transparência. Criar canal de ouvidoria."},
    },
    "inseguranca_laboral": {
        "red": {"title": "Insegurança laboral elevada", "description": "Comunicar perspetivas organizacionais com transparência. Oferecer suporte em transições. Reforçar estabilidade quando possível."},
        "yellow": {"title": "Insegurança laboral moderada", "description": "Manter comunicação clara sobre a situação da organização. Reforçar compromisso com os colaboradores."},
    },
    "satisfacao_laboral": {
        "red": {"title": "Insatisfação laboral generalizada", "description": "Realizar escuta ativa sobre causas. Implementar melhorias no ambiente e condições. Aplicar pesquisa qualitativa complementar."},
        "yellow": {"title": "Satisfação laboral moderada", "description": "Identificar fatores de satisfação e insatisfação. Implementar melhorias pontuais com impacto visível."},
    },
    "conflito_trabalho_familia": {
        "red": {"title": "Conflito trabalho-família crítico", "description": "Implementar políticas de flexibilidade (horários, teletrabalho). Revisar carga horária. Respeitar limites entre trabalho e vida pessoal."},
        "yellow": {"title": "Conflito trabalho-família moderado", "description": "Avaliar possibilidade de horários flexíveis. Promover cultura de respeito ao tempo pessoal."},
    },
    "saude_geral": {
        "red": {"title": "Saúde geral comprometida", "description": "Implementar programa de qualidade de vida. Oferecer avaliação de saúde periódica. Promover hábitos saudáveis no trabalho."},
        "yellow": {"title": "Saúde geral em atenção", "description": "Incentivar atividade física e alimentação saudável. Oferecer ginástica laboral."},
    },
    "problemas_dormir": {
        "red": {"title": "Distúrbios de sono significativos", "description": "Avaliar fatores laborais que afetam o sono (turnos, stress). Oferecer programa de higiene do sono. Encaminhar casos graves para acompanhamento."},
        "yellow": {"title": "Qualidade do sono em atenção", "description": "Orientar sobre higiene do sono. Avaliar impacto da carga de trabalho nos horários de descanso."},
    },
    "burnout": {
        "red": {"title": "Burnout — Intervenção urgente", "description": "Reduzir carga de trabalho imediatamente. Implementar programa de recuperação. Oferecer suporte psicológico. Avaliar causas sistêmicas."},
        "yellow": {"title": "Sinais de esgotamento", "description": "Monitorar indicadores de exaustão. Promover momentos de recuperação. Incentivar uso de férias e folgas."},
    },
    "stress": {
        "red": {"title": "Níveis de stress críticos", "description": "Implementar programa de gestão do stress. Oferecer técnicas de relaxamento e mindfulness. Avaliar e reduzir fontes de pressão."},
        "yellow": {"title": "Stress moderado", "description": "Promover técnicas de gestão do stress. Avaliar picos de pressão e seus gatilhos."},
    },
    "sintomas_depressivos": {
        "red": {"title": "Sintomas depressivos — Atenção especial", "description": "Encaminhar para apoio psicológico especializado. Avaliar ambiente de trabalho como fator contribuinte. Oferecer suporte emocional."},
        "yellow": {"title": "Indicadores de tristeza", "description": "Fortalecer suporte social no trabalho. Monitorar e oferecer canais de acolhimento."},
    },
    "comportamentos_ofensivos": {
        "red": {"title": "Comportamentos ofensivos — Intervenção imediata", "description": "Investigar situações reportadas. Implementar política de tolerância zero. Criar canal seguro de denúncia. Aplicar medidas disciplinares quando necessário."},
        "yellow": {"title": "Sinais de comportamentos inadequados", "description": "Reforçar código de conduta. Promover formação sobre respeito e diversidade. Monitorar clima."},
    },
}

# ──────────────────────────────────────────────
# RECOMENDAÇÕES COMBINATÓRIAS
# ──────────────────────────────────────────────

COMBO_RULES = [
    # (dimensões necessárias em RED, prioridade, título, descrição)
    {
        "dimensions": ["burnout", "stress", "conflito_trabalho_familia"],
        "min_red": 3,
        "priority": "imediata",
        "title": "[URGENTE] Risco sistêmico de esgotamento coletivo",
        "description": "A combinação de burnout, stress e conflito trabalho/família em níveis críticos indica risco de adoecimento coletivo. Recomenda-se: intervenção sistêmica urgente com redução de carga, programa de recuperação, política de flexibilidade e suporte psicológico imediato."
    },
    {
        "dimensions": ["burnout", "stress"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[ATENCAO] Esgotamento e stress combinados",
        "description": "Burnout e stress em níveis elevados simultaneamente exigem ação imediata: redução de pressão, programa de gestão do stress, avaliação de cargas de trabalho e oferta de suporte emocional."
    },
    {
        "dimensions": ["burnout", "sintomas_depressivos"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[URGENTE] Risco de afastamento por saúde mental",
        "description": "Burnout associado a sintomas depressivos indica risco elevado de afastamentos. Encaminhar para suporte psicológico, avaliar causas organizacionais e implementar programa de saúde mental."
    },
    {
        "dimensions": ["qualidade_lideranca", "apoio_superiores"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[ATENCAO] Déficit de liderança e suporte",
        "description": "Liderança fraca combinada com falta de apoio dos superiores compromete toda a estrutura organizacional. Investir urgentemente em desenvolvimento de lideranças, coaching e reestruturação de gestão."
    },
    {
        "dimensions": ["qualidade_lideranca", "confianca_vertical", "justica_respeito"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[URGENTE] Crise de governança organizacional",
        "description": "Déficits em liderança, confiança e justiça indicam crise de governança. Necessária intervenção na cultura organizacional: transparência, equidade nos processos e desenvolvimento de lideranças éticas."
    },
    {
        "dimensions": ["recompensas", "justica_respeito", "confianca_vertical"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[ATENCAO] Percepção de injustiça sistêmica",
        "description": "Falta de reconhecimento combinada com injustiça e desconfiança gera desengajamento profundo. Revisar políticas de reconhecimento, criar processos transparentes e reconstruir confiança."
    },
    {
        "dimensions": ["exigencias_quantitativas", "ritmo_trabalho", "conflito_trabalho_familia"],
        "min_red": 2,
        "priority": "curto",
        "title": "[ATENCAO] Sobrecarga invadindo a vida pessoal",
        "description": "Excesso de demandas e ritmo acelerado estão comprometendo a vida pessoal. Revisar metas e prazos, implementar política de desconexão digital e avaliar redistribuição de tarefas."
    },
    {
        "dimensions": ["influencia_trabalho", "possibilidades_desenvolvimento","significado_trabalho"],
        "min_red": 2,
        "priority": "curto",
        "title": "[ATENCAO] Desengajamento por falta de propósito e autonomia",
        "description": "Baixa autonomia, poucas oportunidades e perda de sentido indicam risco de desengajamento. Implementar gestão participativa, planos de desenvolvimento e reconexão com o propósito organizacional."
    },
    {
        "dimensions": ["inseguranca_laboral", "stress", "satisfacao_laboral"],
        "min_red": 2,
        "priority": "curto",
        "title": "[ATENCAO] Instabilidade gerando ansiedade e insatisfação",
        "description": "Insegurança laboral combinada com stress e insatisfação requer comunicação transparente sobre o futuro da organização, suporte emocional e programas de retenção."
    },
    {
        "dimensions": ["comunidade_social", "comportamentos_ofensivos"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[URGENTE] Ambiente de trabalho tóxico",
        "description": "Relações sociais deterioradas com presença de comportamentos ofensivos indicam ambiente tóxico. Intervenção imediata: investigação, mediação, aplicação de código de conduta e canal de denúncia."
    },
    {
        "dimensions": ["saude_geral", "problemas_dormir", "burnout"],
        "min_red": 2,
        "priority": "imediata",
        "title": "[URGENTE] Saúde física comprometida pelo trabalho",
        "description": "Saúde geral, sono e burnout em níveis críticos sugerem que o trabalho está adoecendo os colaboradores. Programa de saúde ocupacional integral, revisão de condições de trabalho e suporte médico."
    },
]


def generate_recommendations(dim_scores: list) -> list:
    """
    Gera lista de recomendações priorizadas.
    Combina regras combinatórias + individuais.
    """
    status_map = {d["dimension_id"]: d["status"] for d in dim_scores}
    recommendations = []
    used_dims = set()

    # 1) Regras combinatórias
    for rule in COMBO_RULES:
        red_count = sum(1 for d in rule["dimensions"] if status_map.get(d) == "red")
        if red_count >= rule["min_red"]:
            recommendations.append({
                "dimension_ids": ",".join(rule["dimensions"]),
                "priority": rule["priority"],
                "title": rule["title"],
                "description": rule["description"],
                "is_custom": False,
            })
            used_dims.update(rule["dimensions"])

    # 2) Recomendações individuais (dimensões não cobertas por combos)
    priority_order = {"red": "curto", "yellow": "medio"}
    for d in dim_scores:
        dim_id = d["dimension_id"]
        status = d["status"]
        if status == "green":
            continue
        if dim_id in used_dims and status == "red":
            continue  # already covered by combo
        if dim_id in INDIVIDUAL_RECOMMENDATIONS and status in INDIVIDUAL_RECOMMENDATIONS[dim_id]:
            rec = INDIVIDUAL_RECOMMENDATIONS[dim_id][status]
            recommendations.append({
                "dimension_ids": dim_id,
                "priority": priority_order.get(status, "medio"),
                "title": rec["title"],
                "description": rec["description"],
                "is_custom": False,
            })

    # 3) Ordenar por prioridade
    priority_rank = {"imediata": 0, "curto": 1, "medio": 2}
    recommendations.sort(key=lambda r: priority_rank.get(r["priority"], 3))

    return recommendations
