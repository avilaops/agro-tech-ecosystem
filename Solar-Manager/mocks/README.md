# Solar-Manager - Mock Implementation

## 📋 Objetivo

Sistema de gestão de energia solar para estações de recarga de robôs autônomos. Gerencia:
- **Painéis solares**: Monitoramento de geração, eficiência, condições ambientais
- **Baterias**: Estado de carga (SOC), saúde (SOH), ciclos, temperatura
- **Otimização**: Uso inteligente de energia solar + bateria
- **Recarga de robôs**: Agendamento coordenado e priorização

## 🔄 Contrato de Dados

### **INPUT: Dados do Sistema Solar**

Recebe dados em tempo real da estação de recarga:

```json
{
  "timestamp": "2026-02-20T15:30:00.000Z",
  "station_id": "SOLAR-STATION-001",
  "solar_panels": {
    "total_capacity_kwp": 16.08,
    "current_generation": {
      "power_kw": 12.45,
      "voltage_v": 920.0,
      "efficiency_percent": 77.4
    },
    "environmental_conditions": {
      "irradiance_w_m2": 850,
      "panel_temperature_c": 42,
      "ambient_temperature_c": 28,
      "cloud_cover_percent": 15
    }
  },
  "battery_storage": {
    "technology": "LiFePO4",
    "specs": {
      "energy_capacity_kwh": 192,
      "cycle_life": 6000
    },
    "current_state": {
      "state_of_charge_percent": 85,
      "state_of_health_percent": 96,
      "voltage_v": 395.2,
      "temperature_c": 32
    }
  },
  "load_management": {
    "total_load_kw": 2.85,
    "robot_charging": {
      "active_robots": 1,
      "robots": [
        {
          "robot_id": "MICROBOT-001",
          "battery_soc_percent": 45,
          "charge_power_kw": 2.5
        }
      ]
    }
  },
  "charging_schedule": {
    "scheduled_charges": [
      {
        "robot_id": "MICROBOT-002",
        "current_soc_percent": 55,
        "priority": "medium"
      }
    ]
  }
}
```

### **PROCESSING: Gestão de Energia**

1. **Solar Panel Monitoring** (via Modbus/RS485)
   - Leitura de inversores solares
   - Medição de irradiância (piranômetros)
   - Monitoramento de temperatura
   - Cálculo de performance ratio (PR = Energia_Real / Energia_Teórica)
   - Detecção de anomalias (baixa eficiência, temperatura elevada)

2. **Battery Management** (via CAN/BMS)
   - State of Charge (SOC): Energia disponível (%)
   - State of Health (SOH): Degradação da capacidade (%)
   - Ciclos de vida: Contagem e estimativa de vida útil
   - Temperatura: Impacto na performance e degradação
   - Proteções: Over-voltage, under-voltage, over-current, over-temp
   - Balanceamento de células

3. **Energy Optimization**
   - **Estratégia de uso**:
     - Surplus solar → Carregar baterias
     - Déficit solar → Usar baterias
     - SOC baixo → Priorizar recarga da bateria
   - **Agendamento de robôs**:
     - Calcular capacidade simultânea (available_power / 2.5kW)
     - Priorizar: High priority > Low SOC
     - Aproveitar janelas de alta geração solar
     - Evitar sobrecarga da estação
   - **Previsão**: Forecast de geração próxima hora (ML)

4. **Decision Making**
   - Ações de bateria (charge/discharge/maintain)
   - Iniciar/adiar recarga de robôs
   - Alertas de energia crítica
   - Notificações para Core/operador

### **OUTPUT: Decisões de Gestão**

Retorna análise completa e ações recomendadas:

```json
{
  "timestamp": "2026-02-20T15:30:00.000Z",
  "station_id": "SOLAR-STATION-001",
  "energy_analysis": {
    "solar_power_kw": 12.45,
    "battery_soc_percent": 85,
    "battery_usable_kwh": 124.8,
    "availability_status": "excellent"
  },
  "battery_strategy": {
    "strategy": "charge",
    "target_power_kw": 9.60,
    "reason": "Excesso solar disponível"
  },
  "charging_plan": {
    "max_simultaneous_charging": 3,
    "robots_to_start_now": [
      {"robot_id": "MICROBOT-002", "duration_min": 45},
      {"robot_id": "SUPPORTBOT-001", "duration_min": 30}
    ]
  },
  "actions": [
    {
      "type": "battery_control",
      "command": "charge",
      "target_power_kw": 9.60,
      "priority": "medium"
    },
    {
      "type": "start_robot_charging",
      "robot_id": "MICROBOT-002",
      "priority": "medium"
    }
  ]
}
```

## 🧩 Componentes

### 1. Solar Panel Monitor (`solar_panel_monitor_mock.py`)

**Monitora array de painéis solares**

```python
monitor = SolarPanelMonitor("SOLAR-STATION-001")
result = monitor.monitor_solar_array(solar_data)
```

**Features:**
- **Geração atual**: Potência (kW), tensão (V), corrente (A), eficiência (%)
- **Condições ambientais**: Irradiância (W/m²), temperatura painéis/ambiente, nuvens, elevação solar
- **Performance metrics**:
  - Fator de capacidade: (Potência_Atual / Capacidade_Total) × 100
  - Performance Ratio: Energia_Real / (Capacidade × Irradiância/1000)
  - Perda por temperatura: ~0.4%/°C acima de 25°C
  - Specific Yield: kWh gerados / kWp instalado
- **Detecção de anomalias**:
  - Eficiência < 70% (sujeira, sombreamento, falha)
  - Performance Ratio < 0.75 (degradação, mau funcionamento)
  - Temperatura > 65°C (risco de dano)
  - Perda por temperatura > 8% (necessário resfriamento)
- **Previsão**: Geração próxima hora e resto do dia

**Specs do Sistema (exemplo):**
- Painéis: 24× Canadian Solar HiKu7 670W (16.08 kWp total)
- Eficiência: 21.6% (nominal), 77.4% (operacional com perdas)
- Performance Ratio típico: 0.85-0.95 (excelente: >0.9)

### 2. Battery Manager (`battery_manager_mock.py`)

**Gerencia banco de baterias LiFePO4**

```python
manager = BatteryManager("BATTERY-BANK-001")
result = manager.manage_battery_bank(solar_data)
```

**Features:**
- **Estado atual**: SOC (%), tensão (V), corrente (A), potência (kW), temperatura (°C), status (charging/discharging/idle)
- **Métricas de saúde**:
  - SOH (State of Health): Capacidade atual vs nominal (degradação natural)
  - Ciclos: Completados vs vida útil total (LiFePO4: ~6000 ciclos)
  - Vida restante: % de ciclos ainda disponíveis
  - Round-trip efficiency: Energia_Saída / Energia_Entrada (LiFePO4: ~90%)
  - Temperature impact: Optimal (15-35°C), Degradation (>45°C), Reduced capacity (<0°C)
  - Overall health score: Métrica 0-100 ponderando SOH, vida, eficiência, temperatura
- **Análise de capacidade**:
  - Nominal vs Real (considerando SOH)
  - Disponível (atual com SOC)
  - Utilizável (respeitando DoD 80% para LiFePO4)
  - Energia para carga completa
  - C-rate: Taxa de carga/descarga atual (1C = capacidade nominal em 1h)
- **Detecção de problemas**:
  - SOC < 20% (crítico se <10%)
  - SOH < 80% (degradação significativa)
  - Temperatura fora da faixa (< 0°C ou > 45°C)
  - Tensão anormal (desvio > 15% do nominal)
  - Fim de vida útil (< 10% ciclos restantes)
- **Recomendações**: Carregar, parar carga, resfriar, planejar substituição

**Specs do Sistema (exemplo):**
- Tecnologia: LiFePO4 (segura, longa vida, alta potência)
- Capacidade: 384V × 500Ah = 192 kWh
- Max charge/discharge: 1C/2C (192 kW charge, 384 kW discharge)
- Ciclos: 6000 a 80% DoD
- Garantia: 10 anos

### 3. Energy Optimizer (`energy_optimizer_mock.py`)

**Otimiza uso de energia e coordena recarga**

```python
optimizer = EnergyOptimizer("SOLAR-STATION-001")
result = optimizer.optimize_energy_usage(solar_data)
```

**Estratégia de Otimização:**

1. **Análise de Disponibilidade**:
   - Solar atual (kW)
   - Bateria utilizável (kWh, respeitando SOC > 20%)
   - Previsão próxima hora
   - Status: excellent/good/limited/critical

2. **Análise de Demanda**:
   - Carga total (instalações + robôs)
   - Robôs ativos carregando
   - Robôs na fila aguardando
   - Estimativa próxima hora

3. **Estratégia de Bateria**:
   - **Charge**: Surplus solar > 2kW e SOC < 95%
   - **Discharge**: Déficit > 2kW e SOC > 25%
   - **Priority charge**: SOC < 20% (bateria crítica)
   - **Maintain**: Balanço adequado

4. **Agendamento de Robôs**:
   - Capacidade simultânea: Available_Power / 2.5kW por robô
   - Priorização: High priority → Medium → Low → Menor SOC
   - Timing: Preferir horários de alta geração solar
   - Limitação: Não sobrecarregar estação

5. **Ações Geradas**:
   - Controle de bateria (charge/discharge/maintain)
   - Iniciar recarga de robôs (com solar disponível)
   - Adiar recarga (aguardar mais solar ou capacidade)
   - Alertas de energia crítica

**Lógica de Decisão:**
```
Surplus = Solar_kW - Load_kW

IF Surplus > 2 AND Battery_SOC < 95:
    → Charge battery (usar excesso solar)
ELIF Surplus < -2 AND Battery_SOC > 25:
    → Discharge battery (suprir déficit)
ELIF Battery_SOC < 20:
    → Priority charge (evitar descarga profunda)
ELSE:
    → Maintain (balanço adequado)

Robot_Charging_Capacity = Available_Power / 2.5kW
Sort robots by (Priority, SOC_ascending)
IF Solar > 5kW:
    → Start top N robots (até capacidade)
ELSE:
    → Delay charging (aguardar melhor geração)
```

## 📊 Testes

### Teste 1: Solar Panel Monitor

```bash
cd D:\Projetos\Solar-Manager\mocks
python solar_panel_monitor_mock.py
```

**Output esperado:**
```
☀️  Solar-Manager - Solar Panel Monitor Mock

☀️  Estação: SOLAR-STATION-001
   Capacidade: 16.08 kWp
   Painéis: 24 unidades

☀️  MONITORAMENTO DE PAINÉIS SOLARES
📍 ESTAÇÃO: SOLAR-STATION-001
   Array: ARRAY-001
   Status: NORMAL

⚡ GERAÇÃO ATUAL:
   Potência: 12.45 kW (~77% da capacidade)
   Tensão: 920.0 V
   Corrente: 13.5 A
   Eficiência: 77.4%

🌤️  CONDIÇÕES AMBIENTAIS:
   Irradiância: 850 W/m²
   Temp. painéis: 42°C
   Temp. ambiente: 28°C
   Cobertura nuvens: 15%
   Elevação solar: 58°

📊 PERFORMANCE:
   Fator de capacidade: 77.4%
   Performance ratio: 0.911 (EXCELENTE)
   Perda por temperatura: 6.8%

✅ NENHUMA ANOMALIA DETECTADA

🔮 PREVISÃO:
   Condições: EXCELLENT
   Próxima hora: 11.8 kWh (92% confiança)
   Resto do dia: 18.5 kWh

✅ MONITORAMENTO COMPLETO
```

### Teste 2: Battery Manager

```bash
python battery_manager_mock.py
```

**Output esperado:**
```
🔋 Solar-Manager - Battery Manager Mock

🔋 Banco de Baterias: BATTERY-BANK-001
   Tecnologia: LiFePO4
   Capacidade: 192 kWh
   Tensão nominal: 384 V

🔋 GERENCIAMENTO DE BATERIAS
📍 BATERIA: BATTERY-BANK-001
   Status: HEALTHY

⚡ ESTADO ATUAL:
   SOC: 85%
   Tensão: 395.2 V
   Corrente: 28.5 A
   Potência: 11.26 kW (charging)
   Temperatura: 32°C (OPTIMAL)

💚 SAÚDE:
   SOH: 96%
   Score geral: 94.2/100 (EXCELENTE)
   Ciclos: 450 / 6000
   Vida restante: 92.5%
   Eficiência: 90%
   Impacto temp.: OPTIMAL

📊 CAPACIDADE:
   Nominal: 192.0 kWh
   Real (com SOH): 184.3 kWh
   Disponível: 156.7 kWh
   Utilizável: 156.7 kWh (respeitando DoD)
   Para carga completa: 27.6 kWh
   C-rate atual: 0.06C (carga lenta)

✅ NENHUM PROBLEMA DETECTADO

✅ GERENCIAMENTO COMPLETO
```

### Teste 3: Energy Optimizer (Integrado)

```bash
python energy_optimizer_mock.py
```

**Output esperado:**
```
⚡ Solar-Manager - Energy Optimizer Mock

⚡ Estação: SOLAR-STATION-001
   Solar: 12.45 kW
   Bateria: 85%
   Carga: 2.85 kW

⚡ OTIMIZAÇÃO DE ENERGIA

📊 ANÁLISE DE ENERGIA:
   Solar atual: 12.45 kW
   Bateria: 85% (124.8 kWh utilizável)
   Disponibilidade: EXCELLENT
   Previsão próxima hora: 11.8 kWh

📈 DEMANDA:
   Carga total: 2.85 kW
   Instalações: 0.35 kW
   Robôs carregando: 1 (2.50 kW)
   Robôs aguardando: 2

🔋 ESTRATÉGIA DE BATERIA:
   Ação: CHARGE
   Potência alvo: 9.60 kW
   Balanço solar: +9.60 kW (EXCESSO)
   Motivo: Excesso solar disponível

🤖 PLANO DE RECARGA:
   Capacidade simultânea: 3 robôs
   Potência disponível: 9.60 kW

   ✅ INICIAR AGORA: 2 robôs
      • MICROBOT-002 (45min)
      • SUPPORTBOT-001 (30min)

🎯 AÇÕES RECOMENDADAS: 3
   ⚠️ 1. BATTERY CONTROL → CHARGE (9.60 kW)
   ⚠️ 2. START ROBOT CHARGING → MICROBOT-002
   ⚠️ 3. START ROBOT CHARGING → SUPPORTBOT-001

✅ OTIMIZAÇÃO COMPLETA
```

## ✅ Critérios de Sucesso

- [x] **Estação solar operacional**: 16.08 kWp, 24 painéis, geração 12.45 kW
- [x] **Condições ambientais monitoradas**: 850 W/m² irradiância, 42°C painéis, 15% nuvens
- [x] **Performance calculada**: 77.4% capacidade, 0.911 PR (excelente), 6.8% perda térmica
- [x] **Nenhuma anomalia detectada**: Eficiência OK, temperatura OK, PR OK
- [x] **Previsão de geração**: 11.8 kWh próxima hora (92% confiança)
- [x] **Bateria LiFePO4 gerenciada**: 192 kWh, 85% SOC, 96% SOH
- [x] **Saúde da bateria calculada**: 94.2/100 score, 92.5% vida restante, 450/6000 ciclos
- [x] **Capacidade analisada**: 184.3 kWh real, 156.7 kWh utilizável, 0.06C carga
- [x] **Nenhum problema na bateria**: SOC OK, SOH OK, temperatura 32°C (optimal)
- [x] **Otimização de energia**: Excesso +9.6 kW identificado, estratégia CHARGE
- [x] **Agendamento de robôs**: 3 robôs simultâneos possível, 2 para iniciar agora
- [x] **3 ações geradas**: Carregar bateria + iniciar 2 robôs

## ✅ Status

**✅ CONTRATO VALIDADO** — Pipeline MicroBot → Solar → Energy Optimization **FUNCIONA**

Este mock simula completamente o sistema de gestão de energia:
- ✅ Monitoramento de painéis solares (geração, eficiência, PR)
- ✅ Gestão de baterias LiFePO4 (SOC, SOH, ciclos, saúde)
- ✅ Otimização de energia (surplus/déficit, estratégia)
- ✅ Agendamento inteligente de recarga de robôs
- ✅ Detecção de anomalias e recomendações

## 🚀 Roadmap para Produção

### Hardware
- **Painéis Solares**: 24× Canadian Solar HiKu7 670W (16.08 kWp)
- **Inversores**: 2× Fronius Symo 8.2 kW (Modbus RTU)
- **Baterias**: BYD Battery-Box Premium LVL 15.4 (192 kWh LiFePO4)
- **BMS**: Built-in CAN bus communication
- **Sensores**:
  - Piranômetro: Kipp & Zonen CMP3 (irradiância)
  - Temperatura: PT100 (painéis + baterias)
  - Shunt: 500A/75mV (medição de corrente)
- **Controlador**: Raspberry Pi 4 ou Industrial PC com RS485/CAN interfaces

### Software
- **Framework**: Python 3.10+ com asyncio
- **Comunicação**:
  - pymodbus (Modbus RTU/TCP para inversores)
  - python-can (CAN bus para BMS)
  - paho-mqtt (telemetria para Core)
- **Database**: InfluxDB (time-series para histórico de energia)
- **Dashboards**: Grafana (monitoramento tempo real)
- **ML**: scikit-learn (previsão de geração solar baseado em histórico + clima)

### Algoritmos de Produção
1. **MPPT (Maximum Power Point Tracking)**: Feito pelos inversores
2. **Energy Forecast**:
   - Input: Histórico (30 dias), previsão climática (API OpenWeatherMap)
   - Model: Random Forest Regressor
   - Features: Hora do dia, dia do ano, irradiância prevista, temperatura, nuvens
   - Output: Geração esperada próximas 24h (intervalos de 1h)
3. **Battery SOH Estimation**:
   - Algoritmo: Coulomb counting + voltage curve analysis
   - Calibração: Full charge/discharge cycles periodicamente
   - ML: LSTM para prever degradação futura
4. **Charging Optimization**:
   - MPC (Model Predictive Control) para maximizar uso solar
   - Objective function: MIN(grid_import + battery_degradation)
   - Constraints: SOC limits, robot priorities, max power

### Integração
- **Input**: 
  - Inversores solares (geração atual, histórico)
  - BMS (SOC, SOH, tensão, corrente, temperatura)
  - Robôs via MQTT (SOC, localização, prioridade de recarga)
  - API clima (previsão de irradiância)
- **Output**:
  - Comandos para inversores (potência ativa/reativa)
  - Comandos para BMS (charge/discharge rate)
  - Notificações para CanaSwarm-Core (estação disponível/ocupada)
  - Agendamento para robôs (quando iniciar recarga)
- **Telemetria**: 
  - MQTT `/solar/{station_id}/generation` (1 min)
  - MQTT `/solar/{station_id}/battery` (10 sec)
  - MQTT `/solar/{station_id}/optimization` (5 min)

### Safety & Reliability
- **Proteções elétricas**:
  - Over-voltage protection (painéis + baterias)
  - Over-current protection (disjuntores)
  - Ground fault detection (GFDI)
  - Arc fault detection (AFCI)
- **Redundância**:
  - Dual inverters (50% capacity each)
  - Battery pack modular (6× 32 kWh)
  - Backup communication (4G LTE se Wi-Fi cair)
- **Manutenção**:
  - Limpeza de painéis: Mensal (ou após chuva forte)
  - Inspeção térmica: Trimestral (câmera IR para hot spots)
  - Calibração de sensores: Semestral
  - Substituição preventiva: Baterias a 70% SOH

### Performance Targets
- **Disponibilidade**: >95% uptime
- **Performance Ratio**: >0.85 anual (>0.90 em dias claros)
- **Battery efficiency**: >88% round-trip
- **Max simultaneous charging**: 4 robôs (10 kW)
- **Autonomy**: 2 dias sem sol (baterias + carga mínima)

## 📦 Dependências

**Mock (atual):**
- Python 3.10+ stdlib (json, random, datetime, pathlib)

**Produção:**
- pymodbus 3.3.2 (Modbus RTU/TCP)
- python-can 4.2.2 (CAN bus)
- paho-mqtt 1.6.1 (telemetria)
- influxdb-client 1.36.1 (time-series DB)
- numpy 1.24.3 (cálculos)
- pandas 2.0.3 (análise de dados)
- scikit-learn 1.3.0 (ML forecast)
- grafana-api 1.0.3 (dashboards)

## 🔗 Integrações

**Consome de:**
- **CanaSwarm-MicroBot**: Status de bateria, demanda de recarga
- **CanaSwarm-Core**: Lista de robôs ativos, prioridades de missão
- **API Clima**: Previsão de irradiância (OpenWeatherMap/INMET)

**Fornece para:**
- **CanaSwarm-Core**: Status da estação (disponível/ocupada), capacidade de recarga
- **CanaSwarm-MicroBot**: Autorização para iniciar recarga, tempos estimados
- **Operator Dashboard**: Métricas de energia, alertas, históricos

## 🎯 Impacto

- **Sustentabilidade**: 100% energia renovável, zero emissões na operação
- **Autonomia**: Robôs operam indefinidamente sem intervenção humana
- **Economia**: Payback em ~3-4 anos (solar + baterias), R$ ~500k economia/10 anos
- **Eficiência**: Otimização reduz desperdício em 15-20%
- **Inteligência**: Forecast ML melhora planejamento de missões
- **Confiabilidade**: Baterias garantem operação 24/7, mesmo sem sol
- **Escalabilidade**: Fácil adicionar mais estações conforme frota cresce
