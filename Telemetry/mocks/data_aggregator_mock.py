#!/usr/bin/env python3
"""
Telemetry - Data Aggregator Mock

Agregador de dados de telemetria (analytics, trends, KPIs)
"""

import json
from pathlib import Path
from typing import Dict, List


class DataAggregator:
    """Agregador de dados de telemetria"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.aggregation_count = 0
        self.history = []
    
    def aggregate_data(self, telemetry_data: Dict) -> Dict:
        """
        Agrega dados de telemetria da frota
        
        Agrega emmétricas como:
        - Média, min, max, desvio padrão
        - Distribuição por tipo de robô
        - Tendências (trends)
        - KPIs operacionais
        
        Args:
            telemetry_data: Dados de telemetria
        
        Returns:
            Dados agregados
        """
        self.aggregation_count += 1
        
        robots = telemetry_data.get('robots_telemetry', [])
        
        # Agregações de frota
        fleet_aggregation = self._aggregate_fleet_metrics(robots)
        
        # Agregações de bateria
        battery_aggregation = self._aggregate_battery_metrics(robots)
        
        # Agregações de missão
        mission_aggregation = self._aggregate_mission_metrics(robots)
        
        # Agregações de performance
        performance_aggregation = self._aggregate_performance_metrics(robots)
        
        # KPIs operacionais
        operational_kpis = self._calculate_operational_kpis(fleet_aggregation, 
                                                             battery_aggregation, 
                                                             mission_aggregation)
        
        result = {
            'session_id': self.session_id,
            'timestamp': telemetry_data['timestamp'],
            'aggregation_count': self.aggregation_count,
            'fleet': fleet_aggregation,
            'battery': battery_aggregation,
            'mission': mission_aggregation,
            'performance': performance_aggregation,
            'kpis': operational_kpis
        }
        
        self.history.append(result)
        return result
    
    def _aggregate_fleet_metrics(self, robots: List[Dict]) -> Dict:
        """Agrega métricas de frota"""
        total_robots = len(robots)
        
        # Por tipo
        by_type = {}
        for robot in robots:
            rtype = robot['type']
            by_type[rtype] = by_type.get(rtype, 0) + 1
        
        # Por status de saúde
        by_health = {'healthy': 0, 'warning': 0, 'critical': 0, 'unknown': 0}
        for robot in robots:
            health = robot.get('health', {}).get('overall_status', 'unknown')
            by_health[health] = by_health.get(health, 0) + 1
        
        # Por status de missão
        by_mission_status = {}
        for robot in robots:
            mission_status = robot.get('mission', {}).get('status', 'unknown')
            by_mission_status[mission_status] = by_mission_status.get(mission_status, 0) + 1
        
        # Posições (centróide da frota)
        lats = [r['position']['lat'] for r in robots if r.get('position')]
        lons = [r['position']['lon'] for r in robots if r.get('position')]
        
        centroid = {
            'lat': sum(lats) / len(lats) if lats else 0,
            'lon': sum(lons) / len(lons) if lons else 0
        }
        
        # Velocidade média
        speeds = [r['position'].get('speed_ms', 0) for r in robots if r.get('position')]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        return {
            'total_robots': total_robots,
            'by_type': by_type,
            'by_health': by_health,
            'by_mission_status': by_mission_status,
            'centroid': centroid,
            'average_speed_ms': round(avg_speed, 2)
        }
    
    def _aggregate_battery_metrics(self, robots: List[Dict]) -> Dict:
        """Agrega métricas de bateria"""
        batteries = [r.get('battery', {}) for r in robots if r.get('battery')]
        
        if not batteries:
            return {}
        
        # SOC
        socs = [b['soc_percent'] for b in batteries]
        avg_soc = sum(socs) / len(socs)
        min_soc = min(socs)
        max_soc = max(socs)
        
        # Temperatura
        temps = [b['temperature_c'] for b in batteries]
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        
        # Potência
        powers = [abs(b['voltage_v'] * b['current_a']) for b in batteries]
        total_power = sum(powers)
        
        # Carregando
        charging_count = sum(1 for b in batteries if b.get('charging', False))
        
        # Ciclos
        cycles = [b.get('cycles_count', 0) for b in batteries]
        avg_cycles = sum(cycles) / len(cycles) if cycles else 0
        
        # Range estimado
        ranges = [b.get('estimated_range_km', 0) for b in batteries]
        avg_range = sum(ranges) / len(ranges) if ranges else 0
        
        # Distribuição de SOC
        soc_distribution = {
            'critical_0_20': sum(1 for s in socs if s < 20),
            'low_20_50': sum(1 for s in socs if 20 <= s < 50),
            'medium_50_80': sum(1 for s in socs if 50 <= s < 80),
            'high_80_100': sum(1 for s in socs if s >= 80)
        }
        
        return {
            'average_soc_percent': round(avg_soc, 1),
            'min_soc_percent': min_soc,
            'max_soc_percent': max_soc,
            'soc_distribution': soc_distribution,
            'average_temperature_c': round(avg_temp, 1),
            'max_temperature_c': max_temp,
            'total_power_consumption_kw': round(total_power / 1000, 2),
            'charging_count': charging_count,
            'average_cycles': round(avg_cycles, 0),
            'average_range_km': round(avg_range, 1)
        }
    
    def _aggregate_mission_metrics(self, robots: List[Dict]) -> Dict:
        """Agrega métricas de missão"""
        missions = [r.get('mission', {}) for r in robots if r.get('mission')]
        
        # Missões ativas
        active_missions = [m for m in missions if m.get('mission_id')]
        
        if not active_missions:
            return {
                'active_missions': 0,
                'idle_robots': len(robots),
                'total_area_covered_ha': 0,
                'total_area_remaining_ha': 0
            }
        
        # Progresso
        progresses = [m.get('progress_percent', 0) for m in active_missions]
        avg_progress = sum(progresses) / len(progresses) if progresses else 0
        
        # Área
        areas_covered = [m.get('area_covered_ha', 0) for m in missions]
        areas_remaining = [m.get('area_remaining_ha', 0) for m in missions]
        total_area_covered = sum(areas_covered)
        total_area_remaining = sum(areas_remaining)
        
        # Por status
        mission_statuses = [m.get('status', 'idle') for m in missions]
        by_status = {}
        for status in mission_statuses:
            by_status[status] = by_status.get(status, 0) + 1
        
        # Eficiência (área coberta por hora de uptime)
        total_uptime = sum(r.get('health', {}).get('uptime_hours', 0) for r in robots)
        efficiency_ha_per_hour = (total_area_covered / total_uptime) if total_uptime > 0 else 0
        
        return {
            'active_missions': len(active_missions),
            'idle_robots': by_status.get('idle', 0),
            'average_progress_percent': round(avg_progress, 1),
            'total_area_covered_ha': round(total_area_covered, 2),
            'total_area_remaining_ha': round(total_area_remaining, 2),
            'by_status': by_status,
            'efficiency_ha_per_hour': round(efficiency_ha_per_hour, 2)
        }
    
    def _aggregate_performance_metrics(self, robots: List[Dict]) -> Dict:
        """Agrega métricas de performance"""
        healths = [r.get('health', {}) for r in robots if r.get('health')]
        
        if not healths:
            return {}
        
        # CPU
        cpus = [h.get('cpu_usage_percent', 0) for h in healths]
        avg_cpu = sum(cpus) / len(cpus)
        max_cpu = max(cpus) if cpus else 0
        
        # Memória
        mems = [h.get('memory_usage_percent', 0) for h in healths]
        avg_mem = sum(mems) / len(mems)
        max_mem = max(mems) if mems else 0
        
        # Uptime
        uptimes = [h.get('uptime_hours', 0) for h in healths]
        avg_uptime = sum(uptimes) / len(uptimes)
        total_uptime = sum(uptimes)
        
        # Latência de rede
        latencies = [h.get('network_latency_ms', 0) for h in healths]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return {
            'average_cpu_percent': round(avg_cpu, 1),
            'max_cpu_percent': max_cpu,
            'average_memory_percent': round(avg_mem, 1),
            'max_memory_percent': max_mem,
            'average_uptime_hours': round(avg_uptime, 1),
            'total_uptime_hours': round(total_uptime, 1),
            'average_network_latency_ms': round(avg_latency, 0)
        }
    
    def _calculate_operational_kpis(self, fleet: Dict, battery: Dict, 
                                    mission: Dict) -> Dict:
        """Calcula KPIs operacionais"""
        # Disponibilidade (% de robôs saudáveis e não carregando)
        healthy_count = fleet['by_health'].get('healthy', 0)
        charging_count = battery.get('charging_count', 0)
        total_robots = fleet['total_robots']
        
        available_robots = healthy_count - charging_count
        availability = (available_robots / total_robots * 100) if total_robots > 0 else 0
        
        # Utilização (% de robôs em missão ativa)
        active_missions = mission.get('active_missions', 0)
        utilization = (active_missions / total_robots * 100) if total_robots > 0 else 0
        
        # Eficiência energética (área/kWh) - estimado
        total_power_kw = battery.get('total_power_consumption_kw', 0)
        area_covered = mission.get('total_area_covered_ha', 0)
        energy_efficiency = (area_covered / total_power_kw) if total_power_kw > 0 else 0
        
        # Saúde da frota (score 0-100)
        health_score = (
            (healthy_count / total_robots) * 40 +  # 40% peso
            (battery.get('average_soc_percent', 0) / 100) * 30 +  # 30% peso
            (mission.get('average_progress_percent', 0) / 100) * 20 +  # 20% peso
            (1 - battery.get('max_temperature_c', 25) / 100) * 10  # 10% peso
        )
        
        # Classificação de performance
        if health_score >= 80:
            performance_level = 'excellent'
        elif health_score >= 60:
            performance_level = 'good'
        elif health_score >= 40:
            performance_level = 'fair'
        else:
            performance_level = 'poor'
        
        return {
            'availability_percent': round(availability, 1),
            'utilization_percent': round(utilization, 1),
            'energy_efficiency_ha_per_kwh': round(energy_efficiency, 2),
            'fleet_health_score': round(health_score, 1),
            'performance_level': performance_level,
            'operational_readiness': 'ready' if availability >= 70 and health_score >= 60 else 'limited'
        }
    
    def display_aggregation_report(self, result: Dict):
        """Exibe relatório de agregação"""
        print("\n" + "="*70)
        print("📊 AGREGAÇÃO DE DADOS")
        print("="*70)
        
        fleet = result['fleet']
        battery = result['battery']
        mission = result['mission']
        perf = result['performance']
        kpis = result['kpis']
        
        print(f"\n🤖 FROTA:")
        print(f"   Total: {fleet['total_robots']} robôs")
        print(f"   Por tipo: {fleet['by_type']}")
        print(f"   Por saúde: Healthy {fleet['by_health']['healthy']}, Warning {fleet['by_health']['warning']}, Critical {fleet['by_health']['critical']}")
        print(f"   Velocidade média: {fleet['average_speed_ms']:.2f} m/s")
        print(f"   Centróide: ({fleet['centroid']['lat']:.4f}, {fleet['centroid']['lon']:.4f})")
        
        print(f"\n🔋 BATERIAS:")
        print(f"   SOC médio: {battery['average_soc_percent']:.1f}% (min {battery['min_soc_percent']}%, max {battery['max_soc_percent']}%)")
        print(f"   Distribuição: {battery['soc_distribution']['high_80_100']} alto, {battery['soc_distribution']['medium_50_80']} médio, {battery['soc_distribution']['low_20_50']} baixo, {battery['soc_distribution']['critical_0_20']} crítico")
        print(f"   Temperatura média: {battery['average_temperature_c']:.1f}°C (max {battery['max_temperature_c']:.1f}°C)")
        print(f"   Consumo total: {battery['total_power_consumption_kw']:.2f} kW")
        print(f"   Carregando: {battery['charging_count']} robô(s)")
        print(f"   Range médio: {battery['average_range_km']:.1f} km")
        
        print(f"\n📍 MISSÕES:")
        print(f"   Ativas: {mission['active_missions']}")
        print(f"   Idle: {mission['idle_robots']}")
        print(f"   Progresso médio: {mission['average_progress_percent']:.1f}%")
        print(f"   Área coberta: {mission['total_area_covered_ha']:.2f} ha")
        print(f"   Área restante: {mission['total_area_remaining_ha']:.2f} ha")
        print(f"   Eficiência: {mission['efficiency_ha_per_hour']:.2f} ha/h")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"   CPU médio: {perf['average_cpu_percent']:.1f}% (max {perf['max_cpu_percent']}%)")
        print(f"   RAM médio: {perf['average_memory_percent']:.1f}% (max {perf['max_memory_percent']}%)")
        print(f"   Uptime médio: {perf['average_uptime_hours']:.1f}h (total {perf['total_uptime_hours']:.1f}h)")
        print(f"   Latência média: {perf['average_network_latency_ms']:.0f} ms")
        
        print(f"\n📈 KPIs OPERACIONAIS:")
        print(f"   Disponibilidade: {kpis['availability_percent']:.1f}%")
        print(f"   Utilização: {kpis['utilization_percent']:.1f}%")
        print(f"   Eficiência energética: {kpis['energy_efficiency_ha_per_kwh']:.2f} ha/kWh")
        print(f"   Score de saúde: {kpis['fleet_health_score']:.1f}/100 ({kpis['performance_level'].upper()})")
        print(f"   Prontidão operacional: {kpis['operational_readiness'].upper()}")


if __name__ == "__main__":
    print("📊 Telemetry - Data Aggregator Mock\n")
    print("="*70)
    
    # Inicializa agregador
    aggregator = DataAggregator("TELEM-SESSION-20260220-154500")
    
    # Carrega dados
    data_file = Path(__file__).parent / "example_telemetry_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        telemetry_data = json.load(f)
    
    print(f"\n📊 Session: {telemetry_data['telemetry_session_id']}")
    print(f"   Robôs: {telemetry_data['fleet_snapshot']['total_robots']}")
    
    # Agrega dados
    result = aggregator.aggregate_data(telemetry_data)
    
    # Exibe relatório
    aggregator.display_aggregation_report(result)
    
    print("\n" + "="*70)
    print("✅ AGREGAÇÃO COMPLETA")
    print("="*70)
    print(f"\n💡 Total de agregações: {aggregator.aggregation_count}\n")
