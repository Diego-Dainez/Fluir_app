"""
Fluir — Dados do COPSOQ II (Versão Curta Portuguesa)
41 questões, 26 dimensões, 8 categorias visuais
"""

# ===== CATEGORIAS VISUAIS (8 páginas do questionário) =====
CATEGORIES = [
    {
        "id": "exigencias",
        "name": "Exigencias do Trabalho",
        "icon": "",
        "description": "Avalie a intensidade e frequencia das demandas no seu dia a dia.",
        "color": "#7A6B8A",
        "questions": [1, 2, 3, 4, 5, 6],
    },
    {
        "id": "autonomia",
        "name": "Autonomia e Desenvolvimento",
        "icon": "",
        "description": "Sobre as oportunidades de crescimento e influencia no seu trabalho.",
        "color": "#6B82A8",
        "questions": [7, 8, 9],
    },
    {
        "id": "informacao",
        "name": "Informacao e Clareza",
        "icon": "",
        "description": "Sobre a transparencia e clareza no seu ambiente de trabalho.",
        "color": "#8FB09A",
        "questions": [10, 11, 12],
    },
    {
        "id": "reconhecimento",
        "name": "Reconhecimento e Apoio",
        "icon": "",
        "description": "Sobre o reconhecimento e apoio que recebe no trabalho.",
        "color": "#C4A8D8",
        "questions": [13, 14, 15, 16],
    },
    {
        "id": "lideranca",
        "name": "Lideranca e Gestao",
        "icon": "",
        "description": "Sobre a qualidade da lideranca e gestao na organizacao.",
        "color": "#4A5A7A",
        "questions": [17, 18, 19, 20, 21, 22],
    },
    {
        "id": "significado",
        "name": "Significado e Compromisso",
        "icon": "",
        "description": "Sobre o significado, satisfacao e seguranca no trabalho.",
        "color": "#8BA7C8",
        "questions": [23, 24, 25, 26, 27, 28],
    },
    {
        "id": "saude",
        "name": "Saude e Bem-Estar",
        "icon": "",
        "description": "Sobre sua saude, qualidade do sono e equilibrio emocional.",
        "color": "#E8C9A0",
        "questions": [29, 30, 31, 32, 33, 34, 35, 36, 37],
    },
    {
        "id": "ambiente",
        "name": "Ambiente de Trabalho",
        "icon": "",
        "description": "Sobre seguranca e respeito no ambiente de trabalho.",
        "color": "#B0CCE4",
        "questions": [38, 39, 40, 41],
    },
]

# ===== 41 QUESTÕES =====
QUESTIONS = {
    1:  {"text": "A sua carga de trabalho acumula-se por ser mal distribuída?", "scale": "frequency", "dimension": "exigencias_quantitativas"},
    2:  {"text": "Com que frequência não tem tempo para completar todas as tarefas do seu trabalho?", "scale": "frequency", "dimension": "exigencias_quantitativas"},
    3:  {"text": "Precisa trabalhar muito rapidamente?", "scale": "frequency", "dimension": "ritmo_trabalho"},
    4:  {"text": "O seu trabalho exige a sua atenção constante?", "scale": "frequency", "dimension": "exigencias_cognitivas"},
    5:  {"text": "O seu trabalho exige que tome decisões difíceis?", "scale": "frequency", "dimension": "exigencias_cognitivas"},
    6:  {"text": "O seu trabalho exige emocionalmente de si?", "scale": "intensity", "dimension": "exigencias_emocionais"},
    7:  {"text": "Tem um elevado grau de influência no seu trabalho?", "scale": "intensity", "dimension": "influencia_trabalho"},
    8:  {"text": "O seu trabalho exige que tenha iniciativa?", "scale": "frequency", "dimension": "possibilidades_desenvolvimento"},
    9:  {"text": "O seu trabalho permite-lhe aprender coisas novas?", "scale": "frequency", "dimension": "possibilidades_desenvolvimento"},
    10: {"text": "No seu local de trabalho, é informado com antecedência sobre decisões importantes, mudanças ou planos para o futuro?", "scale": "frequency", "dimension": "previsibilidade"},
    11: {"text": "Recebe toda a informação de que necessita para fazer bem o seu trabalho?", "scale": "frequency", "dimension": "previsibilidade"},
    12: {"text": "Sabe exatamente quais as suas responsabilidades?", "scale": "frequency", "dimension": "transparencia_papel"},
    13: {"text": "O seu trabalho é reconhecido e apreciado pela gerência?", "scale": "frequency", "dimension": "recompensas"},
    14: {"text": "É tratado de forma justa no seu local de trabalho?", "scale": "frequency", "dimension": "recompensas"},
    15: {"text": "Com que frequência tem ajuda e apoio do seu superior imediato?", "scale": "frequency", "dimension": "apoio_superiores"},
    16: {"text": "Existe um bom ambiente de trabalho entre si e os seus colegas?", "scale": "intensity", "dimension": "comunidade_social"},
    17: {"text": "A sua chefia oferece aos indivíduos e ao grupo boas oportunidades de desenvolvimento?", "scale": "intensity", "dimension": "qualidade_lideranca"},
    18: {"text": "A sua chefia é boa no planeamento do trabalho?", "scale": "intensity", "dimension": "qualidade_lideranca"},
    19: {"text": "A gerência confia nos seus funcionários para fazerem o seu trabalho bem?", "scale": "frequency", "dimension": "confianca_vertical"},
    20: {"text": "Confia na informação que lhe é transmitida pela gerência?", "scale": "frequency", "dimension": "confianca_vertical"},
    21: {"text": "Os conflitos são resolvidos de uma forma justa?", "scale": "frequency", "dimension": "justica_respeito"},
    22: {"text": "O trabalho é igualmente distribuído pelos funcionários?", "scale": "frequency", "dimension": "justica_respeito"},
    23: {"text": "Sou sempre capaz de resolver problemas, se tentar o suficiente.", "scale": "intensity", "dimension": "auto_eficacia"},
    24: {"text": "O seu trabalho tem algum significado para si?", "scale": "intensity", "dimension": "significado_trabalho"},
    25: {"text": "Sente que o seu trabalho é importante?", "scale": "intensity", "dimension": "significado_trabalho"},
    26: {"text": "Sente que os problemas do seu local de trabalho são seus também?", "scale": "intensity", "dimension": "compromisso_trabalho"},
    27: {"text": "Quão satisfeito está com o seu trabalho de uma forma global?", "scale": "intensity", "dimension": "satisfacao_laboral"},
    28: {"text": "Sente-se preocupado em ficar desempregado?", "scale": "intensity", "dimension": "inseguranca_laboral"},
    29: {"text": "Em geral, como sente que é a sua saúde?", "scale": "intensity", "dimension": "saude_geral"},
    30: {"text": "Sente que o seu trabalho lhe exige muita energia que acaba por afetar a sua vida privada negativamente?", "scale": "intensity", "dimension": "conflito_trabalho_familia"},
    31: {"text": "Sente que o seu trabalho lhe exige muito tempo que acaba por afetar a sua vida privada negativamente?", "scale": "intensity", "dimension": "conflito_trabalho_familia"},
    32: {"text": "Com que frequência acordou várias vezes durante a noite e depois não conseguia adormecer novamente?", "scale": "frequency", "dimension": "problemas_dormir"},
    33: {"text": "Com que frequência se sentiu fisicamente exausto?", "scale": "frequency", "dimension": "burnout"},
    34: {"text": "Com que frequência se sentiu emocionalmente exausto?", "scale": "frequency", "dimension": "burnout"},
    35: {"text": "Com que frequência se sentiu irritado?", "scale": "frequency", "dimension": "stress"},
    36: {"text": "Com que frequência se sentiu ansioso?", "scale": "frequency", "dimension": "stress"},
    37: {"text": "Com que frequência se sentiu triste?", "scale": "frequency", "dimension": "sintomas_depressivos"},
    38: {"text": "Tem sido alvo de insultos ou provocações verbais?", "scale": "frequency", "dimension": "comportamentos_ofensivos"},
    39: {"text": "Tem sido exposto a assédio sexual indesejado?", "scale": "frequency", "dimension": "comportamentos_ofensivos"},
    40: {"text": "Tem sido exposto a ameaças de violência?", "scale": "frequency", "dimension": "comportamentos_ofensivos"},
    41: {"text": "Tem sido exposto a violência física?", "scale": "frequency", "dimension": "comportamentos_ofensivos"},
}

# ===== 26 DIMENSÕES Mapeadas para 8 CATEGORIAS =====
DIMENSIONS = {
    # Exigencias do Trabalho
    "exigencias_quantitativas":      {"name": "Exigências Quantitativas",           "type": "risk",     "questions": [1, 2],          "category": "Exigencias do Trabalho",               "description": "Sobrecarga de trabalho e má distribuição de tarefas"},
    "ritmo_trabalho":                {"name": "Ritmo de Trabalho",                  "type": "risk",     "questions": [3],             "category": "Exigencias do Trabalho",               "description": "Velocidade exigida na execução das tarefas"},
    "exigencias_cognitivas":         {"name": "Exigências Cognitivas",              "type": "risk",     "questions": [4, 5],          "category": "Exigencias do Trabalho",               "description": "Atenção constante e tomada de decisões difíceis"},
    "exigencias_emocionais":         {"name": "Exigências Emocionais",              "type": "risk",     "questions": [6],             "category": "Exigencias do Trabalho",               "description": "Demanda emocional do trabalho"},

    # Autonomia e Desenvolvimento
    "influencia_trabalho":           {"name": "Influência no Trabalho",             "type": "resource", "questions": [7],             "category": "Autonomia e Desenvolvimento",         "description": "Grau de controlo e autonomia sobre o próprio trabalho"},
    "possibilidades_desenvolvimento":{"name": "Possibilidades de Desenvolvimento",  "type": "resource", "questions": [8, 9],          "category": "Autonomia e Desenvolvimento",         "description": "Oportunidades de aprendizagem e crescimento profissional"},
    "auto_eficacia":                 {"name": "Auto-eficácia",                      "type": "resource", "questions": [23],            "category": "Autonomia e Desenvolvimento",         "description": "Crença na própria capacidade de resolver problemas"},

    # Informacao e Clareza
    "previsibilidade":               {"name": "Previsibilidade",                    "type": "resource", "questions": [10, 11],        "category": "Informacao e Clareza",                "description": "Informação antecipada sobre mudanças e decisões"},
    "transparencia_papel":           {"name": "Transparência do Papel Laboral",     "type": "resource", "questions": [12],            "category": "Informacao e Clareza",                "description": "Clareza sobre responsabilidades e expectativas"},

    # Reconhecimento e Apoio
    "recompensas":                   {"name": "Recompensas (Reconhecimento)",       "type": "resource", "questions": [13, 14],        "category": "Reconhecimento e Apoio",              "description": "Reconhecimento e tratamento justo"},
    "apoio_superiores":              {"name": "Apoio Social de Superiores",         "type": "resource", "questions": [15],            "category": "Reconhecimento e Apoio",              "description": "Suporte recebido dos superiores hierárquicos"},
    "comunidade_social":             {"name": "Comunidade Social no Trabalho",      "type": "resource", "questions": [16],            "category": "Reconhecimento e Apoio",              "description": "Qualidade do ambiente social entre colegas"},

    # Lideranca e Gestao
    "qualidade_lideranca":           {"name": "Qualidade da Liderança",             "type": "resource", "questions": [17, 18],        "category": "Lideranca e Gestao",                  "description": "Competência da chefia direta"},
    "confianca_vertical":            {"name": "Confiança Vertical",                 "type": "resource", "questions": [19, 20],        "category": "Lideranca e Gestao",                  "description": "Confiança entre gestão e funcionários"},
    "justica_respeito":              {"name": "Justiça e Respeito",                 "type": "resource", "questions": [21, 22],        "category": "Lideranca e Gestao",                  "description": "Equidade na resolução de conflitos e distribuição de trabalho"},

    # Significado e Compromisso
    "significado_trabalho":          {"name": "Significado do Trabalho",            "type": "resource", "questions": [24, 25],        "category": "Significado e Compromisso",           "description": "Sentido e importância atribuída ao trabalho"},
    "compromisso_trabalho":          {"name": "Compromisso com o Local de Trabalho","type": "resource", "questions": [26],            "category": "Significado e Compromisso",           "description": "Envolvimento e identificação com a organização"},
    "satisfacao_laboral":            {"name": "Satisfação Laboral",                 "type": "resource", "questions": [27],            "category": "Significado e Compromisso",           "description": "Satisfação global com o trabalho"},
    "inseguranca_laboral":           {"name": "Insegurança Laboral",                "type": "risk",     "questions": [28],            "category": "Significado e Compromisso",           "description": "Preocupação com perda de emprego"},
    "conflito_trabalho_familia":     {"name": "Conflito Trabalho/Família",          "type": "risk",     "questions": [30, 31],        "category": "Significado e Compromisso",           "description": "Impacto negativo do trabalho na vida privada"},

    # Saude e Bem-Estar
    "saude_geral":                   {"name": "Saúde Geral",                        "type": "resource", "questions": [29],            "category": "Saude e Bem-Estar",                   "description": "Percepção subjetiva do estado de saúde"},
    "problemas_dormir":              {"name": "Problemas em Dormir",                "type": "risk",     "questions": [32],            "category": "Saude e Bem-Estar",                   "description": "Dificuldades relacionadas com o sono"},
    "burnout":                       {"name": "Burnout",                            "type": "risk",     "questions": [33, 34],        "category": "Saude e Bem-Estar",                   "description": "Exaustão física e emocional"},
    "stress":                        {"name": "Stress",                             "type": "risk",     "questions": [35, 36],        "category": "Saude e Bem-Estar",                   "description": "Irritabilidade e ansiedade"},
    "sintomas_depressivos":          {"name": "Sintomas Depressivos",               "type": "risk",     "questions": [37],            "category": "Saude e Bem-Estar",                   "description": "Tristeza e falta de interesse"},

    # Ambiente de Trabalho
    "comportamentos_ofensivos":      {"name": "Comportamentos Ofensivos",           "type": "risk",     "questions": [38, 39, 40, 41],"category": "Ambiente de Trabalho",                "description": "Exposição a violência e assédio no trabalho"},
}

# ===== ESCALAS LIKERT =====
SCALE_LABELS = {
    "frequency": {1: "Nunca/quase nunca", 2: "Raramente", 3: "Às vezes", 4: "Frequentemente", 5: "Sempre"},
    "intensity": {1: "Nada/quase nada", 2: "Um pouco", 3: "Moderadamente", 4: "Muito", 5: "Extremamente"},
}
