# SETUP DO GITHUB PROJECT
## Guia passo a passo para configurar o controle central do ecossistema

> **Objetivo:** Criar 1 Project central que controla todos os 16+ repositórios

---

## 🎯 POR QUE UM PROJECT CENTRALIZADO?

Sem ele, você teria que:
* Abrir 16 repositórios diferentes para ver o que está sendo feito
* Não conseguir visualizar dependências entre projetos
* Perder a visão de "todos os projetos terminam juntos"

Com ele, você tem:
* **Visão única** de todo o trabalho (cross-repo)
* **Priorização global** (não apenas por repo)
* **Controle de dependências** entre projetos
* **Roadmap sincronizado**

---

## 📋 PASSO A PASSO

### 1️⃣ Criar o Project

1. Acesse: https://github.com/orgs/avilaops/projects (ou https://github.com/users/avilaops/projects se for conta pessoal)
2. Clique em **"New project"**
3. Escolha template: **"Board"**
4. Nome: **"Agro-Tech Ecosystem"**
5. Descrição: **"Controle central de todos os 16+ projetos do ecossistema"**

---

### 2️⃣ Configurar Custom Fields

No Project, vá em **Settings** (ícone ⚙️) → **Fields**

Crie estes 7 campos personalizados:

#### Field 1: **Status** (Single Select)
* Tipo: **Single Select**
* Opções (nesta ordem):
  1. `Backlog` (cor cinza: #9E9E9E)
  2. `Ready` (cor verde: #00C853)
  3. `In Progress` (cor azul: #2196F3)
  4. `In Review` (cor roxo: #9C27B0)
  5. `Blocked` (cor vermelho: #E91E63)
  6. `Done` (cor verde escuro: #4CAF50)

#### Field 2: **Priority** (Single Select)
* Tipo: **Single Select**
* Opções:
  1. `P0` (cor vermelho: #D32F2F)
  2. `P1` (cor laranja: #F57C00)
  3. `P2` (cor amarelo: #FBC02D)
  4. `P3` (cor cinza: #9E9E9E)

#### Field 3: **Layer** (Single Select)
* Tipo: **Single Select**
* Opções:
  1. `Decision` (cor azul: #667BC6)
  2. `Sensing` (cor rosa: #DA7F8F)
  3. `Execution` (cor amarelo: #FADA7A)
  4. `Infra` (cor verde: #A4D0A4)

#### Field 4: **Quarter** (Single Select)
* Tipo: **Single Select**
* Opções:
  1. `Q1-2026` (Jan-Mar)
  2. `Q2-2026` (Abr-Jun)
  3. `Q3-2026` (Jul-Set)
  4. `Q4-2026` (Out-Dez)

#### Field 5: **Effort** (Single Select)
* Tipo: **Single Select**
* Opções:
  1. `XS` (< 1 dia)
  2. `S` (1-3 dias)
  3. `M` (1 semana)
  4. `L` (2-4 semanas)
  5. `XL` (1-3 meses)

#### Field 6: **Impact** (Single Select)
* Tipo: **Single Select**
* Opções:
  1. `High` (cor vermelho: #D32F2F)
  2. `Medium` (cor amarelo: #FBC02D)
  3. `Low` (cor cinza: #9E9E9E)

#### Field 7: **Blocked By** (Text)
* Tipo: **Text**
* Descrição: "Link para issue bloqueadora (ex: #123 ou org/repo#456)"

---

### 3️⃣ Criar as 5 Views Principais

#### View 1: **Board (Kanban)** — Controle diário

1. Na view padrão, clique em **"Board"** (já vem criada)
2. Renomeie para: **"Board — Daily Control"**
3. **Layout:** Board
4. **Group by:** Status
5. **Column order:** Backlog → Ready → In Progress → In Review → Blocked → Done
6. **Filter:** `is:open` (não mostrar Done por padrão — opcional)
7. **Sort:** Priority (P0 no topo)

---

#### View 2: **Roadmap (Table)** — Controle semanal

1. Clique no **"+"** ao lado das abas de view
2. Nome: **"Roadmap — Weekly"**
3. **Layout:** Table
4. **Group by:** Quarter
5. **Sort:** Priority (P0 primeiro)
6. **Visible columns:**
   * Title
   * Status
   * Layer
   * Effort
   * Impact
   * Repository
   * Assignees
7. **Filter:** `is:open` ou `Status != Done`

---

#### View 3: **By Layer (Board)** — Balanceamento

1. Novo view: **"By Layer — Balance"**
2. **Layout:** Board
3. **Group by:** Layer
4. **Column order:** Decision | Sensing | Execution | Infra
5. **Filter:** `Status:In Progress` OR `Status:Ready`
6. **Sort:** Priority

**Objetivo:** Ver se alguma camada está sobrecarregada ou esquecida

---

#### View 4: **Blocked (Table)** — Caça gargalo

1. Novo view: **"Blocked — Unblock Now"**
2. **Layout:** Table
3. **Filter:** `Status:Blocked`
4. **Sort:** Priority (P0 primeiro)
5. **Visible columns:**
   * Title
   * Blocked By
   * Layer
   * Quarter
   * Priority
   * Repository

**Objetivo:** Resolver bloqueios rápido

---

#### View 5: **This Week (Table)** — Execução pura

1. Novo view: **"This Week — Focus"**
2. **Layout:** Table
3. **Filter:** `Status:In Progress` AND `Quarter:Q1-2026` (ajustar conforme quarter atual)
4. **Sort:** Priority
5. **Visible columns:**
   * Title
   * Status
   * Priority
   * Effort
   * Assignees

**Objetivo:** Foco no que está sendo feito AGORA

---

### 4️⃣ Configurar Automações (Workflows)

No Project, vá em **Settings** → **Workflows**

#### Automation 1: **Auto-add to project**
* **Trigger:** Item added to project
* **Action:** Set Status = `Backlog`

#### Automation 2: **Move to In Review**
* **Trigger:** Pull request opened
* **Action:** Set Status = `In Review`

#### Automation 3: **Move to Done**
* **Trigger:** Pull request merged
* **Action:** Set Status = `Done`

#### Automation 4: **Closed → Done**
* **Trigger:** Issue closed
* **Action:** Set Status = `Done`

---

### 5️⃣ Adicionar Repositórios ao Project

Para que o Project possa "ver" issues/PRs de todos os repos:

1. No Project, vá em **Settings** → **Manage access**
2. Adicione os repositórios:
   * `avilaops/agro-tech-ecosystem`
   * `avilaops/Precision-Agriculture-Platform`
   * `avilaops/CanaSwarm-Intelligence`
   * `avilaops/AgriBot-Retrofit`
   * `avilaops/AI-Vision-Agriculture`
   * `avilaops/CanaSwarm-Core`
   * `avilaops/CanaSwarm-MicroBot`
   * `avilaops/CanaSwarm-Vision`
   * `avilaops/CanaSwarm-Swarm-Coordinator`
   * `avilaops/CanaSwarm-3D-Models`
   * `avilaops/CanaSwarm-Solar-Manager`
   * `avilaops/CanaSwarm-Docs`
   * `avilaops/MicroGrid-Manager`
   * `avilaops/Industrial-Automation-OS`
   * `avilaops/Robotics-Swarm-Simulator`
   * `avilaops/Autonomous-Agent-Framework`
   * `avilaops/Agro-Machinery-Marketplace`

**Ou** use o link direto ao criar issue: `#agro-tech-ecosystem` nas issues te dá opção de adicionar ao project.

---

### 6️⃣ Testar o Setup

Crie 1 issue de teste:

1. Vá em qualquer repo (ex: `Precision-Agriculture-Platform`)
2. Crie issue usando template **"⚙️ Feature/Task"**
3. Preencha os campos
4. Adicione label `triage`
5. No sidebar direito, em **Projects**, adicione ao **"Agro-Tech Ecosystem"**
6. A issue deve aparecer automaticamente na view **Board** na coluna **Backlog**

Agora edite a issue no Project (não no repo):
* Mude **Status** para `Ready`
* Mude **Priority** para `P1`
* Mude **Layer** para `Decision`
* Mude **Quarter** para `Q1-2026`
* Mude **Effort** para `M`
* Mude **Impact** para `High`

Vá para a view **Roadmap** — a issue deve estar lá organizada.

---

## 🎨 RESULTADO ESPERADO

### View Board (Daily)
```
┌─ Backlog ─┬─ Ready ─┬─ In Progress ─┬─ In Review ─┬─ Blocked ─┬─ Done ─┐
│ Issue A   │ Issue C  │ Issue E        │ PR #123     │ Issue X   │ Issue Z│
│ Issue B   │ Issue D  │ Issue F        │             │           │        │
│           │          │ Issue G        │             │           │        │
└───────────┴──────────┴────────────────┴─────────────┴───────────┴────────┘
```

### View By Layer (Balance)
```
┌─ Decision ─┬─ Sensing ─┬─ Execution ─┬─ Infra ─┐
│ Issue A    │ Issue C    │ Issue E     │ Issue G │
│ Issue B    │ Issue D    │ Issue F     │ Issue H │
│            │            │             │         │
└────────────┴────────────┴─────────────┴─────────┘
```

---

## 📊 COMO USAR NO DIA A DIA

### 🌅 **Manhã (5 min):**
1. Abrir view **"Board — Daily Control"**
2. Ver coluna **In Progress** (o que está sendo feito)
3. Ver coluna **Blocked** (algum gargalo novo?)
4. Priorizar o que fazer hoje

### 🗓️ **Toda segunda (30 min):**
1. Abrir view **"Roadmap — Weekly"**
2. Revisar P0 e P1 do quarter atual
3. Mover issues de **Backlog** para **Ready** (spec completa)
4. Review de **Blocked** (resolver gargalos)

### 📈 **Fim do mês (2h):**
1. Review do quarter
2. Métricas:
   * Quantas issues foram Done?
   * Cycle time médio (Ready → Done)?
   * Quantas ficaram Blocked?
   * Alguma camada esquecida?
3. Ajustar roadmap do próximo mês

---

## 🚀 PRÓXIMOS PASSOS

Depois do setup:

1. ✅ Aplicar labels em todos os repos (`scripts/setup-labels.ps1`)
2. ✅ Criar as 7 issues P0 iniciais (governança + primeiro ciclo)
3. ✅ Fazer primeiro triage (classificar as issues)
4. ✅ Começar primeiro sprint/iteration Q1-2026

---

## 📚 RECURSOS

* [GitHub Projects Docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
* [Projects Best Practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
* [Automating Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)

---

**Com o Project configurado, você tem visão de tudo em um só lugar.**

🎯📊
