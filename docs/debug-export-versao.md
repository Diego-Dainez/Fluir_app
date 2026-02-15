# Debug: Export PPT em versao antiga do backend

## 1. Sintoma

O export PPT retorna `{"detail":"Not Found"}` ao acessar:
`/api/admin/surveys/{id}/export/pptx?admin_code=...`

## 2. Informacoes coletadas

- **Erro:** `{"detail":"Not Found"}` (HTTP 404)
- **URL:** `http://localhost:8000/api/admin/surveys/bd2e9a3e-64de-41fa-b773-64af1cb91558/export/pptx?admin_code=fluir2026`
- **OpenAPI do servidor em execucao:** possui `/export/pdf` e `/export/excel`, **nao possui** `/export/pptx`
- **Codigo em disco (main.py):** possui `/export/pptx`, nao possui `/export/pdf`
- **Endpoint /api/version:** retorna 404 (confirmando que o codigo novo nao esta carregado)

## 3. Hipoteses

1. **Confirmada:** O processo em execucao esta rodando codigo antigo (que tinha export/pdf, nao pptx)
2. O uvicorn iniciado pelo assistente falhou (comando `uvicorn` nao encontrado no PATH)
3. Outro processo/terminal esta servindo na porta 8000 com build antigo

## 4. Causa raiz

**O servidor na porta 8000 ainda esta rodando uma build antiga.** Nessa build:
- A rota era `/export/pdf` (removida e substituida por `/export/pptx`)
- Nao existe o endpoint `/api/version`
- O codigo em disco foi atualizado, mas o processo uvicorn nunca foi reiniciado com sucesso

## 5. Correcao

### Passo 1: Parar o servidor antigo
- No terminal onde o uvicorn esta rodando, pressione `Ctrl+C`
- Se nao souber qual terminal: verifique processos na porta 8000 e encerre

### Passo 2: Iniciar o servidor com o codigo novo
No diretorio do projeto, execute:

```powershell
cd C:\Users\diego.dainez\OneDrive\_Py\Projeto_Katia\App_web
python -m uvicorn main:app --reload --host 0.0.0.0
```

(O uso de `python -m uvicorn` evita problema de PATH no PowerShell.)

### Passo 3: Confirmar que o codigo novo esta ativo
Acesse: http://localhost:8000/api/version

Resposta esperada:
```json
{
  "app": "1.0.0",
  "ppt_format": "2.0",
  "export_features": ["cards", "radar", "bar", "copywriting"]
}
```

Se retornar isso, o export PPT funcionara em `/api/admin/surveys/{id}/export/pptx`.

## 6. Prevencao

1. **Local:** Usar sempre `python -m uvicorn main:app --reload` em desenvolvimento
2. **Antes de testar export:** Conferir `/api/version` para validar que a build esta correta
3. **Producao (Render):** Garantir que o ultimo deploy foi concluido antes de testar
