#!/usr/bin/env python3
"""
Solar-Manager - Battery Manager Mock

Gerencia banco de baterias (SOC, SOH, ciclos, saúde)
"""

import json
import random
from pathlib import Path
from typing import Dict
from datetime import datetime


class BatteryManager:
    """Gerenciador de banco de baterias LiFePO4"""
    
    def __init__(self, battery_id: str):
        self.battery_id = battery_id
        self.management_count = 0
        self.history = []
    
    def manage_battery_bank(self, solar_data: Dict) -> Dict:
        """
        Gerencia banco de baterias
        
        Em produção, isso seria:
        - BMS (Battery Management System) via CAN bus
        - Medição de tensão/corrente (shunt resistors)
        - Sensores de temperatura (NTC/PT100)
        - Balanceamento de células (active/passive)
        - Proteções (over-voltage, under-voltage, over-current, over-temp)
        
        Args:
            solar_data: Dados do sistema solar
        
        Returns:
            Status completo das baterias
        """
        self.management_count += 1
        
        battery = solar_data.get('battery_storage', {})
        current_state = battery.get('current_state', {})
        specs = battery.get('specs', {})
        
        # Calcula health metrics
        health = self._calculate_battery_health(battery)
        
        # Calcula capacidade disponível
        capacity = self._calculate_available_capacity(battery, health)
        
        # Detecta problemas
        issues = self._detect_battery_issues(current_state, health, specs)
        
        # Recomendações de uso
        recommendations = self._generate_recommendations(current_state, health, capacity)
        
        result = {
            'timestamp': solar_data['timestamp'],
            'battery_id': self.battery_id,
            'management_count': self.management_count,
            'current_state': current_state,
            'health_metrics': health,
            'capacity_analysis': capacity,
            'issues': issues,
            'recommendations': recommendations,
            'status': 'healthy' if len(issues) == 0 else 'warning'
        }
        
        self.history.append(result)
        return result
    
    def _calculate_battery_health(self, battery: Dict) -> Dict:
        """Calcula métricas de saúde da bateria"""
        state = battery.get('current_state', {})
        usage = battery.get('usage_stats', {})
        specs = battery.get('specs', {})
        
        soc = state.get('state_of_charge_percent', 0)
        soh = state.get('state_of_health_percent', 100)
        temp = state.get('temperature_c', 25)
        
        # Cycles completados vs vida útil
        cycles = usage.get('cycles_completed', 0)
        cycle_life = specs.get('cycle_life', 6000)
        remaining_life_percent = ((cycle_life - cycles) / cycle_life * 100) if cycle_life > 0 else 0
        
        # Eficiência round-trip
        efficiency = usage.get('round_trip_efficiency_percent', 90)
        
        # Degradação por temperatura
        # Baterias LiFePO4: ideal 15-35°C, degradação acima de 45°C
        if temp > 45:
            temp_impact = 'high_degradation'
            temp_impact_score = 0.6
        elif temp > 35:
            temp_impact = 'moderate_degradation'
            temp_impact_score = 0.8
        elif temp < 0:
            temp_impact = 'reduced_capacity'
            temp_impact_score = 0.7
        else:
            temp_impact = 'optimal'
            temp_impact_score = 1.0
        
        # Score geral de saúde (0-100)
        health_score = (
            soh * 0.4 +  # 40% peso para SOH
            remaining_life_percent * 0.3 +  # 30% peso para vida útil restante
            efficiency * 0.2 +  # 20% peso para eficiência
            temp_impact_score * 100 * 0.1  # 10% peso para temperatura
        )
        
        return {
            'state_of_health_percent': soh,
            'remaining_life_percent': round(remaining_life_percent, 1),
            'cycles_completed': cycles,
            'estimated_remaining_cycles': cycle_life - cycles,
            'round_trip_efficiency_percent': efficiency,
            'temperature_impact': temp_impact,
            'overall_health_score': round(health_score, 1)
        }
    
    def _calculate_available_capacity(self, battery: Dict, health: Dict) -> Dict:
        """Calcula capacidade disponível da bateria"""
        specs = battery.get('specs', {})
        state = battery.get('current_state', {})
        
        nominal_capacity_kwh = specs.get('energy_capacity_kwh', 0)
        soc = state.get('state_of_charge_percent', 0)
        soh = health.get('state_of_health_percent', 100)
        
        # Capacidade real considerando SOH
        actual_capacity_kwh = nominal_capacity_kwh * (soh / 100)
        
        # Energia disponível atual
        available_energy_kwh = actual_capacity_kwh * (soc / 100)
        
        # Energia que pode ser descarregada (considerando DoD 80% para LiFePO4)
        usable_energy_kwh = available_energy_kwh if soc > 20 else 0
        
        # Energia que pode ser armazenada
        energy_to_full_kwh = actual_capacity_kwh - available_energy_kwh
        
        # C-rate atual
        current_power_kw = abs(state.get('power_kw', 0))
        nominal_voltage = specs.get('nominal_voltage_v', 1)
        capacity_ah = specs.get('capacity_ah', 1)
        c_rate = (current_power_kw * 1000) / (nominal_voltage * capacity_ah) if (nominal_voltage * capacity_ah) > 0 else 0
        
        return {
            'nominal_capacity_kwh': nominal_capacity_kwh,
            'actual_capacity_kwh': round(actual_capacity_kwh, 2),
            'available_energy_kwh': round(available_energy_kwh, 2),
            'usable_energy_kwh': round(usable_energy_kwh, 2),
            'energy_to_full_kwh': round(energy_to_full_kwh, 2),
            'depth_of_discharge_percent': 100 - soc,
            'current_c_rate': round(c_rate, 2)
        }
    
    def _detect_battery_issues(self, state: Dict, health: Dict, specs: Dict) -> list:
        """Detecta problemas na bateria"""
        issues = []
        
        soc = state.get('state_of_charge_percent', 0)
        soh = health.get('state_of_health_percent', 100)
        temp = state.get('temperature_c', 25)
        voltage = state.get('voltage_v', 0)
        
        # SOC crítico
        if soc < 20:
            issues.append({
                'type': 'low_soc',
                'severity': 'critical' if soc < 10 else 'warning',
                'value': soc,
                'threshold': 20,
                'message': f"Estado de carga baixo: {soc}%"
            })
        
        # SOH degradado
        if soh < 80:
            issues.append({
                'type': 'degraded_soh',
                'severity': 'warning',
                'value': soh,
                'threshold': 80,
                'message': f"Estado de saúde degradado: {soh}%"
            })
        
        # Temperatura fora da faixa
        if temp > 45:
            issues.append({
                'type': 'high_temperature',
                'severity': 'critical' if temp > 55 else 'warning',
                'value': temp,
                'threshold': 45,
                'message': f"Temperatura elevada: {temp}°C"
            })
        elif temp < 0:
            issues.append({
                'type': 'low_temperature',
                'severity': 'warning',
                'value': temp,
                'threshold': 0,
                'message': f"Temperatura baixa: {temp}°C"
            })
        
        # Tensão anormal
        nominal_voltage = specs.get('nominal_voltage_v', 384)
        voltage_deviation = abs(voltage - nominal_voltage) / nominal_voltage * 100
        if voltage_deviation > 15:
            issues.append({
                'type': 'voltage_abnormal',
                'severity': 'warning',
                'value': voltage,
                'expected': nominal_voltage,
                'deviation_percent': round(voltage_deviation, 1),
                'message': f"Tensão anormal: {voltage}V (esperado ~{nominal_voltage}V)"
            })
        
        # Fim de vida útil
        if health['remaining_life_percent'] < 10:
            issues.append({
                'type': 'end_of_life',
                'severity': 'critical' if health['remaining_life_percent'] < 5 else 'warning',
                'value': health['remaining_life_percent'],
                'threshold': 10,
                'message': f"Fim de vida útil: {health['remaining_life_percent']:.1f}% restante"
            })
        
        return issues
    
    def _generate_recommendations(self, state: Dict, health: Dict, capacity: Dict) -> list:
        """Gera recomendações de uso"""
        recommendations = []
        
        soc = state.get('state_of_charge_percent', 0)
        status = state.get('charge_discharge_status', 'idle')
        
        # Recomendações de carga
        if soc < 30 and status != 'charging':
            recommendations.append({
                'type': 'charge_soon',
                'priority': 'high' if soc < 20 else 'medium',
                'action': 'Iniciar recarga',
                'reason': f'SOC baixo ({soc}%)'
            })
        
        if soc > 95 and status == 'charging':
            recommendations.append({
                'type': 'stop_charging',
                'priority': 'medium',
                'action': 'Parar recarga',
                'reason': f'SOC alto ({soc}%), evitar sobrecarga'
            })
        
        # Recomendações de temperatura
        temp = state.get('temperature_c', 25)
        if temp > 40:
            recommendations.append({
                'type': 'cooling',
                'priority': 'high' if temp > 45 else 'medium',
                'action': 'Ativar resfriamento',
                'reason': f'Temperatura elevada ({temp}°C)'
            })
        
        # Recomendações de ciclos
        if health['remaining_life_percent'] < 20:
            recommendations.append({
                'type': 'replacement_planning',
                'priority': 'low',
                'action': 'Planejar substituição',
                'reason': f"Vida útil: {health['remaining_life_percent']:.1f}% restante"
            })
        
        return recommendations
    
    def display_battery_report(self, result: Dict):
        """Exibe relatório de baterias"""
        print("\n" + "="*70)
        print("🔋 GERENCIAMENTO DE BATERIAS")
        print("="*70)
        
        state = result['current_state']
        health = result['health_metrics']
        capacity = result['capacity_analysis']
        
        print(f"\n📍 BATERIA: {result['battery_id']}")
        print(f"   Status: {result['status'].upper()}")
        
        print(f"\n⚡ ESTADO ATUAL:")
        print(f"   SOC: {state['state_of_charge_percent']}%")
        print(f"   Tensão: {state['voltage_v']:.1f} V")
        print(f"   Corrente: {state['current_a']:.1f} A")
        print(f"   Potência: {state['power_kw']:.2f} kW ({state['charge_discharge_status']})")
        print(f"   Temperatura: {state['temperature_c']}°C")
        
        print(f"\n💚 SAÚDE:")
        print(f"   SOH: {health['state_of_health_percent']}%")
        print(f"   Score geral: {health['overall_health_score']:.1f}/100")
        print(f"   Ciclos: {health['cycles_completed']} / {health['cycles_completed'] + health['estimated_remaining_cycles']}")
        print(f"   Vida restante: {health['remaining_life_percent']:.1f}%")
        print(f"   Eficiência: {health['round_trip_efficiency_percent']}%")
        print(f"   Impacto temp.: {health['temperature_impact'].replace('_', ' ').upper()}")
        
        print(f"\n📊 CAPACIDADE:")
        print(f"   Nominal: {capacity['nominal_capacity_kwh']:.1f} kWh")
        print(f"   Real (com SOH): {capacity['actual_capacity_kwh']:.1f} kWh")
        print(f"   Disponível: {capacity['available_energy_kwh']:.1f} kWh")
        print(f"   Utilizável: {capacity['usable_energy_kwh']:.1f} kWh")
        print(f"   Para carga completa: {capacity['energy_to_full_kwh']:.1f} kWh")
        print(f"   C-rate atual: {capacity['current_c_rate']:.2f}C")
        
        if result['issues']:
            print(f"\n⚠️  PROBLEMAS DETECTADOS: {len(result['issues'])}")
            for issue in result['issues']:
                severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡"
                print(f"   {severity_icon} {issue['message']}")
        else:
            print(f"\n✅ NENHUM PROBLEMA DETECTADO")
        
        if result['recommendations']:
            print(f"\n💡 RECOMENDAÇÕES: {len(result['recommendations'])}")
            for rec in result['recommendations']:
                priority_icon = "❗" if rec['priority'] == 'high' else "⚠️" if rec['priority'] == 'medium' else "ℹ️"
                print(f"   {priority_icon} {rec['action']}: {rec['reason']}")


if __name__ == "__main__":
    print("🔋 Solar-Manager - Battery Manager Mock\n")
    print("="*70)
    
    # Inicializa gerenciador
    manager = BatteryManager("BATTERY-BANK-001")
    
    # Carrega dados de exemplo
    data_file = Path(__file__).parent / "example_solar_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        solar_data = json.load(f)
    
    battery_info = solar_data['battery_storage']
    print(f"\n🔋 Banco de Baterias: {battery_info['battery_id']}")
    print(f"   Tecnologia: {battery_info['technology']}")
    print(f"   Capacidade: {battery_info['specs']['energy_capacity_kwh']} kWh")
    print(f"   Tensão nominal: {battery_info['specs']['nominal_voltage_v']} V")
    
    # Gerencia bateria
    result = manager.manage_battery_bank(solar_data)
    
    # Exibe relatório
    manager.display_battery_report(result)
    
    print("\n" + "="*70)
    print("✅ GERENCIAMENTO COMPLETO")
    print("="*70)
    print(f"\n💡 Total de verificações: {manager.management_count}\n")
