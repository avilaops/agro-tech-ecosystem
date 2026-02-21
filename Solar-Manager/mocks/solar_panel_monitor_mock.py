#!/usr/bin/env python3
"""
Solar-Manager - Solar Panel Monitor Mock

Monitora painéis solares (geração, eficiência, condições ambientais)
"""

import json
import random
from pathlib import Path
from typing import Dict
from datetime import datetime, timedelta


class SolarPanelMonitor:
    """Monitor de painéis solares fotovoltaicos"""
    
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.monitoring_count = 0
        self.history = []
    
    def monitor_solar_array(self, solar_data: Dict) -> Dict:
        """
        Monitora array de painéis solares
        
        Em produção, isso seria:
        - Leitura de inversores solares via Modbus/RS485
        - Sensores de irradiância (piranômetros)
        - Sensores de temperatura (PT100/termopares)
        - Sistema de aquisição de dados (SCADA)
        
        Args:
            solar_data: Dados do sistema solar
        
        Returns:
            Status completo dos painéis
        """
        self.monitoring_count += 1
        
        panels = solar_data.get('solar_panels', {})
        env = panels.get('environmental_conditions', {})
        
        # Calcula métricas de performance
        performance = self._calculate_performance_metrics(panels, env)
        
        # Detecta anomalias
        anomalies = self._detect_anomalies(panels, performance)
        
        # Previsão de geração
        forecast = self._forecast_generation(env, solar_data.get('energy_forecast', {}))
        
        result = {
            'timestamp': solar_data['timestamp'],
            'station_id': self.station_id,
            'array_id': panels.get('array_id', 'UNKNOWN'),
            'monitoring_count': self.monitoring_count,
            'current_generation': panels.get('current_generation', {}),
            'environmental_conditions': env,
            'performance_metrics': performance,
            'anomalies': anomalies,
            'forecast': forecast,
            'status': 'normal' if len(anomalies) == 0 else 'warning'
        }
        
        self.history.append(result)
        return result
    
    def _calculate_performance_metrics(self, panels: Dict, env: Dict) -> Dict:
        """Calcula métricas de performance do array"""
        total_capacity_kw = panels.get('total_capacity_kwp', 0)
        current_power_kw = panels.get('current_generation', {}).get('power_kw', 0)
        irradiance = env.get('irradiance_w_m2', 0)
        
        # Eficiência atual vs nominal
        if total_capacity_kw > 0:
            capacity_factor = (current_power_kw / total_capacity_kw) * 100
        else:
            capacity_factor = 0
        
        # Performance ratio (PR): relação entre energia real e teórica
        # PR = Energia_Real / (Capacidade × Irradiância/1000)
        if irradiance > 0 and total_capacity_kw > 0:
            theoretical_power = total_capacity_kw * (irradiance / 1000)
            performance_ratio = (current_power_kw / theoretical_power) if theoretical_power > 0 else 0
        else:
            performance_ratio = 0
        
        # Temperatura de operação
        panel_temp = env.get('panel_temperature_c', 25)
        ambient_temp = env.get('ambient_temperature_c', 25)
        temp_rise = panel_temp - ambient_temp
        
        # Perda por temperatura (painéis perdem ~0.4%/°C acima de 25°C)
        temp_coefficient = -0.004  # -0.4% por °C
        temp_loss_percent = (panel_temp - 25) * temp_coefficient * 100
        
        return {
            'capacity_factor_percent': round(capacity_factor, 2),
            'performance_ratio': round(performance_ratio, 3),
            'current_efficiency_percent': panels.get('current_generation', {}).get('efficiency_percent', 0),
            'temperature_rise_c': round(temp_rise, 1),
            'temperature_loss_percent': round(temp_loss_percent, 2),
            'specific_yield_kwh_kwp': round(
                panels.get('daily_stats', {}).get('energy_generated_kwh', 0) / total_capacity_kw
                if total_capacity_kw > 0 else 0, 
                2
            )
        }
    
    def _detect_anomalies(self, panels: Dict, performance: Dict) -> list:
        """Detecta anomalias no sistema solar"""
        anomalies = []
        
        # Eficiência baixa
        if performance['current_efficiency_percent'] < 70:
            anomalies.append({
                'type': 'low_efficiency',
                'severity': 'warning',
                'value': performance['current_efficiency_percent'],
                'threshold': 70,
                'message': f"Eficiência baixa: {performance['current_efficiency_percent']:.1f}%"
            })
        
        # Performance Ratio baixo
        if performance['performance_ratio'] < 0.75:
            anomalies.append({
                'type': 'low_performance_ratio',
                'severity': 'warning',
                'value': performance['performance_ratio'],
                'threshold': 0.75,
                'message': f"Performance ratio baixo: {performance['performance_ratio']:.2f}"
            })
        
        # Temperatura elevada
        panel_temp = panels.get('environmental_conditions', {}).get('panel_temperature_c', 0)
        if panel_temp > 65:
            anomalies.append({
                'type': 'high_temperature',
                'severity': 'critical' if panel_temp > 75 else 'warning',
                'value': panel_temp,
                'threshold': 65,
                'message': f"Temperatura elevada: {panel_temp}°C"
            })
        
        # Perda por temperatura significativa
        if performance['temperature_loss_percent'] > 8:
            anomalies.append({
                'type': 'excessive_temp_loss',
                'severity': 'info',
                'value': performance['temperature_loss_percent'],
                'threshold': 8,
                'message': f"Perda por temperatura: {performance['temperature_loss_percent']:.1f}%"
            })
        
        return anomalies
    
    def _forecast_generation(self, env: Dict, forecast_data: Dict) -> Dict:
        """Prevê geração de energia baseado em condições"""
        irradiance = env.get('irradiance_w_m2', 0)
        cloud_cover = env.get('cloud_cover_percent', 0)
        
        # Próxima hora
        next_hour = forecast_data.get('next_hour', {})
        
        # Resto do dia
        today = forecast_data.get('today_remaining', {})
        
        # Classificação de condições
        if irradiance > 800 and cloud_cover < 20:
            conditions = 'excellent'
        elif irradiance > 600 and cloud_cover < 40:
            conditions = 'good'
        elif irradiance > 400:
            conditions = 'fair'
        else:
            conditions = 'poor'
        
        return {
            'current_conditions': conditions,
            'next_hour_kwh': next_hour.get('expected_generation_kwh', 0),
            'next_hour_confidence': next_hour.get('confidence_percent', 0),
            'today_remaining_kwh': today.get('expected_generation_kwh', 0),
            'remaining_sunshine_hours': today.get('remaining_sunshine_hours', 0)
        }
    
    def display_monitoring_report(self, result: Dict):
        """Exibe relatório de monitoramento"""
        print("\n" + "="*70)
        print("☀️  MONITORAMENTO DE PAINÉIS SOLARES")
        print("="*70)
        
        gen = result['current_generation']
        env = result['environmental_conditions']
        perf = result['performance_metrics']
        
        print(f"\n📍 ESTAÇÃO: {result['station_id']}")
        print(f"   Array: {result['array_id']}")
        print(f"   Status: {result['status'].upper()}")
        
        print(f"\n⚡ GERAÇÃO ATUAL:")
        print(f"   Potência: {gen['power_kw']:.2f} kW")
        print(f"   Tensão: {gen['voltage_v']:.1f} V")
        print(f"   Corrente: {gen['current_a']:.1f} A")
        print(f"   Eficiência: {gen['efficiency_percent']:.1f}%")
        
        print(f"\n🌤️  CONDIÇÕES AMBIENTAIS:")
        print(f"   Irradiância: {env['irradiance_w_m2']} W/m²")
        print(f"   Temp. painéis: {env['panel_temperature_c']}°C")
        print(f"   Temp. ambiente: {env['ambient_temperature_c']}°C")
        print(f"   Cobertura nuvens: {env['cloud_cover_percent']}%")
        print(f"   Elevação solar: {env['sun_elevation_deg']}°")
        
        print(f"\n📊 PERFORMANCE:")
        print(f"   Fator de capacidade: {perf['capacity_factor_percent']:.1f}%")
        print(f"   Performance ratio: {perf['performance_ratio']:.3f}")
        print(f"   Perda por temperatura: {abs(perf['temperature_loss_percent']):.1f}%")
        
        if result['anomalies']:
            print(f"\n⚠️  ANOMALIAS DETECTADAS: {len(result['anomalies'])}")
            for anomaly in result['anomalies']:
                severity_icon = "🔴" if anomaly['severity'] == 'critical' else "🟡" if anomaly['severity'] == 'warning' else "ℹ️"
                print(f"   {severity_icon} {anomaly['message']}")
        else:
            print(f"\n✅ NENHUMA ANOMALIA DETECTADA")
        
        forecast = result['forecast']
        print(f"\n🔮 PREVISÃO:")
        print(f"   Condições: {forecast['current_conditions'].upper()}")
        print(f"   Próxima hora: {forecast['next_hour_kwh']:.1f} kWh ({forecast['next_hour_confidence']}% confiança)")
        print(f"   Resto do dia: {forecast['today_remaining_kwh']:.1f} kWh")


if __name__ == "__main__":
    print("☀️  Solar-Manager - Solar Panel Monitor Mock\n")
    print("="*70)
    
    # Inicializa monitor
    monitor = SolarPanelMonitor("SOLAR-STATION-001")
    
    # Carrega dados de exemplo
    data_file = Path(__file__).parent / "example_solar_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        solar_data = json.load(f)
    
    print(f"\n☀️  Estação: {solar_data['station_id']}")
    print(f"   Localização: {solar_data['location']['name']}")
    print(f"   Capacidade: {solar_data['solar_panels']['total_capacity_kwp']:.2f} kWp")
    print(f"   Painéis: {solar_data['solar_panels']['total_panels']} unidades")
    
    # Monitora array
    result = monitor.monitor_solar_array(solar_data)
    
    # Exibe relatório
    monitor.display_monitoring_report(result)
    
    print("\n" + "="*70)
    print("✅ MONITORAMENTO COMPLETO")
    print("="*70)
    print(f"\n💡 Total de leituras: {monitor.monitoring_count}\n")
