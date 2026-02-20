# DEPENDENCY CONTROL
## Rastreamento de Dependências Entre Projetos

> **"O problema não é gerenciar projetos. É gerenciar dependências entre projetos."**

---

## 🎯 MUDANÇA DE PARADIGMA

### ❌ **Sistema tradicional gerencia:**
* Tarefas
* Issues individuais
* Commits
* PRs

### ✅ **Orquestração de ecossistema gerencia:**
* **Quem depende de quem**
* **Quem trava quem**
* **Quem está pronto pra integrar**
* **Contratos de dados entre projetos**

---

## 🧠 AS 4 CAMADAS REVISADAS

### CAMADA 1 — DECISION (Cérebro)

**Projetos:**
* **CanaSwarm-Intelligence** — Dashboard + analytics
* **Precision-Agriculture-Platform** — Motor econômico + ROI
* **AI-Vision-Agriculture** — Análise de imagens (também Sensing)
* **Autonomous-Agent-Framework** — Framework de agentes autônomos

**Papel:** Transformam dados em decisão

**Prioridade:** MÁXIMA — tudo converge aqui

---

### CAMADA 2 — SENSING (Entrada de Dados)

**Projetos:**
* **CanaSwarm-Vision** — Processamento edge de imagens
* **AI-Vision-Agriculture** — Modelos ML de visão (está em 2 camadas)
* **CanaSwarm-3D-Models** — Modelos CAD para simulação
* **Robotics-Swarm-Simulator** — Simulação de comportamento
* ~~**Security-Threat-Intel**~~ (clonado, não nosso — monitoramento infra)

**Papel:** Coleta dados do mundo real

**Sem isso:** O cérebro fica cego

---

### CAMADA 3 — EXECUTION (Hardware/Campo)

**Projetos:**
* **AgriBot-Retrofit** — Tratores automatizados
* **CanaSwarm-MicroBot** — Robôs de campo
* **CanaSwarm-Swarm-Coordinator** — Orquestração de enxame
* **CanaSwarm-Core** — Sistema central de coordenação

**Papel:** Impacto físico no mundo real

**Sem isso:** Sistema só analisa, não age

---

### CAMADA 4 — INFRASTRUCTURE (Plataforma)

**Projetos:**
* **MicroGrid-Manager** — Gestão de energia
* **CanaSwarm-Solar-Manager** — Energia solar
* **Industrial-Automation-OS** — Automação industrial
* **Agro-Machinery-Marketplace** — Comercialização
* ~~**Vector-DB**~~ (clonado, não nosso)
* **CanaSwarm-Docs** — Documentação + governança

**Papel:** Mantém o resto funcionando

**Sem isso:** Nada escala, nada funciona em produção

---

## 🔗 MAPA DE DEPENDÊNCIAS CRÍTICAS

### ⚠️ DEPENDÊNCIAS BLOQUEADORAS (P0)

**Se não existir, trava tudo:**

| Projeto Dependente | DEPENDE DE | O QUÊ | Formato | Status |
|--------------------|------------|-------|---------|--------|
| **CanaSwarm-Intelligence** | Precision-Platform | Recomendações por zona | API REST /recommendations | 🔴 Não existe |
| **CanaSwarm-Intelligence** | AI-Vision | Análise de imagens | API REST /analyze | 🔴 Não existe |
| **CanaSwarm-Intelligence** | AgriBot | Telemetria de máquinas | MQTT ou HTTP POST | 🔴 Não existe |
| **Precision-Platform** | CanaSwarm-Intelligence | Dados de campo | API REST /field_data | 🔴 Não existe |
| **Precision-Platform** | AgriBot | Mapa aplicado vs. prescrito | Shapefile ou GeoJSON | 🔴 Não existe |
| **AI-Vision** | CanaSwarm-Vision | Imagens processadas edge | Object Storage (S3/MinIO) | 🔴 Não existe |
| **AgriBot** | Precision-Platform | Prescrição VRA | Shapefile ou ISOXML | 🔴 Não existe |
| **CanaSwarm-MicroBot** | Swarm-Coordinator | Tarefas alocadas | MQTT /tasks/{bot_id} | 🔴 Não existe |
| **CanaSwarm-MicroBot** | Solar-Manager | Status de recarga | MQTT /charging/{station_id} | 🔴 Não existe |
| **Swarm-Coordinator** | CanaSwarm-Intelligence | Zonas a monitorar | API REST /zones | 🔴 Não existe |

**LEGENDA:**
* 🔴 Não existe — Contrato não definido
* 🟡 Spec pronta — Contrato definido, não implementado
* 🟢 Funcional — Integração testada e funcionando

---

## 📊 ANÁLISE DE BLOQUEIO

### 🚨 **GARGALOS ATUAIS (priorizar AGORA):**

**1. CanaSwarm-Intelligence é o HUB CENTRAL**
* **Depende de:** 3 projetos (Precision, AI-Vision, AgriBot)
* **Bloqueia:** Swarm-Coordinator, todo ecossistema
* **Risco:** Se não definir contratos, NADA integra

**2. Precision-Platform é o CÉREBRO**
* **Depende de:** 2 projetos (Intelligence, AgriBot)
* **Bloqueia:** AgriBot (prescrições), Intelligence (recomendações)
* **Risco:** MVP pode rodar standalone, mas integração trava Q2

**3. AI-Vision é SENSOR CRÍTICO**
* **Depende de:** 1 projeto (CanaSwarm-Vision)
* **Bloqueia:** Intelligence (sem análise visual), MicroBot (sem visão)
* **Risco:** Sem isso, sistema fica "cego" no campo

---

## ✅ PRIMEIRA ONDA DE CONTRATOS (Q1 2026)

**Objetivo:** Destravar as 3 integrações críticas

### Contrato #1: **Precision-Platform → CanaSwarm-Intelligence**

**Status:** 🔴 Não existe

**Prioridade:** P0

**O que definir:**
* **API REST** em Precision-Platform
* **Endpoint:** `GET /api/v1/recommendations?zone_id={id}`
* **Resposta:**
  ```json
  {
    "zone_id": "Z001",
    "recommendations": [
      {
        "type": "fertilizer",
        "dose_kg_ha": 120,
        "product": "NPK 10-20-10",
        "roi_estimated": 18.5,
        "priority": "high"
      }
    ]
  }
  ```

**Issue:** [ECOSYSTEM INIT] Precision-Platform: Definir API de recomendações

---

### Contrato #2: **AI-Vision → CanaSwarm-Intelligence**

**Status:** 🔴 Não existe

**Prioridade:** P0

**O que definir:**
* **API REST** em AI-Vision
* **Endpoint:** `POST /api/v1/analyze`
* **Request:**
  ```json
  {
    "image_url": "s3://bucket/images/img_001.jpg",
    "gps": {"lat": -21.1234, "lon": -47.5678},
    "timestamp": "2026-02-20T10:30:00Z"
  }
  ```
* **Response:**
  ```json
  {
    "maturity": {"level": "ready", "confidence": 0.85, "atr_estimated": 14.2},
    "pests": [],
    "diseases": []
  }
  ```

**Issue:** [ECOSYSTEM INIT] AI-Vision: Definir API de análise

---

### Contrato #3: **Precision-Platform → AgriBot**

**Status:** 🔴 Não existe

**Prioridade:** P0

**O que definir:**
* **Arquivo shapefile** exportado por Precision
* **Formato:** Shapefile com colunas: `zone_id`, `dose_kg_ha`, `product`
* **AgriBot** importa e executa
* **AgriBot retorna:** Shapefile com colunas: `zone_id`, `dose_applied`, `timestamp`

**Issue:** [ECOSYSTEM INIT] Precision-Platform: Exportar prescrição VRA (shapefile)

---

## 🎯 CONTROLE DE DEPENDÊNCIAS NO GITHUB PROJECT

### Custom Field: **Blocked By**

**Tipo:** Text

**Formato:** `#123` ou `repo#456`

**Exemplo:** Issue "Precision MVP" está com `Blocked By: #45` (aguardando dataset)

---

### View: **Dependency Graph**

**Filtro:** Mostrar issues com campo `Blocked By` preenchido

**Agrupar por:** `Blocked By`

**Resultado:** Ver quantas issues cada bloqueio está travando

**Exemplo:**
```
Blocked By: CanaSwarm-Intelligence#12 (API não existe)
  ├─ Precision-Platform#5 (precisa chamar API)
  ├─ AI-Vision#8 (precisa enviar dados)
  └─ AgriBot#3 (precisa receber comandos)
```

👉 Se você resolver `Intelligence#12`, desbloqueia 3 projetos.

---

### View: **Ready to Integrate**

**Filtro:**
* `Status: Done` OU `Status: Ready`
* `Layer: Decision` OU `Layer: Sensing`
* Tem tag `contract-defined`

**Objetivo:** Ver o que está pronto para começar integrações

---

## 📋 CHECKLIST DE CONTRATO DE DADOS

Para cada projeto, criar issue:

**Título:** `[ECOSYSTEM INIT] Definir contrato de dados do projeto`

**Conteúdo:**

```markdown
## O que este projeto RECEBE

* **De qual projeto:** (nome)
* **Formato:** (JSON, shapefile, MQTT, etc.)
* **Frequência:** (tempo real, batch, sob demanda)
* **Exemplo:**
  ```
  (colar exemplo)
  ```

---

## O que este projeto PRODUZ

* **Para qual projeto:** (nome)
* **Formato:** (JSON, shapefile, MQTT, etc.)
* **Frequência:** (tempo real, batch, sob demanda)
* **Exemplo:**
  ```
  (colar exemplo)
  ```

---

## Dependências Bloqueadoras

- [ ] Projeto X precisa estar pronto (Issue #___)
- [ ] Dataset Y precisa existir
- [ ] API Z precisa estar deployed

---

## Critério de Aceite

- [ ] Contrato documentado (spec OpenAPI ou equivalente)
- [ ] Exemplo funcional (mock data)
- [ ] Testes de validação (schema validation)
- [ ] README atualizado

```

---

## 🚦 ORDEM DE ATIVAÇÃO DE CONTRATOS

### Semana 1-2 (AGORA):
1. ✅ Criar issue de contrato em cada um dos 17 repos
2. ✅ Aplicar labels: `contract`, `P0`, `layer:X`
3. ✅ Adicionar todas ao Project Central

### Semana 2-3:
4. ⏳ Definir contratos dos 3 projetos core:
   * Precision-Platform
   * AI-Vision-Agriculture
   * AgriBot-Retrofit
5. ⏳ Revisar contratos em review técnico (1h cada)

### Semana 3-4:
6. ⏳ Implementar mocks/stubs dos contratos
7. ⏳ Testes de validação (schema, formato)
8. ⏳ Documentação (OpenAPI specs)

### Semana 4+:
9. ⏳ Começar integrações reais
10. ⏳ Testes end-to-end

---

## 📊 MÉTRICAS DE DEPENDENCY HEALTH

**Acompanhar semanalmente:**

| Métrica | Meta | Atual | Status |
|---------|------|-------|--------|
| **Contratos definidos** | 10/17 (60%) | 0/17 | 🔴 |
| **Issues bloqueadas** | < 5 | ? | 🟡 |
| **Dependências resolvidas** | > 3/semana | 0 | 🔴 |
| **Integrações funcionais** | 3 (Q1) | 0 | 🔴 |
| **Tempo médio pra desbloquear** | < 3 dias | ? | 🟡 |

---

## 🎖️ PRINCÍPIO DO CONTRATO PRIMEIRO

**Regra de ouro:**

📌 **Nenhuma integração começa sem contrato definido.**

**Por quê:**
* Evita retrabalho
* Permite desenvolvimento paralelo
* Facilita testes (mock data)
* Documenta dependências
* Permite mudança de implementação sem quebrar integração

**Fluxo certo:**
1. Definir contrato (spec)
2. Implementar mock (fake data)
3. Validar com ambos os lados
4. Implementar de verdade
5. Testar integração

**Fluxo errado:**
1. Implementar de um lado
2. Descobrir que o outro lado esperava formato diferente
3. Refazer tudo
4. Brigar sobre qual lado muda
5. Perder 2 semanas

---

## 🔗 EXEMPLO DE CONTRATO BEM DEFINIDO

**Projeto:** Precision-Agriculture-Platform

**Endpoint:** `POST /api/v1/zones/analyze`

**Request:**
```json
{
  "field_id": "F001",
  "yield_map": {
    "format": "geojson",
    "url": "s3://bucket/yield_maps/f001_2025.geojson"
  },
  "soil_data": {
    "format": "csv",
    "url": "s3://bucket/soil/f001_grid.csv"
  },
  "crop": "sugarcane",
  "season": "2025-2026"
}
```

**Response:**
```json
{
  "field_id": "F001",
  "analysis_id": "A123",
  "zones": [
    {
      "zone_id": "Z001",
      "area_ha": 50,
      "avg_yield_t_ha": 45,
      "profitability_score": 0.32,
      "recommendation": "reform",
      "estimated_loss_brl_year": 120000
    },
    {
      "zone_id": "Z002",
      "area_ha": 80,
      "avg_yield_t_ha": 95,
      "profitability_score": 0.89,
      "recommendation": "maintain",
      "estimated_gain_brl_year": 450000
    }
  ],
  "total_area_ha": 130,
  "total_estimated_impact_brl": 330000
}
```

**Status Codes:**
* `200 OK` — Análise concluída
* `202 Accepted` — Análise em andamento (processamento assíncrono)
* `400 Bad Request` — Formato de dados inválido
* `404 Not Found` — Field não encontrado

**Rate Limit:** 10 requests/min

**Latency Target:** < 30s para campos até 1.000 ha

**Versionamento:** `/api/v1/` (breaking changes → v2)

---

**Dependências não são problema. Dependências INVISÍVEIS são o problema.**

**Este documento as torna visíveis.**

🔗🎯
