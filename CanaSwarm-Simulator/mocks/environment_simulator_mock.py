#!/usr/bin/env python3
"""
Environment Simulator Mock - CanaSwarm Simulator

Simula ambiente dinâmico: terreno, plantação, clima, sol, obstáculos.

Author: CanaSwarm Team
Date: 2026-02-20
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


class EnvironmentSimulator:
    """Simulador de ambiente para robôs agrícolas"""
    
    def __init__(self, environment_data: Dict[str, Any], config: Dict[str, Any]):
        """
        Inicializa environment simulator
        
        Args:
            environment_data: Dados iniciais do ambiente
            config: Configuração da simulação
        """
        self.environment = environment_data.copy()
        self.config = config
        self.timestep = config.get('timestep_seconds', 0.1)
        self.current_time = datetime.fromisoformat(environment_data.get('solar', {}).get('date', '2026-02-20') + 'T00:00:00')
        
    def update_environment(self, elapsed_seconds: float) -> Dict[str, Any]:
        """
        Atualiza estado do ambiente
        
        Args:
            elapsed_seconds: Tempo decorrido desde início da simulação
            
        Returns:
            Estado atualizado do ambiente
        """
        self.current_time = self.current_time + timedelta(seconds=elapsed_seconds)
        
        # Atualizar componentes do ambiente
        if self.config.get('weather_simulation', True):
            self._update_weather(elapsed_seconds)
        
        if self.config.get('solar_simulation', True):
            self._update_solar(elapsed_seconds)
        
        self._update_plantation(elapsed_seconds)
        
        return self.environment.copy()
    
    def _update_weather(self, elapsed_seconds: float):
        """Atualiza condições climáticas"""
        weather = self.environment['weather']
        
        # Temperatura varia com hora do dia (modelo simplificado sinusoidal)
        hour = self.current_time.hour + self.current_time.minute / 60
        temp_base = 25  # Temp média
        temp_amplitude = 8  # Variação diária
        temp_peak_hour = 14  # Pico às 14h
        
        temperature_c = temp_base + temp_amplitude * math.sin(2 * math.pi * (hour - 6) / 24)
        temperature_c += random.uniform(-0.5, 0.5)  # Ruído
        
        # Umidade inversamente proporcional a temperatura
        humidity_base = 70
        humidity_percent = humidity_base - (temperature_c - temp_base) * 2
        humidity_percent = max(30, min(95, humidity_percent))
        
        # Vento varia aleatoriamente
        wind_change = random.uniform(-0.2, 0.2)
        wind_speed_ms = weather['wind_speed_ms'] + wind_change
        wind_speed_ms = max(0, min(15, wind_speed_ms))
        
        # Direção do vento muda lentamente
        wind_direction_change = random.uniform(-2, 2)
        wind_direction_deg = (weather['wind_direction_deg'] + wind_direction_change) % 360
        
        # Precipitação (modelo simples: probabilidade baseada em cloud cover)
        cloud_cover = weather['cloud_cover_percent']
        if random.random() < (cloud_cover / 100) * 0.01:  # 1% chance por timestep se 100% nuvens
            precipitation_mm_per_hour = random.uniform(0, 10)
            cloud_cover = min(100, cloud_cover + 5)
        else:
            precipitation_mm_per_hour = max(0, weather['precipitation_mm_per_hour'] - 0.1)
            cloud_cover = max(0, cloud_cover + random.uniform(-1, 0.5))
        
        # Condições meteorológicas
        if precipitation_mm_per_hour > 5:
            conditions = "rainy"
        elif precipitation_mm_per_hour > 0.5:
            conditions = "drizzle"
        elif cloud_cover > 80:
            conditions = "cloudy"
        elif cloud_cover > 40:
            conditions = "partly_cloudy"
        else:
            conditions = "sunny"
        
        weather.update({
            'temperature_c': round(temperature_c, 1),
            'humidity_percent': round(humidity_percent, 1),
            'wind_speed_ms': round(wind_speed_ms, 1),
            'wind_direction_deg': round(wind_direction_deg, 1),
            'precipitation_mm_per_hour': round(precipitation_mm_per_hour, 1),
            'cloud_cover_percent': round(cloud_cover, 1),
            'conditions': conditions
        })
    
    def _update_solar(self, elapsed_seconds: float):
        """Atualiza posição do sol e irradiância"""
        solar = self.environment['solar']
        
        # Hora atual
        hour = self.current_time.hour + self.current_time.minute / 60 + self.current_time.second / 3600
        
        # Calcular elevação do sol (modelo simplificado)
        latitude = solar['latitude']
        day_of_year = self.current_time.timetuple().tm_yday
        
        # Declinação solar (δ)
        declination = 23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365)
        
        # Ângulo horário (ω)
        hour_angle = 15 * (hour - 12)  # 15° por hora, 0° ao meio-dia
        
        # Elevação solar (α)
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        hour_rad = math.radians(hour_angle)
        
        sin_elevation = (math.sin(lat_rad) * math.sin(dec_rad) + 
                        math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad))
        sun_elevation_deg = math.degrees(math.asin(max(-1, min(1, sin_elevation))))
        
        # Azimute solar (A)
        cos_azimuth = ((math.sin(dec_rad) - math.sin(lat_rad) * math.sin(math.radians(sun_elevation_deg))) /
                      (math.cos(lat_rad) * math.cos(math.radians(sun_elevation_deg))))
        cos_azimuth = max(-1, min(1, cos_azimuth))
        sun_azimuth_deg = math.degrees(math.acos(cos_azimuth))
        
        if hour > 12:  # Afternoon
            sun_azimuth_deg = 360 - sun_azimuth_deg
        
        # Irradiância (baseada em elevação solar e cloud cover)
        if sun_elevation_deg > 0:
            # Irradiância máxima ao meio-dia: ~1000 W/m²
            max_irradiance = 1000
            irradiance_clear_sky = max_irradiance * math.sin(math.radians(sun_elevation_deg))
            
            # Redução por nuvens
            cloud_cover = self.environment['weather']['cloud_cover_percent']
            cloud_factor = 1 - (cloud_cover / 100) * 0.75  # Até 75% redução
            
            irradiance_w_per_m2 = irradiance_clear_sky * cloud_factor
        else:
            irradiance_w_per_m2 = 0  # Noite
        
        solar.update({
            'time': self.current_time.strftime('%H:%M:%S'),
            'sun_elevation_deg': round(sun_elevation_deg, 1),
            'sun_azimuth_deg': round(sun_azimuth_deg, 1),
            'irradiance_w_per_m2': round(irradiance_w_per_m2, 0)
        })
    
    def _update_plantation(self, elapsed_seconds: float):
        """Atualiza estado da plantação"""
        plantation = self.environment['plantation']
        
        # Crescimento das plantas (muito lento, quase imperceptível em simulação curta)
        # Taxa de crescimento: ~0.5% por dia em condições ideais
        growth_rate_per_second = 0.5 / (24 * 3600)  # % por segundo
        
        # Fatores que afetam crescimento
        weather = self.environment['weather']
        temp_factor = 1.0 if 20 <= weather['temperature_c'] <= 35 else 0.5
        water_factor = 1.0 if weather['precipitation_mm_per_hour'] > 0 or weather['humidity_percent'] > 60 else 0.7
        solar = self.environment['solar']
        light_factor = min(1.0, solar['irradiance_w_per_m2'] / 500)
        
        growth_factor = temp_factor * water_factor * light_factor
        
        maturity_change = growth_rate_per_second * growth_factor * elapsed_seconds
        plantation['maturity']['avg_percent'] += maturity_change
        plantation['maturity']['avg_percent'] = min(100, plantation['maturity']['avg_percent'])
        
        # Altura aumenta com maturidade (até ~4m)
        max_height = 4.0
        plantation['height_avg_m'] = (plantation['maturity']['avg_percent'] / 100) * max_height
        
        # Biomassa aumenta (até ~100 ton/ha)
        max_biomass = 100000
        plantation['biomass_kg_per_ha'] = (plantation['maturity']['avg_percent'] / 100) * max_biomass
    
    def get_terrain_height(self, lat: float, lon: float) -> float:
        """
        Obtém altura do terreno em uma posição GPS
        
        Args:
            lat, lon: Coordenadas GPS
            
        Returns:
            Altura em metros
        """
        terrain = self.environment['terrain']
        bounds = terrain['bounds']
        elevation = terrain['elevation']
        
        # Normalizar posição dentro dos bounds (0-1)
        lat_norm = (lat - bounds['lat_min']) / (bounds['lat_max'] - bounds['lat_min'])
        lon_norm = (lon - bounds['lon_min']) / (bounds['lon_max'] - bounds['lon_min'])
        
        # Modelo de elevação simplificado (sinusoidal para variação suave)
        height_variation = (elevation['max_m'] - elevation['min_m']) / 2
        height_avg = (elevation['max_m'] + elevation['min_m']) / 2
        
        # Ondulações no terreno
        height = height_avg + height_variation * (
            math.sin(lat_norm * 2 * math.pi) * 0.5 +
            math.cos(lon_norm * 2 * math.pi) * 0.5
        )
        
        return height
    
    def get_plant_density(self, lat: float, lon: float) -> float:
        """
        Obtém densidade de plantas em uma posição
        
        Args:
            lat, lon: Coordenadas GPS
            
        Returns:
            Densidade (0-1, 1 = densidade máxima)
        """
        plantation = self.environment['plantation']
        
        # Verificar se está dentro da área plantada
        terrain = self.environment['terrain']
        bounds = terrain['bounds']
        
        if not (bounds['lat_min'] <= lat <= bounds['lat_max'] and
                bounds['lon_min'] <= lon <= bounds['lon_max']):
            return 0.0
        
        # Densidade varia com posição (áreas com falhas na plantação)
        lat_norm = (lat - bounds['lat_min']) / (bounds['lat_max'] - bounds['lat_min'])
        lon_norm = (lon - bounds['lon_min']) / (bounds['lon_max'] - bounds['lon_min'])
        
        # Densidade base alta (0.85-1.0) com pequenas variações
        density_base = 0.92
        density_variation = 0.08 * (math.sin(lat_norm * 10) * math.cos(lon_norm * 10))
        density = density_base + density_variation
        
        return max(0, min(1, density))
    
    def check_obstacle_at(self, lat: float, lon: float, radius_m: float = 1.0) -> List[Dict]:
        """
        Verifica obstáculos em uma posição
        
        Args:
            lat, lon: Coordenadas GPS
            radius_m: Raio de verificação
            
        Returns:
            Lista de obstáculos encontrados
        """
        obstacles_found = []
        obstacles = self.environment['terrain'].get('obstacles', [])
        
        for obstacle in obstacles:
            obs_lat = obstacle['position']['lat']
            obs_lon = obstacle['position']['lon']
            obs_radius = obstacle['radius_m']
            
            # Distância (Haversine)
            distance = self._haversine_distance(lat, lon, obs_lat, obs_lon)
            
            if distance < (radius_m + obs_radius):
                obstacles_found.append({
                    'type': obstacle['type'],
                    'distance_m': distance,
                    'position': obstacle['position']
                })
        
        return obstacles_found
    
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
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Retorna resumo do estado do ambiente"""
        weather = self.environment['weather']
        solar = self.environment['solar']
        plantation = self.environment['plantation']
        
        return {
            'timestamp': self.current_time.isoformat(),
            'weather': {
                'conditions': weather['conditions'],
                'temperature_c': weather['temperature_c'],
                'wind_speed_ms': weather['wind_speed_ms'],
                'precipitation': weather['precipitation_mm_per_hour']
            },
            'solar': {
                'elevation_deg': solar['sun_elevation_deg'],
                'irradiance_w_per_m2': solar['irradiance_w_per_m2'],
                'daytime': solar['sun_elevation_deg'] > 0
            },
            'plantation': {
                'maturity_percent': round(plantation['maturity']['avg_percent'], 1),
                'height_m': round(plantation['height_avg_m'], 2),
                'biomass_kg_per_ha': round(plantation['biomass_kg_per_ha'], 0)
            }
        }


def main():
    """Testa environment simulator com dados do exemplo"""
    print("🌍 Simulator - Environment Simulator Mock")
    print("=" * 70)
    
    # Carregar dados
    with open('example_simulation_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Inicializar simulator
    simulator = EnvironmentSimulator(data['environment'], data['config'])
    
    print(f"\n🌤️  AMBIENTE INICIAL:")
    summary = simulator.get_environment_summary()
    print(f"   Timestamp: {summary['timestamp']}")
    print(f"   Condições: {summary['weather']['conditions']}")
    print(f"   Temperatura: {summary['weather']['temperature_c']}°C")
    print(f"   Vento: {summary['weather']['wind_speed_ms']} m/s")
    print(f"   Elevação solar: {summary['solar']['elevation_deg']}°")
    print(f"   Irradiância: {summary['solar']['irradiance_w_per_m2']} W/m²")
    print(f"   Maturidade: {summary['plantation']['maturity_percent']}%")
    
    # Simular 10 minutos (600 segundos)
    print(f"\n⏱️  SIMULANDO 10 MINUTOS...")
    
    elapsed = 0
    timestep = data['config']['timestep_seconds']
    duration = 600  # 10 minutos
    
    # Amostrar a cada 2 minutos
    samples = []
    sample_interval = 120  # 2 minutos
    next_sample = sample_interval
    
    while elapsed < duration:
        simulator.update_environment(timestep)
        elapsed += timestep
        
        if elapsed >= next_sample:
            samples.append({
                'time': elapsed,
                'summary': simulator.get_environment_summary()
            })
            next_sample += sample_interval
    
    print(f"\n📊 EVOLUÇÃO DO AMBIENTE (amostras a cada 2 min):")
    print(f"{'Tempo':<10} {'Temp':<8} {'Vento':<10} {'Sol°':<10} {'Irrad':<12} {'Matur'}")
    print("-" * 70)
    
    for sample in samples:
        t = sample['time']
        s = sample['summary']
        print(f"{t:>6.0f}s   "
              f"{s['weather']['temperature_c']:>5.1f}°C  "
              f"{s['weather']['wind_speed_ms']:>5.1f} m/s  "
              f"{s['solar']['elevation_deg']:>7.1f}°  "
              f"{s['solar']['irradiance_w_per_m2']:>7.0f} W/m²  "
              f"{s['plantation']['maturity_percent']:>5.1f}%")
    
    # Testar queries de posição
    print(f"\n\n📍 QUERIES DE POSIÇÃO:")
    
    test_positions = [
        {'lat': -22.7150, 'lon': -47.6500, 'name': 'Centro'},
        {'lat': -22.7130, 'lon': -47.6480, 'name': 'Próximo a árvore'},
        {'lat': -22.7100, 'lon': -47.6450, 'name': 'Borda'}
    ]
    
    for pos in test_positions:
        lat, lon = pos['lat'], pos['lon']
        height = simulator.get_terrain_height(lat, lon)
        density = simulator.get_plant_density(lat, lon)
        obstacles = simulator.check_obstacle_at(lat, lon, radius_m=2.0)
        
        print(f"\n   📌 {pos['name']} ({lat:.4f}, {lon:.4f}):")
        print(f"      Elevação: {height:.1f} m")
        print(f"      Densidade plantas: {density:.2f} ({density*100:.0f}%)")
        if obstacles:
            print(f"      ⚠️  Obstáculos: {len(obstacles)}")
            for obs in obstacles:
                print(f"         - {obs['type']} a {obs['distance_m']:.2f}m")
        else:
            print(f"      ✅ Sem obstáculos")
    
    print(f"\n✅ Environment simulator funcionando!")
    print(f"\nTotal de timesteps: {int(duration / timestep)}")


if __name__ == '__main__':
    main()
