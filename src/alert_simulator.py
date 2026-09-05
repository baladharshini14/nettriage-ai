import os
import json
import random
from datetime import datetime, timezone

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE_PATH = os.path.join(DATA_DIR, "data", "alerts.json")
FALLBACK_FILE_PATH = os.path.join(DATA_DIR, "alerts.json")

SAMPLE_TEMPLATES = [
    {
        "device": "core-router-dal-01",
        "type": "LINK_DOWN",
        "severity": "CRITICAL",
        "messages": [
            "Secondary DWDM backup channel Loss of Signal detected on interface TenGigE0/0/0/2.",
            "Port TenGigE0/0/0/3 link flap count exceeded threshold (10 flaps in 30s)."
        ]
    },
    {
        "device": "core-router-dal-01",
        "type": "DEVICE_UNREACHABLE",
        "severity": "CRITICAL",
        "messages": [
            "Heartbeat timeout on secondary control processor core-router-dal-01.",
            "Out-of-Band management ping failed for core-router-dal-01."
        ]
    },
    {
        "device": "gNodeB-tower-austin-104",
        "type": "HIGH_LATENCY",
        "severity": "HIGH",
        "messages": [
            "5G NR air interface latency spiked to 210ms due to sector 2 radio interference.",
            "Backhaul microwave queue depth exceeded 95% capacity during peak cell traffic."
        ]
    },
    {
        "device": "bng-gateway-houston-02",
        "type": "AUTH_FAILURE",
        "severity": "HIGH",
        "messages": [
            "RADIUS AAA cluster sync failure. 180 PPPoE session renewal requests dropped.",
            "CHAP authentication handshake timeout for domain @broadband.net."
        ]
    },
    {
        "device": "5g-upf-central-01",
        "type": "DEVICE_UNREACHABLE",
        "severity": "CRITICAL",
        "messages": [
            "GTP-U tunnel heartbeat loss reported on N4 interface to 5G Control Plane.",
            "N3 interface packet dropped rate exceeded 25% threshold."
        ]
    },
    {
        "device": "edge-switch-dal-04",
        "type": "HIGH_LATENCY",
        "severity": "MEDIUM",
        "messages": [
            "VLAN 100 trunk link port congestion detected on GigabitEthernet1/0/12.",
            "Broadcast storm control suppression activated on edge port 18."
        ]
    },
    {
        "device": "pe-router-san-01",
        "type": "AUTH_FAILURE",
        "severity": "MEDIUM",
        "messages": [
            "BGP MD5 signature mismatch from peer 198.51.100.4.",
            "SSH console login failure limit reached for operator admin from 10.100.4.12."
        ]
    }
]

def simulate_new_alert():
    """
    Generate a realistic network alert, append to dataset on disk,
    and return the newly created alert object.
    """
    template = random.choice(SAMPLE_TEMPLATES)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    file_to_open = DATA_FILE_PATH if os.path.exists(DATA_FILE_PATH) else FALLBACK_FILE_PATH
    alerts = []
    if os.path.exists(file_to_open):
        with open(file_to_open, "r", encoding="utf-8") as f:
            try:
                alerts = json.load(f)
            except Exception:
                alerts = []

    next_num = len(alerts) + 1
    new_alert = {
        "id": f"ALT-2026-{next_num:03d}",
        "device": template["device"],
        "type": template["type"],
        "message": random.choice(template["messages"]),
        "severity": template["severity"],
        "timestamp": now_str
    }

    alerts.append(new_alert)

    # Save to data/alerts.json
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)
            
    # Also save to root alerts.json if exists
    if os.path.exists(FALLBACK_FILE_PATH):
        with open(FALLBACK_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)

    return new_alert
