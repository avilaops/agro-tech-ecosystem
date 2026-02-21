#!/usr/bin/env python3
"""
Telemetry - Metrics Collector Mock

Coletor de métricas de telemetria dos robôs
"""

import json
from pathlib import Path
from typing import Dict, List


class MetricsCollector:
    """Coletor de métricas de telemetria"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.collection_count = 0
        self.history = []
    
    def collect_metrics(self, telemetry_data: Dict) -> Dict:
        """
        Coleta métricas de todos os robôs
        
        Em produção, isso seria:
        - MQTT broker (Mosquitto/HiveMQ) com QoS 1
        - Tópicos: fleet/{robot_id}/telemetry/#
        - Protocolo: MQTT 3.1.1 ou 5.0
        - Compressão: Protobuf ou MessagePack
        - Frequência: 1-10 Hz dependendo do sensor
        - Time-series DB: InfluxDB, TimescaleDB
        
        Args:
            telemetry_data: Dados brutos de telemetria
        
        Returns:
            Métricas coletadas e processadas
        """
        self.collection_count += 1
        
        robots = telemetry_data.get('robots_telemetry', [])
        
        # Coleta métricas por robô
        robot_metrics = []
        for robot in robots:
            metrics = self._collect_robot_metrics(robot)
            robot_metrics.append(metrics)
        
        # Estatísticas de coleta
        collection_stats = self._calculate_collection_stats(robot_metrics)
        
        # Qualidade dos dados
        data_quality = self._assess_data_quality(robots, collection_stats)
        
        result = {
            'session_id': self.session_id,
            'timestamp': telemetry_data['timestamp'],
            'collection_count': self.collection_count,
            'robots_count': len(robots),
            'robot_metrics': robot_metrics,
            'collection_stats': collection_stats,
            'data_quality': data_quality
        }
        
        self.history.append(result)
        return result
    
    def _collect_robot_metrics(self, robot: Dict) -> Dict:
        """Coleta métricas de um robô"""
        robot_id = robot['robot_id']
        robot_type = robot['type']
        
        # Posição e movimento
        position = robot.get('position', {})
        location_metrics = {
            'lat': position.get('lat'),
            'lon': position.get('lon'),
            'altitude_m': position.get('altitude_m'),
            'heading_deg': position.get('heading_deg'),
            'speed_ms': position.get('speed_ms', 0)
        }
        
        # Bateria
        battery = robot.get('battery', {})
        battery_metrics = {
            'soc_percent': battery.get('soc_percent'),
            'voltage_v': battery.get('voltage_v'),
            'current_a': battery.get('current_a'),
            'temperature_c': battery.get('temperature_c'),
            'charging': battery.get('charging', False),
            'estimated_range_km': battery.get('estimated_range_km'),
            'power_w': abs(battery.get('voltage_v', 0) * battery.get('current_a', 0)),
            'health_score': self._calculate_battery_health_score(battery)
        }
        
        # Sensores
        sensors = robot.get('sensors', {})
        sensor_status = {}
        active_sensors = 0
        for sensor_name, sensor_data in sensors.items():
            if isinstance(sensor_data, dict):
                status = sensor_data.get('status', 'unknown')
                sensor_status[sensor_name] = status
                if status == 'active':
                    active_sensors += 1
        
        sensor_metrics = {
            'total_sensors': len(sensors),
            'active_sensors': active_sensors,
            'sensor_health_percent': round((active_sensors / len(sensors) * 100) if sensors else 0, 1),
            'sensor_status': sensor_status
        }
        
        # Atuadores
        actuators = robot.get('actuators', {})
        actuator_power = sum(
            act.get('power_w', 0) for act in actuators.values() if isinstance(act, dict)
        )
        
        # Missão
        mission = robot.get('mission', {})
        mission_metrics = {
            'status': mission.get('status', 'idle'),
            'progress_percent': mission.get('progress_percent', 0),
            'area_covered_ha': mission.get('area_covered_ha', 0),
            'area_remaining_ha': mission.get('area_remaining_ha', 0)
        }
        
        # Saúde do sistema
        health = robot.get('health', {})
        system_health = {
            'overall_status': health.get('overall_status', 'unknown'),
            'cpu_usage_percent': health.get('cpu_usage_percent', 0),
            'memory_usage_percent': health.get('memory_usage_percent', 0),
            'uptime_hours': health.get('uptime_hours', 0)
        }
        
        # Alertas
        alerts = robot.get('alerts', [])
        alert_summary = {
            'total_alerts': len(alerts),
            'unacknowledged': len([a for a in alerts if not a.get('acknowledged', False)]),
            'by_severity': self._count_alerts_by_severity(alerts)
        }
        
        return {
            'robot_id': robot_id,
            'type': robot_type,
            'timestamp': robot['timestamp'],
            'location': location_metrics,
            'battery': battery_metrics,
            'sensors': sensor_metrics,
            'actuator_power_w': actuator_power,
            'mission': mission_metrics,
            'system_health': system_health,
            'alerts': alert_summary
        }
    
    def _calculate_battery_health_score(self, battery: Dict) -> float:
        """Calcula score de saúde da bateria"""
        soc = battery.get('soc_percent', 0)
        temp = battery.get('temperature_c', 25)
        voltage = battery.get('voltage_v', 48)
        
        # SOC score (80-100% = 1.0, 50-80% = 0.8, 20-50% = 0.5, <20% = 0.2)
        if soc >= 80:
            soc_score = 1.0
        elif soc >= 50:
            soc_score = 0.8
        elif soc >= 20:
            soc_score = 0.5
        else:
            soc_score = 0.2
        
        # Temperatura score (20-35°C = 1.0, 35-45°C = 0.8, >45°C = 0.6)
        if 20 <= temp <= 35:
            temp_score = 1.0
        elif 35 < temp <= 45:
            temp_score = 0.8
        elif temp > 45:
            temp_score = 0.6
        else:
            temp_score = 0.9
        
        # Tensão score (48-52V = 1.0 para sistema 48V nominal)
        voltage_score = 1.0 if 46 <= voltage <= 53 else 0.8
        
        # Score ponderado
        health_score = (soc_score * 0.5 + temp_score * 0.3 + voltage_score * 0.2)
        return round(health_score, 2)
    
    def _count_alerts_by_severity(self, alerts: List[Dict]) -> Dict:
        """Conta alertas por severidade"""
        by_severity = {'critical': 0, 'warning': 0, 'info': 0}
        for alert in alerts:
            severity = alert.get('severity', 'info')
            by_severity[severity] = by_severity.get(severity, 0) + 1
        return by_severity
    
    def _calculate_collection_stats(self, robot_metrics: List[Dict]) -> Dict:
        """Calcula estatísticas de coleta"""
        if not robot_metrics:
            return {
                'collection_rate': 0,
                'expected_robots': 0,
                'collected_robots': 0,
                'collection_success_rate': 0
            }
        
        total_robots = len(robot_metrics)
        
        # Métricas de bateria
        battery_socs = [m['battery']['soc_percent'] for m in robot_metrics]
        avg_battery_soc = sum(battery_socs) / len(battery_socs) if battery_socs else 0
        
        # Métricas de saúde
        health_statuses = [m['system_health']['overall_status'] for m in robot_metrics]
        healthy_count = sum(1 for s in health_statuses if s == 'healthy')
        
        # Métricas de missão
        mission_statuses = [m['mission']['status'] for m in robot_metrics]
        active_missions = sum(1 for s in mission_statuses if s not in ['idle', 'charging'])
        
        return {
            'total_robots': total_robots,
            'collection_success_rate': 100.0,  # Mock sempre 100%
            'average_battery_soc': round(avg_battery_soc, 1),
            'healthy_robots': healthy_count,
            'active_missions': active_missions,
            'total_alerts': sum(m['alerts']['total_alerts'] for m in robot_metrics)
        }
    
    def _assess_data_quality(self, robots: List[Dict], stats: Dict) -> Dict:
        """Avalia qualidade dos dados coletados"""
        # Completude (% de campos preenchidos)
        total_fields = 0
        filled_fields = 0
        
        for robot in robots:
            # Conta campos importantes
            if robot.get('position'):
                total_fields += 5
                filled_fields += 5  # Mock sempre completo
            
            if robot.get('battery'):
                total_fields += 7
                filled_fields += 7
            
            if robot.get('sensors'):
                total_fields += len(robot.get('sensors', {}))
                filled_fields += len([s for s in robot.get('sensors', {}).values() if s])
        
        completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
        
        # Latência (mock)
        latency_ms = 125  # Da system_health
        
        # Freshness (tempo desde última coleta)
        freshness_score = 1.0 if latency_ms < 200 else 0.8 if latency_ms < 500 else 0.5
        
        # Score geral de qualidade
        quality_score = (completeness / 100 * 0.5 + freshness_score * 0.3 + 
                        (stats['collection_success_rate'] / 100) * 0.2)
        
        return {
            'completeness_percent': round(completeness, 1),
            'latency_ms': latency_ms,
            'freshness_score': freshness_score,
            'quality_score': round(quality_score, 2),
            'quality_level': 'excellent' if quality_score >= 0.9 else 'good' if quality_score >= 0.7 else 'fair'
        }
    
    def display_collection_report(self, result: Dict):
        """Exibe relatório de coleta"""
        print("\n" + "="*70)
        print("📡 COLETA DE TELEMETRIA")
        print("="*70)
        
        stats = result['collection_stats']
        quality = result['data_quality']
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Robôs coletados: {stats['total_robots']}")
        print(f"   Taxa de sucesso: {stats['collection_success_rate']:.1f}%")
        print(f"   SOC médio: {stats['average_battery_soc']:.1f}%")
        print(f"   Robôs saudáveis: {stats['healthy_robots']}/{stats['total_robots']}")
        print(f"   Missões ativas: {stats['active_missions']}")
        print(f"   Total de alertas: {stats['total_alerts']}")
        
        print(f"\n💎 QUALIDADE DOS DADOS:")
        print(f"   Completude: {quality['completeness_percent']:.1f}%")
        print(f"   Latência: {quality['latency_ms']} ms")
        print(f"   Freshness: {quality['freshness_score']:.2f}")
        print(f"   Score geral: {quality['quality_score']:.2f}")
        print(f"   Nível: {quality['quality_level'].upper()}")
        
        print(f"\n🤖 MÉTRICAS POR ROBÔ:")
        for metric in result['robot_metrics'][:5]:  # Primeiros 5
            battery = metric['battery']
            health = metric['system_health']
            mission = metric['mission']
            
            status_icon = "✅" if health['overall_status'] == 'healthy' else "⚠️"
            print(f"\n   {status_icon} {metric['robot_id']} ({metric['type']})")
            print(f"      Bateria: {battery['soc_percent']}% | {battery['power_w']:.0f}W | Score {battery['health_score']}")
            print(f"      Sensores: {metric['sensors']['active_sensors']}/{metric['sensors']['total_sensors']} ativos ({metric['sensors']['sensor_health_percent']:.1f}%)")
            print(f"      Missão: {mission['status'].upper()} | {mission['progress_percent']:.0f}% | {mission['area_covered_ha']:.1f} ha")
            print(f"      CPU: {health['cpu_usage_percent']}% | RAM: {health['memory_usage_percent']}% | Uptime: {health['uptime_hours']:.1f}h")
            if metric['alerts']['total_alerts'] > 0:
                print(f"      ⚠️  Alertas: {metric['alerts']['total_alerts']} ({metric['alerts']['unacknowledged']} não reconhecidos)")


if __name__ == "__main__":
    print("📡 Telemetry - Metrics Collector Mock\n")
    print("="*70)
    
    # Inicializa coletor
    collector = MetricsCollector("TELEM-SESSION-20260220-154500")
    
    # Carrega dados
    data_file = Path(__file__).parent / "example_telemetry_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        telemetry_data = json.load(f)
    
    print(f"\n📡 Session: {telemetry_data['telemetry_session_id']}")
    print(f"   Timestamp: {telemetry_data['timestamp']}")
    print(f"   Intervalo: {telemetry_data['collection_interval_seconds']}s")
    
    # Coleta métricas
    result = collector.collect_metrics(telemetry_data)
    
    # Exibe relatório
    collector.display_collection_report(result)
    
    print("\n" + "="*70)
    print("✅ COLETA COMPLETA")
    print("="*70)
    print(f"\n💡 Total de coletas: {collector.collection_count}\n")
