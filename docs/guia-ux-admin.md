# Guia UX do Painel Administrativo - Fluir

Passo a passo da experiência do usuário no painel de gestão, do acesso até as ações principais.

---

## 1. Acesso ao painel

### 1.1 Tela de login
- **Rota:** `/` (raiz)
- **Elementos:** Campo "Código de Acesso", botão "Entrar", link "Esqueci minha chave"
- **Fluxo:** Usuário digita o código administrativo e clica em "Entrar"
- **Validação:** Se o código for inválido, aparece mensagem "Código inválido"
- **Sucesso:** Redirecionamento para `/admin` e armazenamento do código em `sessionStorage`

### 1.2 Recuperação de chave
- **Gatilho:** Clique em "Esqueci minha chave"
- **Comportamento:** Exibe formulário com campo de e-mail
- **Fluxo:** Usuário informa o e-mail cadastrado e clica em "Enviar"
- **Feedback:** Mensagem informando se o e-mail está cadastrado e se a chave foi enviada

### 1.3 Acesso direto ao admin
- Se o usuário já tiver código em `sessionStorage`, ao acessar `/` é redirecionado automaticamente para `/admin`

---

## 2. Layout e navegação

### 2.1 Sidebar (menu lateral)
- **Logo:** Fluir + "Painel de Gestão"
- **Botão hamburger:** À direita de "Fluir"; abre/fecha a sidebar
- **Estado colapsado:** Faixa estreita (56px) com ícones: hamburger, Pesquisas, Dashboard, Respostas, Sair
- **Estado expandido:** Sidebar 260px com textos e ícones completos

### 2.2 Abas principais
| Aba | Quando aparece | Conteúdo |
|-----|----------------|----------|
| **Pesquisas** | Sempre | Lista de pesquisas da empresa |
| **Dashboard** | Após selecionar uma pesquisa | Indicadores, gráficos e recomendações |
| **Respostas** | Após selecionar uma pesquisa | Tabela transposta por respondente |

### 2.3 Header
- **Título dinâmico:** "Pesquisas", "Dashboard" ou "Respostas Individuais"
- **Ações contextuais:** Dependem da aba atual (ex.: "+ Nova Pesquisa", botões PPT/Excel)

---

## 3. Aba Pesquisas

### 3.1 Estado vazio
- Mensagem: "Nenhuma pesquisa encontrada"
- Botão "+ Nova Pesquisa" no header

### 3.2 Lista de pesquisas (cards)
Cada card exibe:
- Nome da empresa (editável)
- Toggle ativo/inativo
- Data de criação
- Quantidade de respondentes
- Código da pesquisa
- Botões: "Compartilhar" e "Excluir"

### 3.3 Criar nova pesquisa
1. Clicar em "+ Nova Pesquisa"
2. Modal "Nova Pesquisa" abre
3. Informar "Nome da Empresa / Cliente"
4. Clicar em "Criar Pesquisa"
5. Toast de sucesso e novo card aparece na lista

### 3.4 Editar nome da empresa
1. No card, clicar em "Editar" ao lado do nome
2. Campo vira input de texto
3. Editar e confirmar (Enter ou clicar fora) ou cancelar (Esc)

### 3.5 Ativar/desativar pesquisa
- Toggle no card: ativo (verde) ou inativo (vermelho)
- Clique alterna o status; toast "Status atualizado!"

### 3.6 Compartilhar pesquisa
1. Clicar em "Compartilhar"
2. Modal exibe QR Code e link da pesquisa
3. Botão "Copiar Link" para copiar o URL
4. Toast "Link copiado!" ao copiar

### 3.7 Excluir pesquisa
1. Clicar em "Excluir"
2. Modal de confirmação: "Tem certeza que deseja excluir a pesquisa [nome]?"
3. Opções: "Cancelar" ou "Excluir"
4. Se confirmar: pesquisa removida, toast "Pesquisa excluída."; se era a selecionada, volta para aba Pesquisas

### 3.8 Selecionar pesquisa para análise
- Clicar no card (área não ocupada por botões)
- Abas Dashboard e Respostas passam a aparecer na sidebar
- Navegação automática para o Dashboard

---

## 4. Aba Dashboard

### 4.1 Pré-requisito
- Ter selecionado uma pesquisa

### 4.2 Ações do header
- **PPT:** Exporta relatório em PowerPoint (cor #e72a3f)
- **Excel:** Exporta planilha (cor #31a966)

### 4.3 Seletor de pesquisas
- Chips no topo para trocar a pesquisa sem voltar à aba Pesquisas

### 4.4 Blocos de conteúdo (de cima para baixo)

#### 4.4.1 Análise e Recomendações (IA)
- Prosa gerada por IA em três blocos: imediato, curto prazo, médio prazo
- Ou lista de recomendações se não houver prosa
- Estado vazio: "Aguardando dados suficientes para análise..."

#### 4.4.2 KPIs
- Cards com indicadores: valor, label, status (cor verde/amarelo/vermelho)

#### 4.4.3 Gráficos
- **Panorama Geral:** Gráfico radar com médias por categoria
- **Comparativo por Dimensão:** Gráfico de barras horizontais com as 26 dimensões

#### 4.4.4 Tabela de Dimensões
- Colunas: #, Dimensão, Score, Status, Tipo, Categoria

---

## 5. Aba Respostas

### 5.1 Pré-requisito
- Ter selecionado uma pesquisa

### 5.2 Conteúdo
- Tabela transposta: Dimensão/Categoria + Média Geral + coluna por respondente (R_001, R_002, etc.)
- Valores individuais por respondente e dimensão

### 5.3 Estados
- Sem pesquisa: "Selecione uma pesquisa no Dashboard primeiro."
- Carregando: "Carregando respostas..."
- Sem respondentes: "Nenhum respondente nesta pesquisa."

---

## 6. Sair

### 6.1 Ação
- Clicar em "Sair" na sidebar (ícone de logout)
- `sessionStorage` é limpo
- Redirecionamento para `/` (tela de login)

---

## 7. Modais e notificações

| Elemento | Uso |
|----------|-----|
| **Modal Nova Pesquisa** | Criar pesquisa; fechar com X ou Cancelar |
| **Modal QR Code** | Compartilhar; mostrar link e QR Code |
| **Modal Excluir** | Confirmar exclusão; fechar clicando fora ou Cancelar |
| **Toast** | Feedback breve (ex.: sucesso, erro); some em ~3s |

---

## 8. Responsividade

### 8.1 Desktop (>= 769px)
- Sidebar expansível; colapsa em faixa de 56px
- Gráficos lado a lado (2 colunas)

### 8.2 Mobile (<= 768px)
- Sidebar colapsa em faixa de 56px ou expande sobre o conteúdo
- Overlay escuro ao expandir; clique fora fecha
- Gráficos empilhados (1 coluna)
- KPIs em grid 2x2

---

## 9. Fluxo resumido (happy path)

```
Login (/) --> Admin (/admin)
    --> Aba Pesquisas
        --> Criar pesquisa
        --> Compartilhar (QR/link)
        --> Selecionar pesquisa
    --> Aba Dashboard
        --> Ver KPIs, gráficos, recomendações
        --> Exportar PPT ou Excel
    --> Aba Respostas
        --> Ver tabela por respondente
    --> Sair --> Login
```
