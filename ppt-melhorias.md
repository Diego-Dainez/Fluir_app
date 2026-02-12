# Melhorias do Export PPT - Fluir

## Objetivo
Aprimorar o export PowerPoint para: capa com imagem de fundo e logo, formato 16:9, e conteudo completo equivalente ao Excel + Dashboard.

---

## Escopo

### 1. Capa do PPT
- **Wallpaper:** imagem `static/img/wallpaper_PPT.png` como plano de fundo
- **Logo:** `static/img/fluir_logo.png` em tamanho reduzido no canto superior direito
- **Texto:** manter titulo, subtitulo e dados (empresa, data)

### 2. Formato
- **Proporcao:** 16:9 (widescreen)
- **Dimensoes:** slide_width=Inches(13.333), slide_height=Inches(7.5)

### 3. Conteudo (paridade Excel + Dashboard)
| Excel/Dashboard | Slide PPT |
|-----------------|-----------|
| Resumo Executivo (titulo, empresa, data, respondentes) | Capa (ja tem) |
| KPIs (4 indicadores) | Slide KPIs |
| Resumo Geral (favoraveis, atencao, criticas) | Slide Resumo |
| Dimensoes (#, Nome, Score, Status, Tipo, Categoria, **Descricao**) | Slide(s) Dimensoes |
| Respostas Individuais (tabela transposta ID x dimensoes) | Slide(s) Respostas |
| Recomendacoes (#, Prioridade, Titulo, Descricao) | Slide Recomendacoes estruturadas |
| Recomendacoes em prosa (IA) | Slides por prazo (imediata, curto, medio) |
| Rodape | Slide final |

---

## Arquivos a modificar

| Arquivo | Mudanca |
|---------|---------|
| `export_service.py` | Refatorar `export_pptx` e helpers; add `respondents_data`, `recommendations`; capa com img; 16:9; slides extras |
| `main.py` | Passar `respondents_data` e `recommendations` para `export_pptx` |

---

## Implementacao

### Fase 1: Formato e capa
- Definir `prs.slide_width`, `prs.slide_height` (16:9)
- Carregar imagens via `Path(__file__).parent / "static" / "img"`
- `_add_title_slide`: adicionar pic wallpaper (full slide), pic logo (top-right ~1"x1"), textos por cima

### Fase 2: Conteudo completo
- Assinatura: `export_pptx(survey, respondents_data, dim_scores_agg, kpis, summary, recommendations, recommendations_prose)`
- Slide Dimensoes: incluir coluna Descricao (pode truncar ou quebrar em 2 slides)
- Slide Respostas Individuais: tabela com ID + scores por dimensao (adaptar de Excel; muitas dims = font menor ou paginar)
- Slide Recomendacoes estruturadas: tabela #, Prioridade, Titulo, Descricao

### Fase 3: Testes
- Atualizar `test_export.py` com novos parametros
- Garantir que imagens existem (skip se nao existir para robustez)

---

## Constantes
- SLIDE_WIDTH_16_9 = 13.333  # inches
- SLIDE_HEIGHT_16_9 = 7.5
- LOGO_SIZE = 1.0  # inches (quadrado)

---

## Checklist
- [ ] Formato 16:9
- [ ] Wallpaper na capa
- [ ] Logo no canto superior direito
- [ ] Slide Respostas Individuais
- [ ] Slide Recomendacoes estruturadas
- [ ] Dimensoes com Descricao
- [ ] Testes passando
