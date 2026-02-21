#!/usr/bin/env python3
"""
Robot Simulator Mock - CanaSwarm Simulator

Integra física, ambiente e missão para simular robô completo em tempo real.

Author: CanaSwarm Team
Date: 2026-02-20
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


class RobotSimulator:
    """Simulador completo de robô autônomo"""
    
    def __init__(self, robot_data: Dict[str, Any], environment: Dict[str, Any], 
                 physics_engine, environment_simulator):
        """
        Inicializa robot simulator
        
        Args:
            robot_data: Dados iniciais do robô
            environment: Estado do ambiente
            physics_engine: Engine de física
            environment_simulator: Simulador de ambiente
        """
        self.robot = robot_data.copy()
        self.physics_engine = physics_engine
        self.env_simulator = environment_simulator
        self.timestep = physics_engine.timestep
        
        # Estatísticas de simulação
        self.stats = {
            'total_timesteps': 0,
            'distance_traveled_km': 0.0,
            'energy_consumed_kwh': 0.0,
            'area_harvested_ha': 0.0,
            'collisions': 0,
            'mission_progress_percent': robot_data['state']['mission'].get('progress_percent', 0)
        }
        
    def update(self) -> Dict[str, Any]:
        """
        Atualiza simulação do robô (1 timestep)
        
        Returns:
            Estado atualizado completo
        """
        # 1. Ler ambiente atual
        environment = self.env_simulator.environment
        
        # 2. Executar lógica de missão (decide ações)
        mission_actions = self._execute_mission_logic()
        
        # 3. Aplicar ações aos atuadores
        self._apply_actions(mission_actions)
        
        # 4. Atualizar física (movimento)
        physics_result = self.physics_engine.update_robot_physics(self.robot, environment)
        self.robot['state'] = physics_result['state']
        
        # 5. Atualizar bateria
        battery_result = self.physics_engine.update_battery_physics(self.robot, environment)
        self.robot['state']['battery'] = battery_result['battery']
        
        # 6. Atualizar sensores (leituras com ruído)
        self._update_sensors(environment)
        
        # 7. Atualizar progresso da missão
        self._update_mission_progress()
        
        # 8. Atualizar health status
        self._update_health_status()
        
        # 9. Atualizar estatísticas
        self._update_statistics(physics_result, battery_result)
        
        # 10. Gerar alertas se necessário
        alerts = self._check_alerts()
        
        # 11. Registrar colisões
        if physics_result['collisions']:
            self.stats['collisions'] += len(physics_result['collisions'])
        
        self.stats['total_timesteps'] += 1
        
        return {
            'robot': self.robot,
            'physics': physics_result,
            'battery': battery_result,
            'alerts': alerts,
            'statistics': self.stats.copy()
        }
    
    def _execute_mission_logic(self) -> Dict[str, Any]:
        """
        Lógica de decisão da missão
        
        Returns:
            Ações a executar (velocidade, direção, blade, etc)
        """
        mission = self.robot['state']['mission']
        battery = self.robot['state']['battery']
        
        # Se bateria crítica (<20%), parar e procurar estação de carga
        if battery['soc_percent'] < 20 and not battery['charging']:
            return {
                'target_speed_ms': 0.0,
                'target_heading_deg': self.robot['state']['position']['heading_deg'],
                'blade_active': False,
                'action': 'emergency_stop_low_battery'
            }
        
        # Se carregando, ficar parado
        if battery['charging']:
            # Descarregar termina se SOC >= 80%
            if battery['soc_percent'] >= 80:
                self.robot['state']['battery']['charging'] = False
                mission['status'] = 'idle'
            
            return {
                'target_speed_ms': 0.0,
                'target_heading_deg': self.robot['state']['position']['heading_deg'],
                'blade_active': False,
                'action': 'charging'
            }
        
        # Lógica por tipo de missão
        if mission['status'] == 'harvesting':
            # Harvesting: velocidade moderada, blade ativa, seguir waypoints
            progress = mission['progress_percent']
            
            # Velocidade depende de densidade de plantas e terreno
            position = self.robot['state']['position']
            plant_density = self.env_simulator.get_plant_density(position['lat'], position['lon'])
            
            # Mais denso = mais lento
            target_speed = 1.5 - plant_density * 0.8  # 0.7 - 1.5 m/s
            
            # Heading: avançar em linha (simplificado - sem waypoint navigation aqui)
            current_heading = position['heading_deg']
            target_heading = current_heading  # Manter direção
            
            return {
                'target_speed_ms': target_speed,
                'target_heading_deg': target_heading,
                'blade_active': True,
                'action': 'harvesting'
            }
        
        elif mission['status'] == 'transporting':
            # Transport: velocidade alta, sem blade
            return {
                'target_speed_ms': 2.2,
                'target_heading_deg': self._calculate_heading_to_destination(),
                'blade_active': False,
                'action': 'transporting'
            }
        
        elif mission['status'] == 'idle':
            # Idle: parado
            return {
                'target_speed_ms': 0.0,
                'target_heading_deg': self.robot['state']['position']['heading_deg'],
                'blade_active': False,
                'action': 'idle'
            }
        
        else:
            # Default: parado
            return {
                'target_speed_ms': 0.0,
                'target_heading_deg': self.robot['state']['position']['heading_deg'],
                'blade_active': False,
                'action': 'unknown'
            }
    
    def _apply_actions(self, actions: Dict[str, Any]):
        """Aplica ações aos atuadores do robô"""
        actuators = self.robot['state']['actuators']
        current_velocity = self.robot['state']['velocity']['linear_ms']
        
        # Controle de velocidade (PID simplificado)
        target_speed = actions['target_speed_ms']
        speed_error = target_speed - current_velocity
        
        # Torque proporcional ao erro de velocidade
        torque_factor = 10  # Ganho proporcional
        target_torque = speed_error * torque_factor
        target_torque = max(0, min(40, target_torque))  # Limitar 0-40 Nm
        
        # Atualizar motores
        if 'left_motor' in actuators:
            actuators['left_motor']['torque_nm'] = target_torque
            actuators['left_motor']['rpm'] = self._torque_to_rpm(target_torque, current_velocity)
            actuators['left_motor']['power_w'] = self._calculate_motor_power(actuators['left_motor'])
        
        if 'right_motor' in actuators:
            actuators['right_motor']['torque_nm'] = target_torque
            actuators['right_motor']['rpm'] = self._torque_to_rpm(target_torque, current_velocity)
            actuators['right_motor']['power_w'] = self._calculate_motor_power(actuators['right_motor'])
        
        # Atualizar blade
        if 'blade' in actuators:
            actuators['blade']['active'] = actions['blade_active']
            if actions['blade_active']:
                actuators['blade']['rpm'] = 850
                actuators['blade']['power_w'] = 1200
            else:
                actuators['blade']['rpm'] = 0
                actuators['blade']['power_w'] = 0
        
        # Atualizar steering (simplificado)
        if 'steering' in actuators:
            current_heading = self.robot['state']['position']['heading_deg']
            target_heading = actions['target_heading_deg']
            heading_error = self._normalize_angle(target_heading - current_heading)
            
            # Steering angle proporcional ao erro
            steering_angle = heading_error * 0.3  # Ganho
            steering_angle = max(-30, min(30, steering_angle))  # Limitar ±30°
            
            actuators['steering']['angle_deg'] = steering_angle
            actuators['steering']['servo_position_percent'] = 50 + (steering_angle / 30) * 50
    
    def _torque_to_rpm(self, torque_nm: float, velocity_ms: float) -> float:
        """Converte torque e velocidade em RPM da roda"""
        wheel_radius = self.robot['physics']['wheel_radius_m']
        
        # Velocidade angular da roda (rad/s)
        if wheel_radius > 0:
            omega_rad_per_s = velocity_ms / wheel_radius
            rpm = omega_rad_per_s * 60 / (2 * math.pi)
        else:
            rpm = 0
        
        return max(0, rpm)
    
    def _calculate_motor_power(self, motor: Dict) -> float:
        """Calcula potência do motor (P = τ × ω)"""
        torque_nm = motor.get('torque_nm', 0)
        rpm = motor.get('rpm', 0)
        
        # Converter RPM para rad/s
        omega_rad_per_s = rpm * 2 * math.pi / 60
        
        # P = τ × ω
        power_w = torque_nm * omega_rad_per_s
        
        return power_w
    
    def _calculate_heading_to_destination(self) -> float:
        """Calcula heading para destino (transport missions)"""
        mission = self.robot['state']['mission']
        
        if 'destination' not in mission:
            return self.robot['state']['position']['heading_deg']
        
        current_pos = self.robot['state']['position']
        dest = mission['destination']
        
        # Calcular bearing entre dois pontos GPS
        lat1 = math.radians(current_pos['lat'])
        lat2 = math.radians(dest['lat'])
        lon1 = math.radians(current_pos['lon'])
        lon2 = math.radians(dest['lon'])
        
        delta_lon = lon2 - lon1
        
        x = math.sin(delta_lon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
        
        bearing_rad = math.atan2(x, y)
        bearing_deg = math.degrees(bearing_rad)
        bearing_deg = (bearing_deg + 360) % 360  # Normalizar 0-360
        
        return bearing_deg
    
    def _normalize_angle(self, angle_deg: float) -> float:
        """Normaliza ângulo para ±180°"""
        while angle_deg > 180:
            angle_deg -= 360
        while angle_deg < -180:
            angle_deg += 360
        return angle_deg
    
    def _update_sensors(self, environment: Dict):
        """Atualiza leituras dos sensores (com ruído)"""
        sensors = self.robot['state']['sensors']
        position = self.robot['state']['position']
        
        # GPS: adicionar ruído
        if 'gps' in sensors:
            noise_m = sensors['gps'].get('noise_m', 0.02)
            # Ruído já está no modelo, apenas registrar
        
        # IMU: adicionar ruído de giroscópio
        if 'imu' in sensors:
            gyro_noise = sensors['imu'].get('gyro_noise_deg_per_s', 0.1)
            sensors['imu']['yaw_deg'] = position['heading_deg'] + random.uniform(-gyro_noise, gyro_noise)
        
        # LiDAR: detectar obstáculos
        if 'lidar' in sensors:
            obstacles = self.env_simulator.check_obstacle_at(
                position['lat'], 
                position['lon'], 
                radius_m=sensors['lidar']['range_m']
            )
            sensors['lidar']['obstacles_detected'] = len(obstacles)
        
        # Câmera: detectar objetos (simplificado - baseado em densidade de plantas)
        if 'camera_front' in sensors:
            plant_density = self.env_simulator.get_plant_density(position['lat'], position['lon'])
            objects_detected = int(plant_density * 15)  # 0-15 objetos
            sensors['camera_front']['objects_detected'] = objects_detected
    
    def _update_mission_progress(self):
        """Atualiza progresso da missão"""
        mission = self.robot['state']['mission']
        velocity = self.robot['state']['velocity']['linear_ms']
        
        if mission['status'] == 'harvesting' and velocity > 0.1:
            # Área coberta proporcional a velocidade e largura de trabalho
            work_width_m = 2.0  # Largura de colheita
            area_m2_per_timestep = velocity * work_width_m * self.timestep
            area_ha_per_timestep = area_m2_per_timestep / 10000
            
            mission['area_covered_ha'] = mission.get('area_covered_ha', 0) + area_ha_per_timestep
            mission['area_remaining_ha'] = max(0, mission.get('area_remaining_ha', 5.0) - area_ha_per_timestep)
            
            # Progresso baseado em área
            total_area = mission['area_covered_ha'] + mission['area_remaining_ha']
            if total_area > 0:
                mission['progress_percent'] = (mission['area_covered_ha'] / total_area) * 100
            
            # Atualizar estatísticas
            self.stats['area_harvested_ha'] = mission['area_covered_ha']
        
        elif mission['status'] == 'transporting':
            # Progresso baseado em distância até destino
            if 'destination' in mission:
                position = self.robot['state']['position']
                dest = mission['destination']
                distance_m = self._haversine_distance(
                    position['lat'], position['lon'],
                    dest['lat'], dest['lon']
                )
                
                # Assumir distância inicial de 1000m
                initial_distance = 1000
                mission['progress_percent'] = max(0, (1 - distance_m / initial_distance) * 100)
                
                # Se chegou (<5m), completar missão
                if distance_m < 5:
                    mission['status'] = 'idle'
                    mission['progress_percent'] = 100
    
    def _update_health_status(self):
        """Atualiza status de saúde do robô"""
        health = self.robot['state']['health']
        battery = self.robot['state']['battery']
        
        # CPU usage varia com carga de trabalho
        mission = self.robot['state']['mission']
        if mission['status'] == 'harvesting':
            health['cpu_usage_percent'] = 70 + random.uniform(-5, 10)
        elif mission['status'] == 'transporting':
            health['cpu_usage_percent'] = 40 + random.uniform(-5, 5)
        else:
            health['cpu_usage_percent'] = 30 + random.uniform(-5, 5)
        
        health['cpu_usage_percent'] = max(20, min(95, health['cpu_usage_percent']))
        
        # Memory usage aumenta lentamente
        health['memory_usage_percent'] += random.uniform(-0.5, 1.0) * self.timestep
        health['memory_usage_percent'] = max(40, min(90, health['memory_usage_percent']))
        
        # Uptime
        health['uptime_hours'] += self.timestep / 3600
        
        # Overall status baseado em condições
        if battery['soc_percent'] < 20:
            health['overall_status'] = 'critical'
        elif battery['soc_percent'] < 40 or battery['temperature_c'] > 50:
            health['overall_status'] = 'warning'
        else:
            health['overall_status'] = 'healthy'
    
    def _update_statistics(self, physics_result: Dict, battery_result: Dict):
        """Atualiza estatísticas de simulação"""
        velocity = physics_result['state']['velocity']['linear_ms']
        distance_m = velocity * self.timestep
        self.stats['distance_traveled_km'] += distance_m / 1000
        
        energy_wh = abs(battery_result['energy_change_wh'])
        self.stats['energy_consumed_kwh'] += energy_wh / 1000
        
        self.stats['mission_progress_percent'] = self.robot['state']['mission']['progress_percent']
    
    def _check_alerts(self) -> List[Dict]:
        """Verifica e gera alertas"""
        alerts = []
        battery = self.robot['state']['battery']
        health = self.robot['state']['health']
        
        # Battery alerts
        if battery['soc_percent'] < 20:
            alerts.append({
                'severity': 'critical',
                'type': 'battery_critical',
                'message': f"Bateria crítica: {battery['soc_percent']}%",
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        elif battery['soc_percent'] < 50 and not battery['charging']:
            alerts.append({
                'severity': 'warning',
                'type': 'battery_low',
                'message': f"Bateria baixa: {battery['soc_percent']}%",
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        # Temperature alerts
        if battery['temperature_c'] > 50:
            alerts.append({
                'severity': 'warning',
                'type': 'temperature_high',
                'message': f"Temperatura alta: {battery['temperature_c']}°C",
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        # CPU alerts
        if health['cpu_usage_percent'] > 90:
            alerts.append({
                'severity': 'warning',
                'type': 'cpu_high',
                'message': f"CPU alto: {health['cpu_usage_percent']}%",
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        return alerts
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância Haversine"""
        R = 6371000  # Raio da Terra em metros
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c


def main():
    """Testa robot simulator"""
    print("🤖 Simulator - Robot Simulator Mock")
    print("=" * 70)
    
    # Carregar dados
    with open('example_simulation_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Import engines (simulação interna)
    import sys
    sys.path.insert(0, '.')
    from physics_engine_mock import PhysicsEngine
    from environment_simulator_mock import EnvironmentSimulator
    
    # Inicializar componentes
    physics_engine = PhysicsEngine(data['config'])
    env_simulator = EnvironmentSimulator(data['environment'], data['config'])
    
    # Simular MICROBOT-002 (harvesting)
    robot_data = data['robots'][1]
    robot_sim = RobotSimulator(robot_data, data['environment'], physics_engine, env_simulator)
    
    print(f"\n🤖 ROBÔ: {robot_sim.robot['robot_id']} ({robot_sim.robot['type']})")
    print(f"   Missão: {robot_sim.robot['state']['mission']['status']}")
    print(f"   SOC inicial: {robot_sim.robot['state']['battery']['soc_percent']}%")
    print(f"   Posição: ({robot_sim.robot['state']['position']['lat']:.6f}, {robot_sim.robot['state']['position']['lon']:.6f})")
    
    # Simular 30 segundos
    duration = 30  # segundos
    timestep = data['config']['timestep_seconds']
    steps = int(duration / timestep)
    
    print(f"\n⏱️  SIMULANDO {duration}s ({steps} timesteps de {timestep}s)...")
    
    # Amostrar a cada 10 segundos
    sample_interval = 10  # segundos
    sample_steps = int(sample_interval / timestep)
    
    for step in range(steps):
        result = robot_sim.update()
        env_simulator.update_environment(timestep)
        
        if (step + 1) % sample_steps == 0:
            elapsed = (step + 1) * timestep
            robot = result['robot']
            stats = result['statistics']
            
            print(f"\n   t={elapsed:.0f}s:")
            print(f"      Posição: ({robot['state']['position']['lat']:.6f}, {robot['state']['position']['lon']:.6f})")
            print(f"      Velocidade: {robot['state']['velocity']['linear_ms']:.2f} m/s")
            print(f"      SOC: {robot['state']['battery']['soc_percent']:.1f}%")
            print(f"      Progresso missão: {robot['state']['mission']['progress_percent']:.1f}%")
            print(f"      Distância: {stats['distance_traveled_km']*1000:.1f} m")
            print(f"      Energia: {stats['energy_consumed_kwh']*1000:.2f} Wh")
            
            if result['alerts']:
                print(f"      ⚠️  Alertas: {len(result['alerts'])}")
                for alert in result['alerts']:
                    print(f"         - {alert['type']}: {alert['message']}")
    
    # Estatísticas finais
    print(f"\n\n📊 ESTATÍSTICAS FINAIS:")
    stats = robot_sim.stats
    print(f"   Timesteps: {stats['total_timesteps']}")
    print(f"   Distância percorrida: {stats['distance_traveled_km']*1000:.1f} m")
    print(f"   Energia consumida: {stats['energy_consumed_kwh']*1000:.1f} Wh")
    print(f"   Área colhida: {stats['area_harvested_ha']:.3f} ha")
    if stats['energy_consumed_kwh'] > 0:
        efficiency = stats['area_harvested_ha'] / stats['energy_consumed_kwh']
        print(f"   Eficiência: {efficiency:.2f} ha/kWh")
    print(f"   Colisões: {stats['collisions']}")
    print(f"   Progresso missão: {stats['mission_progress_percent']:.1f}%")
    
    print(f"\n✅ Robot simulator funcionando!")


if __name__ == '__main__':
    main()
