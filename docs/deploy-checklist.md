# Fluir - Checklist de Deploy (Render)

Pre-flight e fluxo de deploy conforme `/deploy` e git-workflow.

---

## Pre-deploy Checklist

### Qualidade de codigo
- [ ] Testes passando: `python -m pytest tests/ -v`
- [ ] Sem erros de import: `python -c "from main import app; print('OK')"`
- [ ] Dependencias atualizadas: `pip install -r requirements.txt` sem falhas

### Seguranca
- [ ] Nenhum secret hardcoded (FLUIR_ADMIN_CODE, FLUIR_GEMINI_API_KEY via env)
- [ ] Variaveis de ambiente documentadas em render.yaml
- [ ] `pip list` sem pacotes suspeitos

### Documentacao
- [ ] Alteracoes relevantes no codigo comentadas
- [ ] docs/debug-export-versao.md atualizado se houve mudanca no export

### Git (git-workflow)
- [ ] `git status` - sem arquivos sensiveis staged
- [ ] `git diff` revisado antes do commit
- [ ] Mensagem de commit descritiva

---

## Fluxo de Deploy

### 1. Commit e push (local)

```bash
git add .
git status
git diff --cached
git commit -m "feat: descricao das alteracoes"
git push origin main
```

### 2. Deploy no Render

- **Automatico:** Push em `main` dispara deploy no Render (se configurado)
- **Manual:** Dashboard Render > fluir > Manual Deploy

### 3. Verificacao pos-deploy

1. Acessar `https://[seu-app].onrender.com/api/version`
2. Confirmar `ppt_format: "2.0"` e `export_features`
3. Testar export PPT em uma pesquisa

### 4. Rollback (se necessario)

- Render Dashboard > Deployments > Rollback to previous
- Ou: `git revert HEAD` + push (recomendado para rastreabilidade)

---

## Comandos Git Rapidos (git-workflow)

| Tarefa              | Comando                         |
|---------------------|---------------------------------|
| Ver status          | `git status`                    |
| Ver alteracoes      | `git diff`                     |
| Add e commit        | `git add .` + `git commit -m "msg"` |
| Push                | `git push origin main`         |
| Abortar merge       | `git merge --abort`            |
| Ver historico       | `git log --oneline`            |

---

## Variaveis de Ambiente (Render)

| Variavel            | Obrigatoria | Uso                            |
|---------------------|-------------|---------------------------------|
| FLUIR_ADMIN_CODE    | Sim (prod)  | Codigo de acesso admin         |
| FLUIR_GEMINI_API_KEY| Nao         | Prosa consultiva (fallback se vazio) |
| CORS_ORIGINS        | Nao         | Default "*"                    |
| DATABASE_URL        | Auto        | Injetado pelo Render (fluir-db)|
