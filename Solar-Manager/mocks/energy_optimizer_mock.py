#!/usr/bin/env python3
"""
Solar-Manager - Energy Optimizer Mock

Otimiza uso de energia solar e coordena recarga de robôs
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta


class EnergyOptimizer:
    """Otimizador de energia solar e gestão de carga"""
    
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.optimization_count = 0
        self.decisions_history = []
    
    def optimize_energy_usage(self, solar_data: Dict) -> Dict:
        """
        Otimiza uso de energia e coordena recarga
        
        Estratégia:
        1. Priorizar uso direto de solar (sem passar por bateria)
        2. Carregar baterias quando há excesso solar
        3. Usar baterias quando solar insuficiente
        4. Agendar cargas pesadas para horários de pico solar
        5. Evitar descarga profunda de baterias (< 20%)
        
        Args:
            solar_data: Dados completos do sistema
        
        Returns:
            Decisões de otimização
        """
        self.optimization_count += 1
        
        # Análise de energia disponível
        energy_analysis = self._analyze_energy_availability(solar_data)
        
        # Análise de demanda
        load_analysis = self._analyze_load_demand(solar_data)
        
        # Estratégia de bateria
        battery_strategy = self._determine_battery_strategy(energy_analysis, load_analysis)
        
        # Agendamento de recarga de robôs
        charging_plan = self._optimize_robot_charging(solar_data, energy_analysis)
        
        # Ações recomendadas
        actions = self._generate_actions(energy_analysis, load_analysis, battery_strategy, charging_plan)
        
        result = {
            'timestamp': solar_data['timestamp'],
            'station_id': self.station_id,
            'optimization_count': self.optimization_count,
            'energy_analysis': energy_analysis,
            'load_analysis': load_analysis,
            'battery_strategy': battery_strategy,
            'charging_plan': charging_plan,
            'actions': actions
        }
        
        self.decisions_history.append(result)
        return result
    
    def _analyze_energy_availability(self, solar_data: Dict) -> Dict:
        """Analisa energia disponível (solar + bateria)"""
        solar = solar_data.get('solar_panels', {}).get('current_generation', {})
        battery = solar_data.get('battery_storage', {}).get('current_state', {})
        forecast = solar_data.get('energy_forecast', {})
        
        solar_power_kw = solar.get('power_kw', 0)
        battery_soc = battery.get('state_of_charge_percent', 0)
        battery_power_kw = battery.get('power_kw', 0)
        battery_capacity_kwh = solar_data.get('battery_storage', {}).get('specs', {}).get('energy_capacity_kwh', 0)
        
        # Energia disponível na bateria
        battery_energy_kwh = battery_capacity_kwh * (battery_soc / 100)
        battery_usable_kwh = max(0, battery_energy_kwh - (battery_capacity_kwh * 0.2))  # Reserva 20%
        
        # Previsão próxima hora
        next_hour_solar_kwh = forecast.get('next_hour', {}).get('expected_generation_kwh', 0)
        
        # Energia total disponível
        total_available_kw = solar_power_kw + (battery_power_kw if battery_power_kw > 0 else 0)
        
        # Status de disponibilidade
        if solar_power_kw > 10 and battery_soc > 50:
            availability = 'excellent'
        elif solar_power_kw > 5 or battery_soc > 30:
            availability = 'good'
        elif battery_soc > 20:
            availability = 'limited'
        else:
            availability = 'critical'
        
        return {
            'solar_power_kw': solar_power_kw,
            'battery_energy_kwh': round(battery_energy_kwh, 2),
            'battery_usable_kwh': round(battery_usable_kwh, 2),
            'battery_soc_percent': battery_soc,
            'total_available_power_kw': round(total_available_kw, 2),
            'next_hour_expected_kwh': next_hour_solar_kwh,
            'availability_status': availability
        }
    
    def _analyze_load_demand(self, solar_data: Dict) -> Dict:
        """Analisa demanda de carga atual e prevista"""
        load = solar_data.get('load_management', {})
        
        total_load_kw = load.get('total_load_kw', 0)
        robot_charging = load.get('robot_charging', {})
        facility_load_kw = load.get('facility_load_kw', 0)
        
        active_robots = robot_charging.get('active_robots', 0)
        robots = robot_charging.get('robots', [])
        
        # Calcula demanda dos robôs ativos
        robot_load_kw = sum(r.get('charge_power_kw', 0) for r in robots)
        
        # Robôs agendados
        schedule = solar_data.get('charging_schedule', {}).get('scheduled_charges', [])
        pending_robots = len(schedule)
        
        # Estimativa de demanda futura (próxima hora)
        # Assume que robôs agendados começarão a carregar
        future_robot_load_kw = sum(2.0 for _ in schedule[:2])  # ~2kW por robô
        estimated_next_hour_load_kw = facility_load_kw + robot_load_kw + future_robot_load_kw
        
        return {
            'current_total_load_kw': total_load_kw,
            'facility_load_kw': facility_load_kw,
            'robot_charging_load_kw': round(robot_load_kw, 2),
            'active_charging_robots': active_robots,
            'pending_charging_robots': pending_robots,
            'estimated_next_hour_load_kw': round(estimated_next_hour_load_kw, 2)
        }
    
    def _determine_battery_strategy(self, energy: Dict, load: Dict) -> Dict:
        """Determina estratégia de uso da bateria"""
        solar_kw = energy['solar_power_kw']
        battery_soc = energy['battery_soc_percent']
        load_kw = load['current_total_load_kw']
        
        surplus_kw = solar_kw - load_kw
        
        # Estratégia
        if surplus_kw > 2 and battery_soc < 95:
            # Excesso solar, carregar bateria
            strategy = 'charge'
            target_power_kw = min(surplus_kw, 15)  # Limite de carga
            reason = 'Excesso solar disponível'
        elif surplus_kw < -2 and battery_soc > 25:
            # Déficit, usar bateria
            strategy = 'discharge'
            target_power_kw = min(abs(surplus_kw), 20)  # Limite de descarga
            reason = 'Solar insuficiente para demanda'
        elif battery_soc < 20:
            # Bateria crítica, priorizar recarga
            strategy = 'priority_charge'
            target_power_kw = 10
            reason = 'SOC crítico, priorizar recarga'
        else:
            # Manter estado
            strategy = 'maintain'
            target_power_kw = 0
            reason = 'Balanço energético adequado'
        
        return {
            'strategy': strategy,
            'target_power_kw': round(target_power_kw, 2),
            'reason': reason,
            'solar_surplus_deficit_kw': round(surplus_kw, 2)
        }
    
    def _optimize_robot_charging(self, solar_data: Dict, energy: Dict) -> Dict:
        """Otimiza agendamento de recarga de robôs"""
        load = solar_data.get('load_management', {})
        schedule = solar_data.get('charging_schedule', {}).get('scheduled_charges', [])
        
        available_power_kw = load.get('available_power_kw', 0)
        solar_power_kw = energy.get('solar_power_kw', 0)
        forecast_kwh = energy.get('next_hour_expected_kwh', 0)
        
        # Determina quantos robôs podem carregar simultaneamente
        # Assume ~2.5kW por robô em fast charge
        max_simultaneous = int(available_power_kw / 2.5)
        
        # Classifica robôs por prioridade
        sorted_schedule = sorted(
            schedule,
            key=lambda r: (
                0 if r.get('priority') == 'high' else 1 if r.get('priority') == 'medium' else 2,
                r.get('current_soc_percent', 100)  # Menor SOC = maior prioridade
            )
        )
        
        # Decide quais robôs iniciar agora
        robots_to_start = []
        robots_to_delay = []
        
        for robot in sorted_schedule[:max_simultaneous]:
            if solar_power_kw > 5:  # Tem solar disponível
                robots_to_start.append({
                    'robot_id': robot['robot_id'],
                    'reason': 'Solar disponível',
                    'estimated_duration_min': robot.get('estimated_duration_minutes', 45)
                })
            else:
                robots_to_delay.append({
                    'robot_id': robot['robot_id'],
                    'reason': 'Aguardar mais geração solar',
                    'suggested_delay_min': 30
                })
        
        # Robôs que não cabem no limite
        for robot in sorted_schedule[max_simultaneous:]:
            robots_to_delay.append({
                'robot_id': robot['robot_id'],
                'reason': 'Capacidade limitada',
                'suggested_delay_min': 60
            })
        
        return {
            'max_simultaneous_charging': max_simultaneous,
            'available_power_kw': available_power_kw,
            'robots_to_start_now': robots_to_start,
            'robots_to_delay': robots_to_delay,
            'optimal_charging_window': forecast_kwh > 10
        }
    
    def _generate_actions(self, energy: Dict, load: Dict, battery: Dict, charging: Dict) -> List[Dict]:
        """Gera ações de otimização"""
        actions = []
        
        # Ação de bateria
        if battery['strategy'] != 'maintain':
            actions.append({
                'type': 'battery_control',
                'command': battery['strategy'],
                'target_power_kw': battery['target_power_kw'],
                'priority': 'high' if battery['strategy'] == 'priority_charge' else 'medium',
                'reason': battery['reason']
            })
        
        # Ações de recarga de robôs
        for robot in charging['robots_to_start_now']:
            actions.append({
                'type': 'start_robot_charging',
                'robot_id': robot['robot_id'],
                'priority': 'medium',
                'reason': robot['reason']
            })
        
        for robot in charging['robots_to_delay']:
            actions.append({
                'type': 'delay_robot_charging',
                'robot_id': robot['robot_id'],
                'delay_minutes': robot['suggested_delay_min'],
                'priority': 'low',
                'reason': robot['reason']
            })
        
        # Alertas de disponibilidade
        if energy['availability_status'] == 'critical':
            actions.append({
                'type': 'energy_alert',
                'severity': 'critical',
                'message': 'Energia disponível crítica',
                'priority': 'high',
                'recommendation': 'Reduzir cargas não essenciais'
            })
        
        return actions
    
    def display_optimization_report(self, result: Dict):
        """Exibe relatório de otimização"""
        print("\n" + "="*70)
        print("⚡ OTIMIZAÇÃO DE ENERGIA")
        print("="*70)
        
        energy = result['energy_analysis']
        load = result['load_analysis']
        battery = result['battery_strategy']
        charging = result['charging_plan']
        
        print(f"\n📊 ANÁLISE DE ENERGIA:")
        print(f"   Solar atual: {energy['solar_power_kw']:.2f} kW")
        print(f"   Bateria: {energy['battery_soc_percent']}% ({energy['battery_usable_kwh']:.1f} kWh utilizável)")
        print(f"   Disponibilidade: {energy['availability_status'].upper()}")
        print(f"   Previsão próxima hora: {energy['next_hour_expected_kwh']:.1f} kWh")
        
        print(f"\n📈 DEMANDA:")
        print(f"   Carga total: {load['current_total_load_kw']:.2f} kW")
        print(f"   Instalações: {load['facility_load_kw']:.2f} kW")
        print(f"   Robôs carregando: {load['active_charging_robots']} ({load['robot_charging_load_kw']:.2f} kW)")
        print(f"   Robôs aguardando: {load['pending_charging_robots']}")
        
        print(f"\n🔋 ESTRATÉGIA DE BATERIA:")
        print(f"   Ação: {battery['strategy'].upper().replace('_', ' ')}")
        print(f"   Potência alvo: {battery['target_power_kw']:.2f} kW")
        print(f"   Balanço solar: {battery['solar_surplus_deficit_kw']:+.2f} kW")
        print(f"   Motivo: {battery['reason']}")
        
        print(f"\n🤖 PLANO DE RECARGA:")
        print(f"   Capacidade simultânea: {charging['max_simultaneous_charging']} robôs")
        print(f"   Potência disponível: {charging['available_power_kw']:.2f} kW")
        
        if charging['robots_to_start_now']:
            print(f"\n   ✅ INICIAR AGORA: {len(charging['robots_to_start_now'])}")
            for r in charging['robots_to_start_now']:
                print(f"      • {r['robot_id']} ({r['estimated_duration_min']}min)")
        
        if charging['robots_to_delay']:
            print(f"\n   ⏳ ADIAR: {len(charging['robots_to_delay'])}")
            for r in charging['robots_to_delay']:
                print(f"      • {r['robot_id']} (+{r['suggested_delay_min']}min): {r['reason']}")
        
        print(f"\n🎯 AÇÕES RECOMENDADAS: {len(result['actions'])}")
        for i, action in enumerate(result['actions'], 1):
            priority_icon = "❗" if action['priority'] == 'high' else "⚠️" if action['priority'] == 'medium' else "ℹ️"
            print(f"\n   {priority_icon} {i}. {action['type'].upper().replace('_', ' ')}")
            if 'robot_id' in action:
                print(f"      Robô: {action['robot_id']}")
            if 'reason' in action:
                print(f"      Motivo: {action['reason']}")


if __name__ == "__main__":
    print("⚡ Solar-Manager - Energy Optimizer Mock\n")
    print("="*70)
    
    # Inicializa otimizador
    optimizer = EnergyOptimizer("SOLAR-STATION-001")
    
    # Carrega dados de exemplo
    data_file = Path(__file__).parent / "example_solar_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        solar_data = json.load(f)
    
    print(f"\n⚡ Estação: {solar_data['station_id']}")
    print(f"   Solar: {solar_data['solar_panels']['current_generation']['power_kw']:.2f} kW")
    print(f"   Bateria: {solar_data['battery_storage']['current_state']['state_of_charge_percent']}%")
    print(f"   Carga: {solar_data['load_management']['total_load_kw']:.2f} kW")
    
    # Otimiza energia
    result = optimizer.optimize_energy_usage(solar_data)
    
    # Exibe relatório
    optimizer.display_optimization_report(result)
    
    print("\n" + "="*70)
    print("✅ OTIMIZAÇÃO COMPLETA")
    print("="*70)
    print(f"\n💡 Total de otimizações: {optimizer.optimization_count}\n")
