"""
HTML Report Generation.

Generates HTML report from demo results using Jinja2.
"""

from jinja2 import Template
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import webbrowser

from .output import normalize_priority


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agro-Tech Ecosystem Demo Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #10b981;
        }
        
        h1 {
            color: #059669;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        h2 {
            color: #047857;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #10b981;
        }
        
        .priority-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.2em;
            margin: 10px 0;
        }
        
        .priority-critical {
            background: #dc2626;
            color: white;
        }
        
        .priority-high {
            background: #f59e0b;
            color: white;
        }
        
        .priority-medium {
            background: #10b981;
            color: white;
        }
        
        .priority-low {
            background: #6b7280;
            color: white;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: #f0fdf4;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            color: #047857;
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        th {
            background: #047857;
            color: white;
            font-weight: 600;
        }
        
        tr:hover {
            background: #f9fafb;
        }
        
        .next-steps {
            background: #fef3c7;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
        }
        
        .next-steps ol {
            margin-left: 20px;
        }
        
        .next-steps li {
            margin: 10px 0;
            font-size: 1.05em;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #666;
        }
        
        .detection-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            margin: 2px;
        }
        
        .badge-weed {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge-pest {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .badge-disease {
            background: #fed7aa;
            color: #9a3412;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 Agro-Tech Ecosystem Demo Report</h1>
            <p class="timestamp">Generated: {{ timestamp }}</p>
        </header>
        
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Field</div>
                    <div class="stat-value">{{ decision.field_id }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Priority</div>
                    <div class="stat-value">
                        <span class="priority-badge priority-{{ decision.priority.level }}">
                            {{ decision.priority.level.upper() }}
                        </span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Priority Score</div>
                    <div class="stat-value">{{ "%.1f"|format(decision.priority.score) }}/10</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total ROI/year</div>
                    <div class="stat-value">R$ {{ "{:,}".format(decision.estimated_roi_brl_year) }}</div>
                </div>
            </div>
            
            <p style="margin-top: 20px; font-size: 1.05em;">
                <strong>Reason:</strong> {{ decision.priority.reason }}
            </p>
        </div>
        
        {% if vision_data %}
        <div class="section">
            <h2>👁️ Vision Analysis</h2>
            <p><strong>Analysis ID:</strong> {{ vision_data.analysis_id }}</p>
            <p><strong>Crop Health:</strong> {{ vision_data.detections.crop_health.status.upper() }} 
               (NDVI: {{ "%.2f"|format(vision_data.detections.crop_health.ndvi) }})</p>
            
            <div style="margin-top: 15px;">
                {% if vision_data.detections.weeds %}
                    {% for weed in vision_data.detections.weeds %}
                        <span class="detection-badge badge-weed">
                            🌿 {{ weed.class }} ({{ weed.severity }}, {{ "%.0f"|format(weed.area_m2) }}m²)
                        </span>
                    {% endfor %}
                {% endif %}
                
                {% if vision_data.detections.pests %}
                    {% for pest in vision_data.detections.pests %}
                        <span class="detection-badge badge-pest">
                            🐛 {{ pest.class }} ({{ pest.severity }})
                        </span>
                    {% endfor %}
                {% endif %}
                
                {% if vision_data.detections.diseases %}
                    {% for disease in vision_data.detections.diseases %}
                        <span class="detection-badge badge-disease">
                            🦠 {{ disease.class }} ({{ disease.severity }})
                        </span>
                    {% endfor %}
                {% endif %}
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>🗺️ Zone Decisions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Zone</th>
                        <th>Priority</th>
                        <th>Action</th>
                        <th>ROI/year</th>
                    </tr>
                </thead>
                <tbody>
                    {% for zone in decision.zones %}
                    <tr>
                        <td><strong>{{ zone.zone_id }}</strong></td>
                        <td>
                            <span class="priority-badge priority-{{ zone.priority }}">
                                {{ zone.priority.upper() }}
                            </span>
                        </td>
                        <td>{{ zone.action.action.replace('_', ' ').title() }}</td>
                        <td><strong>R$ {{ "{:,}".format(zone.action.estimated_roi_brl_year) }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Next Steps</h2>
            <div class="next-steps">
                <ol>
                    {% for step in decision.next_steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
            </div>
        </div>
        
        <footer class="footer">
            <p>Agro-Tech Ecosystem Demo v1.0</p>
            <p>Multi-source Intelligence: Precision Agriculture + Computer Vision AI</p>
        </footer>
    </div>
</body>
</html>
"""


def generate_html_report(
    results: Dict[str, Any],
    output_dir: Path,
    open_browser: bool = True
) -> Path:
    """
    Generate HTML report from demo results.
    
    Args:
        results: Demo results dictionary
        output_dir: Directory to save report
        open_browser: Whether to open report in browser
    
    Returns:
        Path to generated report
    """
    # Extract data
    decision = results.get("steps", {}).get("decision", {}).get("data", {})
    vision_data = results.get("steps", {}).get("vision", {}).get("data", {})
    
    # Normalize priority field for template compatibility
    if "priority" in decision:
        priority_raw = decision["priority"]
        # Create normalized priority dict for easier Jinja2 access
        priority_normalized = normalize_priority(priority_raw)
        # Convert to dot-accessible object for Jinja2 template
        class PriorityObj:
            def __init__(self, data):
                self.level = data["level"]
                self.score = data["score"]
                self.reason = data["reason"]
        decision["priority"] = PriorityObj(priority_normalized)
    
    # Prepare template data
    template_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decision": decision,
        "vision_data": vision_data if vision_data else None
    }
    
    # Render template
    template = Template(HTML_TEMPLATE)
    html = template.render(**template_data)
    
    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"demo_report_{timestamp_str}.html"
    report_path.write_text(html, encoding="utf-8")
    
    # Open in browser
    if open_browser:
        webbrowser.open(str(report_path))
    
    return report_path
