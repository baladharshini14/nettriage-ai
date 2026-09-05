import os
import json

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(DATA_DIR, "data", "alerts.json")
FALLBACK_FILE_PATH = os.path.join(DATA_DIR, "alerts.json")

def load_alerts():
    """
    Load network alert data from JSON storage.
    """
    file_to_open = DATA_FILE_PATH if os.path.exists(DATA_FILE_PATH) else FALLBACK_FILE_PATH
    if not os.path.exists(file_to_open):
        return []
    
    with open(file_to_open, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_alerts():
    """
    Return all loaded alerts.
    """
    return load_alerts()

def get_alert_by_id(alert_id):
    """
    Retrieve a single alert by its ID.
    """
    alerts = load_alerts()
    for alert in alerts:
        if alert.get("id") == alert_id:
            return alert
    return None

def get_alerts_summary():
    """
    Generate summary statistics for loaded alerts.
    """
    alerts = load_alerts()
    summary = {
        "total_alerts": len(alerts),
        "by_severity": {},
        "by_type": {}
    }
    
    for alert in alerts:
        sev = alert.get("severity", "UNKNOWN")
        alert_type = alert.get("type", "UNKNOWN")
        
        summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
        summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1
        
    return summary
