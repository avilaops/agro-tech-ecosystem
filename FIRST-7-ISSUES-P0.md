# PRIMEIRAS 7 ISSUES P0
## Issues que devem ser criadas AGORA para começar a orquestração

> **Como usar:** Copie cada issue abaixo e crie no repositório `agro-tech-ecosystem`

---

## ISSUE #1: **Criar Taxonomia de Labels**

**Template:** ⚙️ Feature/Task

**Título:** `[INFRA] Criar taxonomia de labels em todos os repositórios`

**Repositório:** agro-tech-ecosystem

**Objetivo:**
Padronizar labels em todos os 16+ repos para garantir consistência e permitir filtros cross-repo no GitHub Project.

**Inputs:**
* Lista de labels definidas em `GOVERNANCE.md`
* Script `scripts/setup-labels.ps1`
* Acesso ao GitHub CLI (gh)

**Outputs:**
* Todas as labels criadas em todos os repos
* Relatório de sucesso/falha por repo

**Critério de Aceite:**
- [ ] Script roda sem erros
- [ ] 40+ labels criadas em cada um dos 17 repositórios
- [ ] Labels aparecem corretamente no GitHub UI
- [ ] Cores e descrições padronizadas

**Classificação:**
* **Layer:** Infra
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** XS (< 1 dia)
* **Impact:** High (bloqueia Issue #3)

**Dependências:**
* Nenhuma (pode começar agora)

**Desbloqueia:**
* Issue #3 (Project Central precisa de labels prontas)

**Spec Técnica:**
```powershell
# Executar
cd D:\Projetos
.\scripts\setup-labels.ps1
```

---

## ISSUE #2: **Criar Templates de Issue**

**Template:** ⚙️ Feature/Task

**Título:** `[INFRA] Criar templates de issue em todos os repositórios`

**Repositório:** agro-tech-ecosystem

**Objetivo:**
Copiar templates de issue (`demand.yml` e `feature.yml`) para todos os repos para padronizar intake de demandas e features.

**Inputs:**
* Templates em `D:\Projetos\.github\ISSUE_TEMPLATE\`
* Lista de repositórios

**Outputs:**
* `.github/ISSUE_TEMPLATE/demand.yml` em cada repo
* `.github/ISSUE_TEMPLATE/feature.yml` em cada repo
* `.github/ISSUE_TEMPLATE/config.yml` em cada repo

**Critério de Aceite:**
- [ ] Templates copiados para todos os 17 repos
- [ ] Ao criar nova issue, templates aparecem como opções
- [ ] Templates preenchem campos corretamente

**Classificação:**
* **Layer:** Infra
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** S (1-3 dias)
* **Impact:** High (padroniza intake)

**Dependências:**
* Nenhuma

**Desbloqueia:**
* Criação de issues padronizadas em todos os projetos

**Spec Técnica:**
```powershell
# Para cada repo:
# 1. Copiar .github/ISSUE_TEMPLATE/ para o repo
# 2. git add, commit, push
# 3. Verificar no GitHub UI
```

---

## ISSUE #3: **Configurar GitHub Project Central**

**Template:** ⚙️ Feature/Task

**Título:** `[INFRA] Configurar GitHub Project central cross-repo`

**Repositório:** agro-tech-ecosystem

**Objetivo:**
Criar e configurar o GitHub Project centralizado que controlará todos os 16+ repositórios.

**Inputs:**
* Guia `GITHUB-PROJECTS-SETUP.md`
* Acesso admin ao GitHub

**Outputs:**
* Project "Agro-Tech Ecosystem" criado
* 7 custom fields configurados
* 5 views criadas
* 4 automações configuradas
* 17 repositórios adicionados

**Critério de Aceite:**
- [ ] Project acessível em https://github.com/orgs/avilaops/projects/X
- [ ] Fields: Status, Priority, Layer, Quarter, Effort, Impact, Blocked By
- [ ] Views: Board, Roadmap, By Layer, Blocked, This Week
- [ ] Automações: Auto-add, Move to In Review, Move to Done, Closed→Done
- [ ] Todos os 17 repos podem adicionar issues ao project

**Classificação:**
* **Layer:** Infra
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** M (1 semana)
* **Impact:** High (core da orquestração)

**Dependências:**
* Issue #1 (labels prontas)

**Desbloqueia:**
* Issue #4, #5, #6, #7 (todas as outras precisam do Project funcionando)

**Spec Técnica:**
Seguir: `GITHUB-PROJECTS-SETUP.md` passo a passo

---

## ISSUE #4: **Documentar Definition of Done**

**Template:** ⚙️ Feature/Task

**Título:** `[DOCS] Atualizar ECOSYSTEM-ORCHESTRATOR.md com processo de governança`

**Repositório:** agro-tech-ecosystem

**Objetivo:**
Integrar as regras de governança (`GOVERNANCE.md`) no documento principal do ecossistema para que todos sigam o mesmo processo.

**Inputs:**
* `GOVERNANCE.md` existente
* `ECOSYSTEM-ORCHESTRATOR.md` existente

**Outputs:**
* `ECOSYSTEM-ORCHESTRATOR.md` atualizado com seção "Como Funciona o Processo"
* Link para `GOVERNANCE.md` em todos os READMEs relevantes

**Critério de Aceite:**
- [ ] Seção "Processo de Trabalho" adicionada ao ECOSYSTEM-ORCHESTRATOR
- [ ] Link para GOVERNANCE.md em todos os 4 projetos core
- [ ] DoD claramente definido e referenciado

**Classificação:**
* **Layer:** Infra
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** XS (< 1 dia)
* **Impact:** Medium (clareza de processo)

**Dependências:**
* Nenhuma

**Desbloqueia:**
* Equipe sabe como trabalhar

---

## ISSUE #5: **[Precision Platform] Ingest + Report Skeleton** ✅ COMPLETE

**Status:** ✅ **IMPLEMENTED** (2026-02-20)  
**See:** `Precision-Agriculture-Platform/IMPLEMENTATION_SUMMARY.md`

**Template:** ⚙️ Feature/Task

**Título:** `[FEATURE] Precision Platform: Criar pipeline de ingestão e relatório básico`

**Repositório:** Precision-Agriculture-Platform

**Objetivo:**
MVP do Precision Platform: ingerir dados de colheita (CSV/shapefile) e gerar relatório básico com mapa de zonas.

**Inputs:**
* Arquivo CSV ou shapefile com dados de colheita (produtividade por ponto GPS)
* Limite do talhão (shapefile)

**Outputs:**
* Script Python que:
  * Lê arquivos de entrada
  * Valida dados (outliers, densidade mínima)
  * Gera mapa de zonas (interpolação IDW simples)
  * Exporta relatório HTML com mapa interativo

**Critério de Aceite:**
- [x] Script roda sem erros com dataset de teste ✅
- [x] Processa 1.000+ pontos em < 2 minutos ✅ (1,500 points in ~1.5 min)
- [x] Gera mapa visual (matplotlib ou folium) ✅ (Folium interactive maps)
- [x] Relatório HTML exportado ✅ (Self-contained HTML with embedded maps)
- [x] README com exemplo de uso ✅ (Complete documentation + 3 examples)
- [x] 1 teste unitário (validação de dados) ✅ (10 unit tests in test_ingest.py)

**Implementation Summary:**
* **Files Created:** 11 (src, tests, examples, docs)
* **Lines of Code:** ~1,700
* **Features Delivered:** 
  - CSV/Shapefile ingestion with validation
  - IDW interpolation + K-Means clustering
  - Interactive HTML reports (folium + matplotlib)
  - Management zone shapefile export
  - Complete unit test coverage
* **Performance:** 1,500 GPS points processed in <2 minutes
* **Output:** HTML report + shapefile + statistics

See [IMPLEMENTATION_SUMMARY.md](Precision-Agriculture-Platform/IMPLEMENTATION_SUMMARY.md) for full details.

**Classificação:**
* **Layer:** Decision
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** L (2-4 semanas)
* **Impact:** High (MVP do projeto core)

**Dependências:**
* Nenhuma (pode começar agora)
* Dataset de teste (criar ou buscar público)

**Desbloqueia:**
* Integração com CanaSwarm-Intelligence (Q2)
* Geração de prescrição VRA (próxima feature)

**Spec Técnica:**
```python
# Stack:
# - Python 3.10+
# - GeoPandas, Shapely, Rasterio
# - scipy (interpolação IDW)
# - folium ou matplotlib (visualização)

# Estrutura:
# src/ingest.py — leitura e validação
# src/zones.py — interpolação e clusterização
# src/report.py — geração de HTML
# tests/ — testes unitários
# examples/ — notebook com exemplo
```

---

## ISSUE #6: **[AI-Vision] Pipeline Placeholder + Interface**

**Template:** ⚙️ Feature/Task

**Título:** `[FEATURE] AI-Vision: Criar pipeline placeholder e definir contrato de dados`

**Repositório:** AI-Vision-Agriculture

**Objetivo:**
Definir o contrato de entrada/saída do AI-Vision e criar pipeline skeleton (sem modelo treinado ainda).

**Inputs:**
* Imagem RGB (JPG/PNG)
* Metadados GPS (lat, lon, timestamp)

**Outputs:**
* JSON com análise:
  ```json
  {
    "image_id": "img_001.jpg",
    "gps": {"lat": -21.1234, "lon": -47.5678},
    "timestamp": "2026-02-20T10:30:00Z",
    "maturity": {
      "level": "ready_to_harvest",
      "confidence": 0.85,
      "estimated_atr": 14.2
    },
    "pests": [],
    "diseases": []
  }
  ```

**Critério de Aceite:**
- [ ] Script aceita imagem + GPS como entrada
- [ ] Retorna JSON no formato especificado (placeholder: valores mockados)
- [ ] API REST (FastAPI) expõe endpoint `/analyze`
- [ ] README com exemplo de uso
- [ ] Contrato de dados documentado (OpenAPI spec)

**Classificação:**
* **Layer:** Sensing
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** M (1 semana)
* **Impact:** High (define integração)

**Dependências:**
* Nenhuma (contrato pode ser definido antes do modelo)

**Desbloqueia:**
* CanaSwarm-Intelligence pode começar integração (Q2)
* Treinamento de modelo ML (próxima fase)

**Spec Técnica:**
```python
# Stack:
# - Python 3.10+
# - FastAPI
# - Pillow (processamento de imagem)
# - pydantic (validação de dados)

# Estrutura:
# src/api.py — FastAPI app
# src/models.py — pydantic models (contrato)
# src/analyzer.py — placeholder (retorna mock)
# tests/ — testes de API
# docs/openapi.json — spec da API
```

---

## ISSUE #7: **[AgriBot] Spec de Telemetria**

**Template:** ⚙️ Feature/Task

**Título:** `[FEATURE] AgriBot: Definir spec de telemetria e criar simulator`

**Repositório:** AgriBot-Retrofit

**Objetivo:**
Definir o contrato de telemetria que o AgriBot vai gerar e criar simulador para testes.

**Inputs:**
* Prescrição VRA (shapefile com dose por zona)

**Outputs:**
* Stream de telemetria (MQTT ou HTTP POST):
  ```json
  {
    "device_id": "agribot_001",
    "timestamp": "2026-02-20T10:35:12Z",
    "gps": {"lat": -21.1234, "lon": -47.5678, "precision": 0.03},
    "operation": "fertilizer_application",
    "zone_id": "Z003",
    "prescribed_dose": 120,
    "applied_dose": 118,
    "speed_kmh": 8.5,
    "tank_level_pct": 67
  }
  ```

**Critério de Aceite:**
- [ ] Spec de telemetria documentado (formato JSON)
- [ ] Simulador roda e gera telemetria mock (1 ponto/segundo)
- [ ] Pode escolher entre MQTT ou HTTP POST
- [ ] README com exemplo de uso
- [ ] Contrato de dados documentado

**Classificação:**
* **Layer:** Execution
* **Priority:** P0
* **Quarter:** Q1-2026
* **Effort:** S (1-3 dias)
* **Impact:** High (define integração)

**Dependências:**
* Nenhuma (contrato pode ser definido antes do hardware)

**Desbloqueia:**
* Precision Platform pode simular integração (Q2)
* Hardware real pode usar o mesmo contrato

**Spec Técnica:**
```python
# Stack:
# - Python 3.10+
# - paho-mqtt (MQTT client) OU requests (HTTP)
# - pydantic (validação)

# Estrutura:
# src/telemetry_spec.py — pydantic models
# src/simulator.py — gera telemetria mock
# tests/ — testes de formato
# docs/telemetry_spec.md — documentação
```

---

## 📊 RESUMO DAS 7 ISSUES P0

| # | Título | Layer | Effort | Dependências | Desbloqueia |
|---|--------|-------|--------|--------------|-------------|
| 1 | Taxonomia de Labels | Infra | XS | Nenhuma | #3 |
| 2 | Templates de Issue | Infra | S | Nenhuma | Intake padronizado |
| 3 | GitHub Project Central | Infra | M | #1 | #4, #5, #6, #7 |
| 4 | Definition of Done | Infra | XS | Nenhuma | Clareza de processo |
| 5 | Precision: Ingest + Report | Decision | L | Nenhuma | Integração Q2 |
| 6 | AI-Vision: Pipeline + Interface | Sensing | M | Nenhuma | Integração Q2 |
| 7 | AgriBot: Spec Telemetria | Execution | S | Nenhuma | Integração Q2 |

---

## 🚀 ORDEM DE EXECUÇÃO RECOMENDADA

### Semana 1-2:
* Issue #1 (Labels) — começar AGORA
* Issue #2 (Templates) — começar AGORA
* Issue #4 (DoD em docs) — começar AGORA

### Semana 2-3:
* Issue #3 (Project Central) — depois de #1

### Semana 1-4 (paralelo):
* Issue #5 (Precision MVP) — começar AGORA
* Issue #6 (AI-Vision contrato) — começar AGORA
* Issue #7 (AgriBot contrato) — começar AGORA

**Percebe o ponto?**
* Infra + Docs (1, 2, 3, 4) podem ser feitos rápido e em paralelo
* MVPs técnicos (5, 6, 7) começam JÁ, mas demoram mais
* Ao término da semana 4, você tem:
  * ✅ Governança funcionando
  * ✅ Project controlando tudo
  * ✅ 3 contratos de integração definidos
  * ✅ 1 MVP funcional (Precision Platform)

---

## 📝 COMO CRIAR ESSAS ISSUES

### Opção 1: Manual (UI do GitHub)
1. Ir em cada repositório
2. Clicar em "Issues" → "New issue"
3. Escolher template relevante
4. Copiar e colar o conteúdo acima
5. Adicionar ao Project "Agro-Tech Ecosystem"

### Opção 2: Automatizado (gh CLI)
```powershell
# Criar arquivo com o corpo da issue
$issueBody = Get-Content "D:\Projetos\issues\issue-001-labels.md" -Raw

# Criar issue via CLI
gh issue create `
  --repo avilaops/agro-tech-ecosystem `
  --title "[INFRA] Criar taxonomia de labels" `
  --body $issueBody `
  --label "P0,layer:infra,Q1-2026,effort:XS" `
  --assignee @me

# Repetir para as outras 6 issues
```

---

**Com essas 7 issues P0 criadas e priorizadas, a orquestração pode começar de verdade.**

🚀🎯
