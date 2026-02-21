#!/usr/bin/env python3
"""
Telemetry - Alert Manager Mock

Gerenciador de alertas e notificações
"""

import json
from pathlib import Path
from typing import Dict, List


class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.alert_count = 0
        self.history = []
    
    def manage_alerts(self, telemetry_data: Dict) -> Dict:
        """
        Gerencia alertas de telemetria
        
        Funções:
        - Coleta alertas de todos os robôs
        - Classifica por severidade
        - Gera novos alertas baseado em thresholds
        - Prioriza alertas para ação
        - Envia notificações
        
        Args:
            telemetry_data: Dados de telemetria
        
        Returns:
            Gerenciamento de alertas
        """
        self.alert_count += 1
        
        robots = telemetry_data.get('robots_telemetry', [])
        
        # Coleta alertas existentes
        existing_alerts = self._collect_existing_alerts(robots)
        
        # Gera novos alertas baseado em regras
        generated_alerts = self._generate_alerts_from_rules(robots)
        
        # Combina e remove duplicatas
        all_alerts = self._merge_alerts(existing_alerts, generated_alerts)
        
        # Prioriza alertas
        prioritized = self._prioritize_alerts(all_alerts)
        
        # Determina ações
        actions = self._determine_actions(prioritized)
        
        # Gera notificações
        notifications = self._generate_notifications(prioritized, actions)
        
        result = {
            'session_id': self.session_id,
            'timestamp': telemetry_data['timestamp'],
            'alert_count': self.alert_count,
            'total_alerts': len(all_alerts),
            'existing_alerts': len(existing_alerts),
            'generated_alerts': len(generated_alerts),
            'prioritized_alerts': prioritized,
            'actions': actions,
            'notifications': notifications
        }
        
        self.history.append(result)
        return result
    
    def _collect_existing_alerts(self, robots: List[Dict]) -> List[Dict]:
        """Coleta alertas existentes dos robôs"""
        alerts = []
        
        for robot in robots:
            robot_id = robot['robot_id']
            robot_alerts = robot.get('alerts', [])
            
            for alert in robot_alerts:
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': alert.get('alert_id'),
                    'severity': alert.get('severity', 'info'),
                    'type': alert.get('type'),
                    'message': alert.get('message'),
                    'timestamp': alert.get('timestamp'),
                    'acknowledged': alert.get('acknowledged', False),
                    'source': 'robot'
                })
        
        return alerts
    
    def _generate_alerts_from_rules(self, robots: List[Dict]) -> List[Dict]:
        """Gera alertas baseado em regras"""
        alerts = []
        alert_id_counter = 1000
        
        for robot in robots:
            robot_id = robot['robot_id']
            
            # Regra 1: Bateria crítica (<20%)
            battery = robot.get('battery', {})
            soc = battery.get('soc_percent', 100)
            if soc < 20:
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': f'ALERT-GEN-{alert_id_counter}',
                    'severity': 'critical',
                    'type': 'battery_critical',
                    'message': f'Bateria crítica em {soc}%',
                    'threshold': 20,
                    'current_value': soc,
                    'source': 'rule_engine'
                })
                alert_id_counter += 1
            
            # Regra 2: Bateria baixa (<50% e não carregando)
            elif soc < 50 and not battery.get('charging', False):
                # Verifica se já existe alerta
                existing = any(a.get('robot_id') == robot_id and 
                             a.get('type') == 'battery_low' 
                             for a in alerts)
                if not existing:
                    alerts.append({
                        'robot_id': robot_id,
                        'alert_id': f'ALERT-GEN-{alert_id_counter}',
                        'severity': 'warning',
                        'type': 'battery_low',
                        'message': f'Bateria baixa em {soc}%',
                        'threshold': 50,
                        'current_value': soc,
                        'source': 'rule_engine'
                    })
                    alert_id_counter += 1
            
            # Regra 3: Temperatura excessiva (>50°C)
            temp = battery.get('temperature_c', 25)
            if temp > 50:
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': f'ALERT-GEN-{alert_id_counter}',
                    'severity': 'warning',
                    'type': 'temperature_high',
                    'message': f'Temperatura bateria elevada: {temp}°C',
                    'threshold': 50,
                    'current_value': temp,
                    'source': 'rule_engine'
                })
                alert_id_counter += 1
            
            # Regra 4: CPU alto (>90%)
            health = robot.get('health', {})
            cpu = health.get('cpu_usage_percent', 0)
            if cpu > 90:
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': f'ALERT-GEN-{alert_id_counter}',
                    'severity': 'warning',
                    'type': 'cpu_high',
                    'message': f'CPU elevada: {cpu}%',
                    'threshold': 90,
                    'current_value': cpu,
                    'source': 'rule_engine'
                })
                alert_id_counter += 1
            
            # Regra 5: Memória alta (>85%)
            mem = health.get('memory_usage_percent', 0)
            if mem > 85:
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': f'ALERT-GEN-{alert_id_counter}',
                    'severity': 'info',
                    'type': 'memory_high',
                    'message': f'Memória elevada: {mem}%',
                    'threshold': 85,
                    'current_value': mem,
                    'source': 'rule_engine'
                })
                alert_id_counter += 1
            
            # Regra 6: Status não saudável
            overall_status = health.get('overall_status', 'unknown')
            if overall_status == 'warning':
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': f'ALERT-GEN-{alert_id_counter}',
                    'severity': 'warning',
                    'type': 'robot_degraded',
                    'message': f'Robô em estado degradado',
                    'source': 'rule_engine'
                })
                alert_id_counter += 1
            elif overall_status == 'critical':
                alerts.append({
                    'robot_id': robot_id,
                    'alert_id': f'ALERT-GEN-{alert_id_counter}',
                    'severity': 'critical',
                    'type': 'robot_critical',
                    'message': f'Robô em estado crítico',
                    'source': 'rule_engine'
                })
                alert_id_counter += 1
        
        return alerts
    
    def _merge_alerts(self, existing: List[Dict], generated: List[Dict]) -> List[Dict]:
        """Combina alertas e remove duplicatas"""
        # Usa um set para rastrear (robot_id, type) para evitar duplicatas
        seen = set()
        merged = []
        
        # Prioriza alertas existentes (já foram reportados)
        for alert in existing:
            key = (alert['robot_id'], alert['type'])
            if key not in seen:
                merged.append(alert)
                seen.add(key)
        
        # Adiciona alertas gerados que não são duplicatas
        for alert in generated:
            key = (alert['robot_id'], alert['type'])
            if key not in seen:
                merged.append(alert)
                seen.add(key)
        
        return merged
    
    def _prioritize_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Prioriza alertas por severidade e tipo"""
        # Define peso de prioridade
        severity_weight = {
            'critical': 100,
            'warning': 50,
            'info': 10
        }
        
        # Define peso por tipo
        type_weight = {
            'battery_critical': 20,
            'robot_critical': 18,
            'safety_violation': 15,
            'temperature_high': 12,
            'battery_low': 10,
            'robot_degraded': 8,
            'cpu_high': 5,
            'memory_high': 3
        }
        
        # Calcula score de prioridade
        for alert in alerts:
            severity_score = severity_weight.get(alert['severity'], 0)
            type_score = type_weight.get(alert['type'], 0)
            ack_penalty = -50 if alert.get('acknowledged', False) else 0
            
            alert['priority_score'] = severity_score + type_score + ack_penalty
        
        # Ordena por priority_score (descending)
        alerts.sort(key=lambda a: a['priority_score'], reverse=True)
        
        # Adiciona rank
        for i, alert in enumerate(alerts, 1):
            alert['priority_rank'] = i
        
        return alerts
    
    def _determine_actions(self, alerts: List[Dict]) -> List[Dict]:
        """Determina ações baseado em alertas"""
        actions = []
        
        for alert in alerts:
            # Só processa alertas não reconhecidos e críticos/warning
            if alert.get('acknowledged', False):
                continue
            
            severity = alert['severity']
            alert_type = alert['type']
            robot_id = alert['robot_id']
            
            # Ações por tipo de alerta
            if alert_type == 'battery_critical':
                actions.append({
                    'action_type': 'emergency_charge',
                    'robot_id': robot_id,
                    'priority': 'high',
                    'description': f'Enviar {robot_id} para estação de recarga imediatamente',
                    'related_alert': alert['alert_id']
                })
                actions.append({
                    'action_type': 'suspend_mission',
                    'robot_id': robot_id,
                    'priority': 'high',
                    'description': f'Suspender missão de {robot_id}',
                    'related_alert': alert['alert_id']
                })
            
            elif alert_type == 'battery_low':
                actions.append({
                    'action_type': 'schedule_charge',
                    'robot_id': robot_id,
                    'priority': 'medium',
                    'description': f'Agendar recarga de {robot_id} após conclusão da missão',
                    'related_alert': alert['alert_id']
                })
            
            elif alert_type == 'temperature_high':
                actions.append({
                    'action_type': 'reduce_load',
                    'robot_id': robot_id,
                    'priority': 'medium',
                    'description': f'Reduzir carga de trabalho de {robot_id} para resfriar',
                    'related_alert': alert['alert_id']
                })
            
            elif alert_type == 'robot_critical':
                actions.append({
                    'action_type': 'emergency_stop',
                    'robot_id': robot_id,
                    'priority': 'critical',
                    'description': f'Parar {robot_id} imediatamente para inspeção',
                    'related_alert': alert['alert_id']
                })
                actions.append({
                    'action_type': 'dispatch_maintenance',
                    'robot_id': robot_id,
                    'priority': 'high',
                    'description': f'Despachar equipe de manutenção para {robot_id}',
                    'related_alert': alert['alert_id']
                })
        
        return actions
    
    def _generate_notifications(self, alerts: List[Dict], actions: List[Dict]) -> List[Dict]:
        """Gera notificações"""
        notifications = []
        
        # Notificações de alertas críticos
        critical_alerts = [a for a in alerts if a['severity'] == 'critical' and not a.get('acknowledged', False)]
        if critical_alerts:
            notifications.append({
                'notification_id': 'NOTIF-001',
                'type': 'critical_alert',
                'channel': ['sms', 'email', 'push'],
                'recipients': ['operator', 'supervisor', 'maintenance_team'],
                'message': f'{len(critical_alerts)} alerta(s) crítico(s) requer atenção imediata',
                'details': [a['message'] for a in critical_alerts[:3]]
            })
        
        # Notificações de ações high priority
        high_priority_actions = [a for a in actions if a['priority'] in ['critical', 'high']]
        if high_priority_actions:
            notifications.append({
                'notification_id': 'NOTIF-002',
                'type': 'action_required',
                'channel': ['push', 'email'],
                'recipients': ['operator', 'supervisor'],
                'message': f'{len(high_priority_actions)} ação(ões) de prioridade alta pendente(s)',
                'details': [a['description'] for a in high_priority_actions[:3]]
            })
        
        # Resumo diário
        notifications.append({
            'notification_id': 'NOTIF-003',
            'type': 'daily_summary',
            'channel': ['email'],
            'recipients': ['manager', 'supervisor'],
            'message': f'Resumo de telemetria: {len(alerts)} alertas ativos',
            'details': {
                'critical': len([a for a in alerts if a['severity'] == 'critical']),
                'warning': len([a for a in alerts if a['severity'] == 'warning']),
                'info': len([a for a in alerts if a['severity'] == 'info'])
            }
        })
        
        return notifications
    
    def display_alert_report(self, result: Dict):
        """Exibe relatório de alertas"""
        print("\n" + "="*70)
        print("🚨 GERENCIAMENTO DE ALERTAS")
        print("="*70)
        
        alerts = result['prioritized_alerts']
        actions = result['actions']
        notifs = result['notifications']
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total de alertas: {result['total_alerts']}")
        print(f"   Existentes: {result['existing_alerts']}")
        print(f"   Gerados: {result['generated_alerts']}")
        
        # Por severidade
        by_severity = {'critical': 0, 'warning': 0, 'info': 0}
        for alert in alerts:
            by_severity[alert['severity']] += 1
        
        print(f"\n📈 POR SEVERIDADE:")
        print(f"   🔴 Critical: {by_severity['critical']}")
        print(f"   ⚠️  Warning: {by_severity['warning']}")
        print(f"   ℹ️  Info: {by_severity['info']}")
        
        print(f"\n🚨 ALERTAS PRIORITÁRIOS: (Top 5)")
        for alert in alerts[:5]:
            icon = "🔴" if alert['severity'] == 'critical' else "⚠️" if alert['severity'] == 'warning' else "ℹ️"
            ack = " [ACK]" if alert.get('acknowledged', False) else ""
            print(f"\n   {icon} #{alert.get('priority_rank', '?')} {alert['robot_id']} - {alert['type'].upper()}{ack}")
            print(f"      Mensagem: {alert['message']}")
            print(f"      Score: {alert.get('priority_score', 0)}")
            if 'current_value' in alert:
                print(f"      Valor: {alert['current_value']} (threshold {alert.get('threshold', 'N/A')})")
        
        print(f"\n⚡ AÇÕES RECOMENDADAS: {len(actions)}")
        for action in actions[:3]:
            priority_icon = "❗" if action['priority'] == 'critical' else "⚠️" if action['priority'] == 'high' else "📌"
            print(f"\n   {priority_icon} {action['action_type'].upper().replace('_', ' ')}")
            print(f"      Robô: {action['robot_id']}")
            print(f"      Prioridade: {action['priority'].upper()}")
            print(f"      Descrição: {action['description']}")
        
        print(f"\n📧 NOTIFICAÇÕES: {len(notifs)}")
        for notif in notifs:
            print(f"\n   {notif['notification_id']} - {notif['type'].upper().replace('_', ' ')}")
            print(f"      Canais: {', '.join(notif['channel'])}")
            print(f"      Destinatários: {', '.join(notif['recipients'])}")
            print(f"      Mensagem: {notif['message']}")


if __name__ == "__main__":
    print("🚨 Telemetry - Alert Manager Mock\n")
    print("="*70)
    
    # Inicializa gerenciador
    manager = AlertManager("TELEM-SESSION-20260220-154500")
    
    # Carrega dados
    data_file = Path(__file__).parent / "example_telemetry_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        telemetry_data = json.load(f)
    
    print(f"\n🚨 Session: {telemetry_data['telemetry_session_id']}")
    print(f"   Robôs: {len(telemetry_data['robots_telemetry'])}")
    
    # Gerencia alertas
    result = manager.manage_alerts(telemetry_data)
    
    # Exibe relatório
    manager.display_alert_report(result)
    
    print("\n" + "="*70)
    print("✅ GERENCIAMENTO COMPLETO")
    print("="*70)
    print(f"\n💡 Total de operações: {manager.alert_count}\n")
