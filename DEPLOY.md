# Deploy da Aplicacao Fluir no Render.com

Este guia descreve como fazer deploy da aplicacao Fluir no Render.com para que o cliente acesse via URL, sem precisar instalar Python.

## Pre-requisitos

- Conta no GitHub (ou GitLab)
- Codigo do Fluir em um repositorio Git
- Conta no Render.com (gratuita)

## Passo 1: Preparar o Repositorio

1. Certifique-se de que todos os arquivos de deploy estao commitados:
   - `render.yaml`
   - `.renderignore`
   - `runtime.txt` ou `.python-version`
   - `requirements.txt`

2. Verifique que `.env` esta no `.gitignore` (nunca commitar chaves ou senhas).

## Passo 2: Criar Conta no Render

1. Acesse https://render.com
2. Clique em "Get Started"
3. Cadastre-se usando GitHub (recomendado para integracao automatica)

## Passo 3: Criar o Web Service

### Opcao A: Usando Blueprint (render.yaml)

1. No painel do Render, clique em "New +" e selecione "Blueprint"
2. Conecte seu repositorio GitHub
3. Selecione o repositorio que contem o Fluir
4. O Render detecta automaticamente o `render.yaml` e cria o servico
5. Clique em "Apply"

### Opcao B: Configuracao Manual

1. No painel do Render, clique em "New +" e selecione "Web Service"
2. Conecte seu repositorio GitHub e selecione o repositorio
3. Configure:
   - **Name:** fluir (ou outro nome)
   - **Region:** Oregon (US West) ou mais proximo dos usuarios
   - **Branch:** main (ou a branch de producao)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free (para comecar)

## Passo 4: Configurar Variaveis de Ambiente

No painel do servico, va em "Environment" e adicione:

| Variavel | Obrigatorio | Descricao |
|----------|-------------|-----------|
| `FLUIR_ADMIN_CODE` | Sim | Codigo de acesso administrativo (escolha um codigo seguro) |
| `FLUIR_GEMINI_API_KEY` | Nao | Chave da API Google Gemini (para recomendacoes em prosa) |
| `CORS_ORIGINS` | Nao | Origens CORS permitidas (use `*` para desenvolvimento) |
| `ADMIN_RECOVERY_EMAIL` | Nao | Email para recuperacao de chave |
| `SMTP_HOST` | Nao | Servidor SMTP para envio de emails |
| `SMTP_PORT` | Nao | Porta SMTP (ex: 587) |
| `SMTP_USER` | Nao | Usuario SMTP |
| `SMTP_PASS` | Nao | Senha do aplicativo |
| `SMTP_FROM` | Nao | Email remetente |

**Importante:** Marque `FLUIR_ADMIN_CODE` e `FLUIR_GEMINI_API_KEY` como "Secret" se a opcao existir.

## Passo 5: Fazer o Deploy

1. Apos salvar as configuracoes, o Render inicia o build automaticamente
2. Acompanhe os logs em "Logs"
3. O deploy leva cerca de 2-5 minutos
4. Ao concluir, a URL sera exibida: `https://fluir-xxxx.onrender.com`

## Passo 6: Verificar o Deploy

1. Acesse a URL do servico
2. Verifique se a tela de login aparece
3. Teste o login com o `FLUIR_ADMIN_CODE` configurado
4. Crie uma pesquisa de teste e valide as funcionalidades principais

## Compartilhando com o Cliente

Envie ao cliente:
- **URL da aplicacao:** `https://fluir-xxxx.onrender.com` (sua URL real)
- **Link do questionario:** apos criar uma pesquisa, use o link gerado ou o QR Code
- **Codigo de acesso:** o `FLUIR_ADMIN_CODE` (com cuidado, apenas para administradores)

## Consideracoes Importantes

### Plano Gratuito

- O servico "dorme" apos 15 minutos de inatividade
- A primeira requisicao apos dormir pode levar 30-60 segundos
- Para uso em producao com clientes, considere o plano pago ($7/mes) que mantem o servico sempre ativo

### Banco de Dados (SQLite)

- O banco SQLite e criado automaticamente
- No plano gratuito, o disco e efemero: dados podem ser perdidos em alguns casos (redeploy, reinicio)
- Para producao critica, considere migrar para PostgreSQL (Render oferece plano gratuito)

### Atualizacoes

- Ao fazer push para o repositorio conectado, o Render faz redeploy automatico
- Ou use "Manual Deploy" no painel para redeployar a versao atual

## Troubleshooting

### Build falha com erro de dependencia

- Verifique se `requirements.txt` esta correto
- Confira os logs do build para mensagens de erro especificas

### Erro 503 ou servico nao responde

- O servico pode estar "acordando" (plano gratuito)
- Aguarde 30-60 segundos e tente novamente

### Login nao funciona

- Confirme que `FLUIR_ADMIN_CODE` esta configurado corretamente
- Verifique se nao ha espacos extras no valor da variavel

### Banco de dados vazio apos redeploy

- No plano gratuito, o disco pode ser limpo
- Para persistencia, use PostgreSQL ou o disco persistente (planos pagos)
