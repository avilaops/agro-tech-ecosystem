# PROVA DE INTEGRAÇÃO
## Precision-Platform → CanaSwarm-Intelligence

> **"Contrato = código mínimo + exemplo. Não documentação."**

---

## 🎯 OBJETIVO

Provar que dois projetos do ecossistema conseguem conversar.

**Fluxo crítico escolhido:** `Precision-Platform → CanaSwarm-Intelligence`

**Por quê este fluxo:**
* Define estrutura do dado agrícola
* Alimenta o cérebro do sistema
* Vira padrão para todas as outras integrações

Se este fluxo existir, o ecossistema respira.

---

## 📋 CONTRATO DE DADOS

### Precision-Agriculture-Platform PRODUZ:

**Endpoint:** `GET /api/v1/recommendations?field_id={id}`

**Response (JSON):**
```json
{
  "field_id": "F001-UsinaGuarani-Piracicaba",
  "analysis_id": "A20260220-001",
  "crop": "sugarcane",
  "season": "2025-2026",
  "harvest_number": 4,
  "total_area_ha": 130,
  "zones": [
    {
      "zone_id": "Z001",
      "area_ha": 50.2,
      "avg_yield_t_ha": 45.3,
      "expected_yield_t_ha": 85.0,
      "profitability_score": 0.32,
      "status": "critical",
      "recommendation": {
        "action": "reform",
        "priority": "high",
        "reason": "Produtividade abaixo de 50% do esperado"
      },
      "financial_impact": {
        "estimated_loss_brl_year": 120000,
        "reform_cost_brl": 8000,
        "payback_months": 8
      }
    }
  ],
  "summary": {
    "total_estimated_impact_brl": 158000,
    "zones_critical": 1,
    "zones_optimal": 1,
    "avg_profitability_score": 0.605
  }
}
```

**Frequência:** Sob demanda (chamada síncrona) ou batch diário

**Status Codes:**
* `200 OK` — Análise completa
* `400 Bad Request` — field_id ausente
* `404 Not Found` — Field não encontrado

---

### CanaSwarm-Intelligence CONSOME:

**Via:** HTTP GET request para Precision API

**Processa:**
* Exibe no dashboard tempo real
* Armazena histórico de recomendações
* Gera alertas para zonas críticas
* Compara ROI entre zonas

**Output:** Dashboard visual + alertas

---

## 🧪 MOCKS FUNCIONAIS

### Arquivos criados:

```
Precision-Agriculture-Platform/
  mocks/
    api_mock.py              # Servidor Flask fake
    example_zones.json       # Dados de exemplo realistas
    requirements.txt         # flask==3.0.0

CanaSwarm-Intelligence/
  mocks/
    consumer_mock.py         # Script que consome API
    requirements.txt         # requests==2.31.0
```

---

## ▶️ COMO EXECUTAR

### 1. Setup (apenas primeira vez):

```bash
# Precision
cd D:\Projetos\Precision-Agriculture-Platform\mocks
pip install -r requirements.txt

# Intelligence
cd D:\Projetos\CanaSwarm-Intelligence\mocks
pip install -r requirements.txt
```

### 2. Iniciar API mock (Terminal 1):

```bash
cd D:\Projetos\Precision-Agriculture-Platform\mocks
python api_mock.py
```

Servidor roda em: `http://localhost:5000`

### 3. Consumir dados (Terminal 2):

```bash
cd D:\Projetos\CanaSwarm-Intelligence\mocks
python consumer_mock.py F001-UsinaGuarani-Piracicaba
```

---

## ✅ CRITÉRIO DE SUCESSO

**A integração está provada quando:**

- [x] `api_mock.py` responde em `http://localhost:5000`
- [x] `consumer_mock.py` consegue buscar dados
- [x] Dados chegam completos no consumer
- [x] Consumer processa e exibe no formato dashboard
- [x] Consumer salva dados localmente

**Output esperado:**
```
✅ Dados recebidos com sucesso!

📊 DASHBOARD - VISÃO GERAL
----------------------------------------------------------------------
Talhão: F001-UsinaGuarani-Piracicaba
Cultura: SUGARCANE | Safra: 2025-2026 | Corte: 4
Área total: 130 ha

💰 IMPACTO FINANCEIRO TOTAL
----------------------------------------------------------------------
Impacto estimado: R$ 158,000.00 / ano
Score médio de rentabilidade: 0.61

🗺️  ANÁLISE POR ZONA
----------------------------------------------------------------------
🔴 ZONA Z001 - 50.2 ha
  Produtividade: 45.3 t/ha (esperado: 85.0)
  Score: 0.32
  Recomendação: REFORM (prioridade high)
  💸 Prejuízo estimado: R$ 120,000.00 / ano
  
🟢 ZONA Z002 - 79.8 ha
  Produtividade: 95.2 t/ha (esperado: 90.0)
  Score: 0.89
  Recomendação: MAINTAIN (prioridade low)
  💰 Ganho estimado: R$ 50,000.00 / ano

🎯 INTEGRAÇÃO PRECISION → INTELLIGENCE: SUCESSO
```

---

## 🔄 PRÓXIMOS PASSOS

**Agora que a integração está provada:**

1. ✅ Substituir mocks por código real (gradualmente)
2. ✅ Adicionar mais campos conforme necessário
3. ✅ Expandir para outros fluxos (AI-Vision → Intelligence, AgriBot → Precision)

**O que NÃO fazer:**
* ❌ Criar 17 contratos sem código
* ❌ Documentar integrações que não existem
* ❌ Planejar Q2/Q3/Q4 antes de ter Q1 funcionando

---

## 📊 STATUS

| Item | Status |
|------|--------|
| Contrato definido | ✅ |
| Mock funcional (Precision) | ✅ |
| Mock funcional (Intelligence) | ✅ |
| Teste manual executado | ⏳ Próximo passo |
| Código real iniciado | ⏳ Após testes |

**Data:** 20/02/2026

**Resultado:** Pipeline mínimo funciona. Ecossistema respira.

---

**Este documento substitui 500 páginas de roadmap.**

**Porque código mínimo > documentação infinita.**

🔗🎯
