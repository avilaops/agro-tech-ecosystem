#!/usr/bin/env python3
"""
Physics Engine Mock - CanaSwarm Simulator

Simula física realista dos robôs: movimento, forças, bateria, colisões.

Author: CanaSwarm Team
Date: 2026-02-20
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


class PhysicsEngine:
    """Motor de física para simulação de robôs autônomos"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa physics engine
        
        Args:
            config: Configuração da simulação (timestep, collision_detection, etc)
        """
        self.config = config
        self.timestep = config.get('timestep_seconds', 0.1)
        self.collision_detection = config.get('collision_detection', True)
        self.gravity = 9.81  # m/s²
        
    def update_robot_physics(self, robot: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza física do robô (posição, velocidade, forças)
        
        Args:
            robot: Estado atual do robô
            environment: Estado do ambiente (terreno, clima)
            
        Returns:
            Estado atualizado do robô com novos valores de física
        """
        state = robot['state']
        physics = robot['physics']
        
        # 1. Calcular forças atuantes
        forces = self._calculate_forces(state, physics, environment)
        
        # 2. Atualizar aceleração (F = ma)
        acceleration = self._calculate_acceleration(forces, physics['mass_kg'])
        
        # 3. Atualizar velocidade (v = v0 + at)
        velocity = self._update_velocity(state['velocity'], acceleration, self.timestep)
        
        # 4. Atualizar posição (s = s0 + vt)
        position = self._update_position(state['position'], velocity, self.timestep, environment)
        
        # 5. Detectar colisões
        collisions = []
        if self.collision_detection:
            collisions = self._detect_collisions(position, robot, environment)
        
        # 6. Atualizar estado
        updated_state = state.copy()
        updated_state['position'] = position
        updated_state['velocity'] = velocity
        updated_state['acceleration'] = acceleration
        
        return {
            'state': updated_state,
            'forces': forces,
            'collisions': collisions
        }
    
    def _calculate_forces(self, state: Dict, physics: Dict, environment: Dict) -> Dict[str, float]:
        """Calcula todas as forças atuantes no robô"""
        
        # Forças dos motores (propulsão)
        motor_force = self._calculate_motor_force(state['actuators'], physics)
        
        # Resistência ao rolamento (Fr = Crr × N)
        rolling_resistance = physics['rolling_resistance'] * physics['mass_kg'] * self.gravity
        
        # Arrasto aerodinâmico (Fd = 0.5 × ρ × Cd × A × v²)
        air_density = 1.225  # kg/m³ at sea level
        frontal_area = physics['dimensions_m']['width'] * physics['dimensions_m']['height']
        velocity_ms = state['velocity']['linear_ms']
        drag_force = 0.5 * air_density * physics['drag_coefficient'] * frontal_area * (velocity_ms ** 2)
        
        # Força gravitacional em declive (Fg = m × g × sin(θ))
        terrain = environment.get('terrain', {})
        slope_deg = terrain.get('slope_avg_deg', 0)
        slope_rad = math.radians(slope_deg)
        gravity_force = physics['mass_kg'] * self.gravity * math.sin(slope_rad)
        
        # Força do vento
        wind_speed_ms = environment.get('weather', {}).get('wind_speed_ms', 0)
        wind_direction_deg = environment.get('weather', {}).get('wind_direction_deg', 0)
        heading_deg = state['position']['heading_deg']
        wind_relative_deg = wind_direction_deg - heading_deg
        wind_force = 0.5 * air_density * frontal_area * (wind_speed_ms ** 2) * math.cos(math.radians(wind_relative_deg))
        
        # Força resultante
        net_force = motor_force - rolling_resistance - drag_force - gravity_force + wind_force
        
        return {
            'motor_force_n': motor_force,
            'rolling_resistance_n': rolling_resistance,
            'drag_force_n': drag_force,
            'gravity_force_n': gravity_force,
            'wind_force_n': wind_force,
            'net_force_n': net_force
        }
    
    def _calculate_motor_force(self, actuators: Dict, physics: Dict) -> float:
        """Calcula força dos motores baseado em torque e raio da roda"""
        left_motor = actuators.get('left_motor', {})
        right_motor = actuators.get('right_motor', {})
        
        left_torque_nm = left_motor.get('torque_nm', 0)
        right_torque_nm = right_motor.get('torque_nm', 0)
        
        total_torque = left_torque_nm + right_torque_nm
        wheel_radius = physics.get('wheel_radius_m', 0.35)
        
        # F = τ / r
        force = total_torque / wheel_radius if wheel_radius > 0 else 0
        
        return force
    
    def _calculate_acceleration(self, forces: Dict, mass_kg: float) -> Dict[str, float]:
        """Calcula aceleração linear e angular"""
        
        # Aceleração linear (a = F/m)
        linear_ms2 = forces['net_force_n'] / mass_kg if mass_kg > 0 else 0
        
        # Aceleração angular (simplificado - baseado em diferença de torque)
        # Em simulação real, seria momento de inércia × aceleração angular
        angular_deg_per_s2 = 0.0  # Calculado separadamente pelo steering
        
        return {
            'linear_ms2': linear_ms2,
            'angular_deg_per_s2': angular_deg_per_s2
        }
    
    def _update_velocity(self, velocity: Dict, acceleration: Dict, dt: float) -> Dict[str, float]:
        """Atualiza velocidade baseado em aceleração"""
        
        # v = v0 + a×t
        linear_ms = velocity['linear_ms'] + acceleration['linear_ms2'] * dt
        angular_deg_per_s = velocity['angular_deg_per_s'] + acceleration['angular_deg_per_s2'] * dt
        
        # Limitar velocidade máxima (evitar valores irreais)
        linear_ms = max(0, min(linear_ms, 3.0))  # Max 3 m/s
        angular_deg_per_s = max(-45, min(angular_deg_per_s, 45))  # Max ±45°/s
        
        return {
            'linear_ms': linear_ms,
            'angular_deg_per_s': angular_deg_per_s
        }
    
    def _update_position(self, position: Dict, velocity: Dict, dt: float, environment: Dict) -> Dict[str, float]:
        """Atualiza posição baseado em velocidade"""
        
        # Movimento linear
        distance_m = velocity['linear_ms'] * dt
        heading_rad = math.radians(position['heading_deg'])
        
        # Conversão aproximada: 1° lat ≈ 111km, 1° lon ≈ 111km × cos(lat)
        lat_change = (distance_m * math.cos(heading_rad)) / 111000
        lon_change = (distance_m * math.sin(heading_rad)) / (111000 * math.cos(math.radians(position['lat'])))
        
        new_lat = position['lat'] + lat_change
        new_lon = position['lon'] + lon_change
        
        # Atualizar altitude baseado em terreno (simplificado)
        terrain = environment.get('terrain', {})
        elevation_min = terrain.get('elevation', {}).get('min_m', 580)
        elevation_max = terrain.get('elevation', {}).get('max_m', 610)
        # Altitude varia com posição (modelo simplificado)
        altitude_m = elevation_min + (elevation_max - elevation_min) * 0.5
        
        # Rotação
        heading_deg = position['heading_deg'] + velocity['angular_deg_per_s'] * dt
        heading_deg = heading_deg % 360  # Normalizar 0-360
        
        return {
            'lat': new_lat,
            'lon': new_lon,
            'altitude_m': altitude_m,
            'heading_deg': heading_deg
        }
    
    def _detect_collisions(self, position: Dict, robot: Dict, environment: Dict) -> List[Dict]:
        """Detecta colisões com obstáculos e outros objetos"""
        collisions = []
        
        robot_lat = position['lat']
        robot_lon = position['lon']
        robot_radius = robot['physics']['dimensions_m']['length'] / 2
        
        # Verificar colisões com obstáculos
        obstacles = environment.get('terrain', {}).get('obstacles', [])
        
        for obstacle in obstacles:
            obs_lat = obstacle['position']['lat']
            obs_lon = obstacle['position']['lon']
            obs_radius = obstacle['radius_m']
            
            # Distância entre robô e obstáculo
            distance_m = self._haversine_distance(robot_lat, robot_lon, obs_lat, obs_lon)
            
            # Colisão se distância < soma dos raios
            if distance_m < (robot_radius + obs_radius):
                collisions.append({
                    'type': 'obstacle',
                    'object': obstacle['type'],
                    'distance_m': distance_m,
                    'severity': 'minor' if distance_m > (robot_radius + obs_radius) * 0.8 else 'major',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
        
        return collisions
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância entre dois pontos GPS (Haversine)"""
        R = 6371000  # Raio da Terra em metros
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def update_battery_physics(self, robot: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza física da bateria (consumo, carga, temperatura)
        
        Args:
            robot: Estado do robô
            environment: Estado do ambiente (solar irradiance)
            
        Returns:
            Estado atualizado da bateria
        """
        battery = robot['state']['battery'].copy()
        actuators = robot['state']['actuators']
        
        # 1. Calcular consumo total de potência
        power_consumption_w = self._calculate_power_consumption(actuators, robot['state'])
        
        # 2. Calcular carga solar (se carregando)
        power_solar_w = 0
        if battery.get('charging', False):
            solar = environment.get('solar', {})
            power_solar_w = self._calculate_solar_charging(solar, robot)
        
        # 3. Potência líquida (negativo = descarga, positivo = carga)
        power_net_w = power_solar_w - power_consumption_w
        
        # 4. Atualizar SOC (State of Charge)
        capacity_wh = battery['capacity_ah'] * battery['voltage_v']
        energy_change_wh = (power_net_w * self.timestep) / 3600  # W×s → Wh
        soc_change_percent = (energy_change_wh / capacity_wh) * 100
        
        new_soc = battery['soc_percent'] + soc_change_percent
        new_soc = max(0, min(100, new_soc))  # Limitar 0-100%
        
        # 5. Atualizar corrente (I = P/V)
        new_current_a = power_net_w / battery['voltage_v'] if battery['voltage_v'] > 0 else 0
        
        # 6. Atualizar temperatura (modelo simplificado)
        ambient_temp = environment.get('weather', {}).get('temperature_c', 25)
        heat_generation = abs(power_net_w) * 0.1  # 10% de perdas térmicas
        temp_rise = heat_generation / 1000  # Simplificado
        
        new_temp = battery['temperature_c'] + (temp_rise - (battery['temperature_c'] - ambient_temp) * 0.01) * self.timestep
        new_temp = max(ambient_temp - 5, min(70, new_temp))  # Limites realistas
        
        # 7. Atualizar tensão baseado em SOC (curva simplificada)
        nominal_voltage = 48.0
        voltage_range = 6.0  # 45-51V
        new_voltage = nominal_voltage + (new_soc - 50) * (voltage_range / 100)
        
        battery_updated = {
            'soc_percent': round(new_soc, 1),
            'voltage_v': round(new_voltage, 1),
            'current_a': round(new_current_a, 1),
            'temperature_c': round(new_temp, 1),
            'capacity_ah': battery['capacity_ah'],
            'charging': battery['charging'],
            'cycles': battery['cycles']
        }
        
        return {
            'battery': battery_updated,
            'power_consumption_w': power_consumption_w,
            'power_solar_w': power_solar_w,
            'power_net_w': power_net_w,
            'energy_change_wh': energy_change_wh
        }
    
    def _calculate_power_consumption(self, actuators: Dict, state: Dict) -> float:
        """Calcula consumo total de potência dos atuadores"""
        total_power_w = 0
        
        # Motores de tração
        if 'left_motor' in actuators:
            total_power_w += actuators['left_motor'].get('power_w', 0)
        if 'right_motor' in actuators:
            total_power_w += actuators['right_motor'].get('power_w', 0)
        
        # Lâmina de corte
        if 'blade' in actuators and actuators['blade'].get('active', False):
            total_power_w += actuators['blade'].get('power_w', 0)
        
        # Sistemas auxiliares (CPU, sensores, comunicação) - constante
        total_power_w += 50  # 50W baseline
        
        # CPU usage aumenta consumo
        cpu_percent = state.get('health', {}).get('cpu_usage_percent', 40)
        compute_power_w = (cpu_percent / 100) * 30  # Max 30W para processamento
        total_power_w += compute_power_w
        
        return total_power_w
    
    def _calculate_solar_charging(self, solar: Dict, robot: Dict) -> float:
        """Calcula potência de carga solar"""
        irradiance_w_per_m2 = solar.get('irradiance_w_per_m2', 0)
        
        # Área de painéis solares (topo do robô)
        panel_area_m2 = robot['physics']['dimensions_m']['length'] * robot['physics']['dimensions_m']['width']
        panel_efficiency = 0.20  # 20% eficiência
        
        # Potência solar = Irradiância × Área × Eficiência
        power_solar_w = irradiance_w_per_m2 * panel_area_m2 * panel_efficiency
        
        return power_solar_w


def main():
    """Testa physics engine com dados do exemplo"""
    print("🔬 Simulator - Physics Engine Mock")
    print("=" * 70)
    
    # Carregar dados
    with open('example_simulation_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Inicializar physics engine
    engine = PhysicsEngine(data['config'])
    
    print(f"\n⚙️  CONFIGURAÇÃO:")
    print(f"   Timestep: {engine.timestep}s")
    print(f"   Collision detection: {engine.collision_detection}")
    
    # Testar física de movimento do MICROBOT-002 (harvesting)
    robot = data['robots'][1]  # MICROBOT-002
    environment = data['environment']
    
    print(f"\n🤖 ROBÔ: {robot['robot_id']} ({robot['type']})")
    print(f"   Posição inicial: {robot['state']['position']['lat']:.6f}, {robot['state']['position']['lon']:.6f}")
    print(f"   Velocidade: {robot['state']['velocity']['linear_ms']} m/s")
    print(f"   Heading: {robot['state']['position']['heading_deg']}°")
    
    # Update física
    physics_result = engine.update_robot_physics(robot, environment)
    
    print(f"\n⚡ FORÇAS:")
    forces = physics_result['forces']
    print(f"   Motor: {forces['motor_force_n']:.1f} N")
    print(f"   Resistência rolamento: {forces['rolling_resistance_n']:.1f} N")
    print(f"   Arrasto aerodinâmico: {forces['drag_force_n']:.1f} N")
    print(f"   Gravidade (declive): {forces['gravity_force_n']:.1f} N")
    print(f"   Vento: {forces['wind_force_n']:.1f} N")
    print(f"   ➜ Força resultante: {forces['net_force_n']:.1f} N")
    
    print(f"\n📍 POSIÇÃO ATUALIZADA:")
    new_pos = physics_result['state']['position']
    print(f"   Nova posição: {new_pos['lat']:.6f}, {new_pos['lon']:.6f}")
    print(f"   Nova velocidade: {physics_result['state']['velocity']['linear_ms']:.2f} m/s")
    print(f"   Nova aceleração: {physics_result['state']['acceleration']['linear_ms2']:.3f} m/s²")
    
    if physics_result['collisions']:
        print(f"\n💥 COLISÕES: {len(physics_result['collisions'])}")
        for col in physics_result['collisions']:
            print(f"   ⚠️  {col['object']}: distância {col['distance_m']:.2f}m, severidade {col['severity']}")
    else:
        print(f"\n✅ SEM COLISÕES")
    
    # Testar bateria do MICROBOT-001 (charging)
    robot_charging = data['robots'][0]  # MICROBOT-001
    
    print(f"\n\n🔋 BATERIA: {robot_charging['robot_id']}")
    battery_initial = robot_charging['state']['battery']
    print(f"   SOC inicial: {battery_initial['soc_percent']}%")
    print(f"   Tensão: {battery_initial['voltage_v']}V")
    print(f"   Corrente: {battery_initial['current_a']}A")
    print(f"   Temperatura: {battery_initial['temperature_c']}°C")
    print(f"   Charging: {battery_initial['charging']}")
    
    # Update bateria
    battery_result = engine.update_battery_physics(robot_charging, environment)
    
    print(f"\n⚡ POTÊNCIA:")
    print(f"   Consumo: {battery_result['power_consumption_w']:.1f} W")
    print(f"   Solar: {battery_result['power_solar_w']:.1f} W")
    print(f"   ➜ Líquida: {battery_result['power_net_w']:.1f} W ({'+' if battery_result['power_net_w'] >= 0 else ''})")
    print(f"   Energia (timestep): {battery_result['energy_change_wh']:.4f} Wh")
    
    print(f"\n🔋 BATERIA ATUALIZADA:")
    battery_new = battery_result['battery']
    soc_change = battery_new['soc_percent'] - battery_initial['soc_percent']
    print(f"   SOC: {battery_new['soc_percent']}% ({soc_change:+.4f}%)")
    print(f"   Tensão: {battery_new['voltage_v']}V")
    print(f"   Corrente: {battery_new['current_a']}A")
    print(f"   Temperatura: {battery_new['temperature_c']}°C")
    
    print(f"\n✅ Physics engine funcionando!")
    print(f"\nTotal de testes: 2")


if __name__ == '__main__':
    main()
