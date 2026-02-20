# GOVERNANÇA & CADÊNCIA
## Como trabalhamos para fazer todos os projetos terminarem juntos

> **"Nenhum trabalho entra em 'In Progress' sem critério de aceite escrito."**

---

## 🏗️ AS 4 CAMADAS FIXAS DO ECOSSISTEMA

Toda demanda, feature, ou ideia se encaixa em **UMA** dessas 4 camadas:

### 1️⃣ **DECISION** (Camada de Decisão)
**O que faz:** Analytics, ROI, recomendações, motor econômico

**Projetos:**
* Precision-Agriculture-Platform (decisão por zona)
* CanaSwarm-Intelligence (dashboard + monitoramento)

**Perguntas que responde:**
* Onde investir primeiro?
* Qual zona reformar?
* Quanto economizar?

---

### 2️⃣ **SENSING** (Camada de Sensoriamento)
**O que faz:** Coleta de dados, visão computacional, GIS, ingest

**Projetos:**
* AI-Vision-Agriculture (visão computacional)
* CanaSwarm-Vision (processamento edge)
* CanaSwarm-MicroBot (captura de dados físicos)

**Perguntas que responde:**
* O que está acontecendo no campo?
* Qual a maturidade da cultura?
* Onde estão os problemas?

---

### 3️⃣ **EXECUTION** (Camada de Execução)
**O que faz:** Automação física, máquinas, robótica, atuação

**Projetos:**
* AgriBot-Retrofit (tratores automatizados)
* CanaSwarm-MicroBot (robôs de campo)
* CanaSwarm-Core (coordenação)
* Swarm-Coordinator (algoritmos de enxame)

**Perguntas que responde:**
* Como executar a recomendação?
* Como automatizar a operação?
* Como coordenar múltiplos robôs?

---

### 4️⃣ **INFRA** (Camada de Infraestrutura)
**O que faz:** APIs, dados, auth, energia, DevOps, plataforma

**Projetos:**
* Solar-Manager (energia solar)
* MicroGrid-Manager (distribuição de energia)
* Industrial-Automation-OS (automação industrial)
* Robotics-Swarm-Simulator (testes)
* Autonomous-Agent-Framework (framework base)
* Agro-Machinery-Marketplace (comercial)

**Perguntas que responde:**
* Como integrar tudo?
* Como garantir energia?
* Como escalar?

---

## 🔄 CICLO DE TRABALHO (CADÊNCIA)

Todo trabalho passa por **5 fases obrigatórias**:

### 1️⃣ INTAKE (Entrada)
**O que acontece:** Ideia/demanda vira Issue com template

**Templates:**
* `📋 Demanda de Mercado` — vinda de cliente/mercado
* `⚙️ Feature/Task` — técnica/engenharia

**Saída:** Issue criada com label `triage`

**Status:** `Backlog`

---

### 2️⃣ SPEC (Especificação)
**O que acontece:** 1 página de spec antes de começar código

**O que deve ter:**
* Objetivo (1 frase)
* Inputs (o que recebe)
* Outputs (o que produz)
* Critério de aceite (3-5 bullets)

**Regra de ouro:** 📌 **Nenhum trabalho entra em "In Progress" sem critério de aceite escrito**

**Saída:** Issue movida para `Ready`

**Status:** `Ready`

---

### 3️⃣ BUILD (Construção)
**O que acontece:** Código, testes, documentação

**Workflow:**
1. Criar branch `feature/issue-123-nome`
2. Desenvolver (commits atômicos)
3. Abrir PR (PR template)
4. CI/CD roda (testes, lint)
5. Code review (pelo menos 1 aprovação)

**Status:** `In Progress` → `In Review`

---

### 4️⃣ RELEASE (Entrega)
**O que acontece:** Merge, tag, changelog, deploy

**Checklist:**
- [ ] PR mergeada
- [ ] Tag versionada (ex: `v0.1.0`)
- [ ] Changelog atualizado
- [ ] Documentação atualizada
- [ ] Deploy realizado (se aplicável)

**Status:** `Done`

---

### 5️⃣ FEEDBACK (Aprendizado)
**O que acontece:** Post-mortem, métricas de impacto

**O que documentar:**
* O que funcionou
* O que não funcionou
* Métricas de impacto (se houver)
* Próximos passos

**Formato:** Comentário na Issue original ou Issue separada com label `post-mortem`

---

## ✅ DEFINITION OF DONE (DoD)

**Nada está "Done" se não passar por todos esses critérios:**

### 📦 Para qualquer entrega:
- [ ] **Roda** — funciona localmente sem erros
- [ ] **Exemplo** — tem exemplo de uso (README, script, ou notebook)
- [ ] **Teste mínimo** — pelo menos 1 teste (unitário ou integração)
- [ ] **Release notes** — changelog ou descrição do que mudou

### 🔗 Para integrações:
- [ ] **Contrato definido** — API spec, formato de arquivo, ou protocolo documentado
- [ ] **README atualizado** — em ambos os projetos (como integrar)
- [ ] **Fluxo completo** — pelo menos 1 caso de uso end-to-end funcional
- [ ] **Teste de integração** — testa a comunicação entre sistemas

### 📊 Para features voltadas a cliente:
- [ ] **Valor mensurável** — métrica de sucesso definida (ROI, %, tempo economizado)
- [ ] **Feedback coletado** — pelo menos 1 usuário testou e aprovou
- [ ] **Documentação de usuário** — não só técnica, mas como usar

---

## 🏷️ TAXONOMIA DE LABELS

### **TYPE** (tipo de trabalho)
* `demand` — Demanda de mercado/cliente
* `feature` — Nova funcionalidade
* `bug` — Correção de bug
* `refactor` — Refatoração
* `docs` — Documentação
* `infra` — Infraestrutura/DevOps
* `research` — Pesquisa/spike

### **LAYER** (camada do ecossistema)
* `layer:decision` — Analytics, ROI, recomendações
* `layer:sensing` — Visão, sensores, ingest
* `layer:execution` — Máquinas, robôs, atuação
* `layer:infra` — APIs, dados, energia, DevOps

### **PRIORITY** (prioridade)
* `P0` — Bloqueador / Cliente pagante esperando
* `P1` — Importante / Impacto alto / Roadmap Q
* `P2` — Útil / Pode esperar Q+1
* `P3` — Nice-to-have / Backlog

### **STATUS** (estado)
* `triage` — Precisa ser analisado
* `blocked` — Bloqueado por dependência
* `ready` — Spec pronta, pode começar
* `in-progress` — Sendo desenvolvido
* `in-review` — PR aberto, aguardando review
* `done` — Completo

### **QUARTER** (tempo)
* `Q1-2026` — Jan-Mar
* `Q2-2026` — Abr-Jun
* `Q3-2026` — Jul-Set
* `Q4-2026` — Out-Dez

### **EFFORT** (esforço)
* `effort:XS` — < 1 dia
* `effort:S` — 1-3 dias
* `effort:M` — 1 semana
* `effort:L` — 2-4 semanas
* `effort:XL` — 1-3 meses

### **IMPACT** (impacto)
* `impact:high` — Crítico para MVP ou cliente pagante
* `impact:medium` — Melhora significativa
* `impact:low` — Incremental

### **REPO** (repositório afetado)
* `repo:precision-platform`
* `repo:canaswarm-intelligence`
* `repo:agribot-retrofit`
* `repo:ai-vision`
* `repo:microbot`
* `repo:swarm-coordinator`
* `repo:solar-manager`
* `repo:microgrid-manager`
* `repo:marketplace`
* `repo:multiple` — Afeta múltiplos repos

---

## 📋 GITHUB PROJECT — ESTRUTURA

### 🎨 Custom Fields

Crie estes campos no GitHub Project:

| Field | Type | Options |
|-------|------|---------|
| **Status** | Single Select | Backlog, Ready, In Progress, In Review, Blocked, Done |
| **Priority** | Single Select | P0, P1, P2, P3 |
| **Layer** | Single Select | Decision, Sensing, Execution, Infra |
| **Quarter** | Single Select | Q1-2026, Q2-2026, Q3-2026, Q4-2026 |
| **Effort** | Single Select | XS, S, M, L, XL |
| **Impact** | Single Select | High, Medium, Low |
| **Blocked By** | Text | Link para issue bloqueadora |

---

### 📊 Views (5 telas principais)

#### 1️⃣ **Board (Kanban)** — Controle diário
* Agrupar por: `Status`
* Colunas: Backlog → Ready → In Progress → In Review → Blocked → Done
* Filtro: `Status != Done` (só mostra trabalho ativo)

#### 2️⃣ **Roadmap (Table)** — Controle semanal
* View: Table
* Agrupar por: `Quarter`
* Ordenar por: `Priority` (P0 primeiro)
* Colunas visíveis: Title, Status, Layer, Effort, Impact, Repo

#### 3️⃣ **By Layer (Board)** — Garantir balanceamento
* Agrupar por: `Layer`
* Colunas: Decision | Sensing | Execution | Infra
* Filtro: `Status = In Progress OR Status = Ready`
* **Objetivo:** Ver se alguma camada está sobrecarregada ou esquecida

#### 4️⃣ **Blocked (Table)** — Caça gargalo
* Filtro: `Status = Blocked`
* Ordenar por: `Priority`
* Colunas visíveis: Title, Blocked By, Layer, Quarter
* **Objetivo:** Resolver bloqueios rápido

#### 5️⃣ **This Week (Table)** — Execução pura
* Filtro: `Status = In Progress` AND `Quarter = Q1-2026` (ou iteration se usar sprints)
* Ordenar por: `Priority`
* **Objetivo:** Foco no que está sendo feito AGORA

---

## 🤖 AUTOMAÇÕES (GitHub Project Workflows)

Configure estas automações nativas:

### Auto-add to project
* **Trigger:** Issue criada com label `triage`
* **Action:** Adicionar ao Project + Status = `Backlog`

### Move to Ready
* **Trigger:** Label `triage` removida + spec completa
* **Action:** Status = `Ready`

### Move to In Review
* **Trigger:** PR aberto e linkado à issue
* **Action:** Status = `In Review`

### Move to Done
* **Trigger:** PR mergeado
* **Action:** Status = `Done`

### Flag blocked
* **Trigger:** Label `blocked` adicionado
* **Action:** Status = `Blocked`

---

## 📐 REGRAS DE TRABALHO

### 1️⃣ Nenhum "In Progress" sem aceite
**Regra:** Issue só pode entrar em `In Progress` se tiver critério de aceite preenchido.

**Como validar:** Code review do próprio template da Issue antes de mover.

---

### 2️⃣ WIP Limit (Work in Progress)
**Regra:** Máximo de 3 issues `In Progress` por pessoa.

**Por quê:** Foco > multitarefa. Terminar é melhor que começar.

---

### 3️⃣ Dependências explícitas
**Regra:** Se Issue A depende de Issue B, usar campo `Blocked By` e label `blocked`.

**Por quê:** Transparência de gargalos.

---

### 4️⃣ Review obrigatório
**Regra:** Todo PR precisa de pelo menos 1 aprovação antes de merge.

**Exceção:** Hotfix crítico por P0 pode merge com post-review.

---

### 5️⃣ Changelog sempre
**Regra:** Todo merge que impacta usuário final precisa atualizar `CHANGELOG.md`.

**Formato:** [Keep a Changelog](https://keepachangelog.com/)

---

## 🔁 CADÊNCIA DE REUNIÕES (se trabalhar em equipe)

### Daily stand-up (assíncrono)
* **Formato:** Comentário na Issue ou mensagem no canal
* **3 perguntas:**
  1. O que fiz ontem?
  2. O que farei hoje?
  3. Há algum bloqueio?

### Weekly review (síncrona — 30min)
* **Agenda:**
  1. Review do Roadmap (view 2)
  2. Review do Blocked (view 4)
  3. Priorização do próximo ciclo (mover de Backlog → Ready)

### Quarterly review (síncrona — 2h)
* **Agenda:**
  1. Retrospectiva do quarter (o que funcionou / não funcionou)
  2. Métricas de impacto (clientes, ROI, hectares)
  3. Ajuste de roadmap (próximos 3 meses)

---

## 📊 MÉTRICAS DE SAÚDE DO ECOSSISTEMA

**Acompanhe semanalmente:**

| Métrica | Meta | Por quê |
|---------|------|---------|
| **Issues em Backlog** | < 50 | Evitar graveyard de ideias |
| **Issues Blocked** | < 5 | Evitar gargalos |
| **Cycle Time** (Ready → Done) | < 2 semanas (médio) | Velocidade de entrega |
| **WIP** (In Progress) | 3-10 (total) | Foco > multitarefa |
| **DoD Compliance** | 100% | Qualidade não negocia |
| **Issues sem aceite** | 0 | Clareza antes de começar |

---

## 🚨 SINAIS DE ALERTA

### 🔴 Backlog explodindo (> 100 issues)
**Sintoma:** Muitas ideias, pouca execução.

**Remédio:** Triage brutal. Fechar ou mover para `Icebox` (backlog frio).

---

### 🔴 Muitas issues Blocked (> 10)
**Sintoma:** Dependências mal gerenciadas ou gargalos.

**Remédio:** Weekly review of Blocked. Se algo está bloqueado > 2 semanas, priorizar desbloqueio.

---

### 🔴 Cycle Time > 4 semanas
**Sintoma:** Issues muito grandes ou pouco foco.

**Remédio:** Quebrar issues grandes. Aplicar WIP limit rigoroso.

---

### 🔴 DoD não sendo seguido
**Sintoma:** PRs sendo mergeados sem testes ou docs.

**Remédio:** Code review mais rigoroso. Automatizar checks no CI/CD.

---

## 📚 REFERÊNCIAS

* [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
* [Keep a Changelog](https://keepachangelog.com/)
* [Semantic Versioning](https://semver.org/)
* [Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)

---

**Governança não é burocracia. É garantir que todos os projetos terminam juntos.**

🎯🔄
