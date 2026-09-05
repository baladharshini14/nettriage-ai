from datetime import datetime, timezone

def parse_timestamp(ts_str):
    """
    Parse ISO 8601 timestamp string to datetime object.
    """
    try:
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str)
    except Exception:
        return datetime.now(timezone.utc)

PRIORITY_RANK = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "UNKNOWN": 0
}

def determine_root_cause_and_priority(alert_types, alert_messages, alert_severities):
    """
    Apply rule-based heuristics to infer root cause, priority, and explanation.
    """
    types_set = set(alert_types)
    max_sev = "LOW"
    for s in alert_severities:
        if PRIORITY_RANK.get(s.upper(), 0) > PRIORITY_RANK.get(max_sev.upper(), 0):
            max_sev = s.upper()

    # Rule 1: LINK_DOWN + DEVICE_UNREACHABLE
    if "LINK_DOWN" in types_set and "DEVICE_UNREACHABLE" in types_set:
        return (
            "Connectivity / Physical Link Severed",
            "CRITICAL",
            "Physical transmission link state failure caused downstream loss of management signal and device unreachability."
        )
    
    # Rule 2: HIGH_LATENCY + LINK_DOWN
    if "HIGH_LATENCY" in types_set and "LINK_DOWN" in types_set:
        return (
            "Link Degradation & Traffic Congestion",
            "HIGH" if max_sev != "CRITICAL" else "CRITICAL",
            "Trunk interface link state failure caused packet rerouting, leading to severe latency and queue spikes."
        )
    
    # Rule 3: Repeated AUTH_FAILURE
    if alert_types.count("AUTH_FAILURE") >= 2:
        return (
            "Authentication Gateway Disturbance / Security Burst",
            "HIGH" if max_sev != "CRITICAL" else "CRITICAL",
            "Multiple consecutive authentication failure events detected on gateway within short time interval."
        )

    # Rule 4: Repeated DEVICE_UNREACHABLE
    if alert_types.count("DEVICE_UNREACHABLE") >= 2:
        return (
            "Persistent Node Power / Infrastructure Outage",
            "CRITICAL",
            "Repeated ping timeout & management heartbeat loss on network node."
        )
    
    # Single alert type fallbacks
    if "LINK_DOWN" in types_set:
        return (
            "Physical Layer / Fiber Link Loss",
            "CRITICAL" if max_sev == "CRITICAL" or any("CRITICAL" in m.upper() for m in alert_messages) else "HIGH",
            "Interface physical link loss detected on network interface."
        )
    if "DEVICE_UNREACHABLE" in types_set:
        return (
            "Node Power Failure / Management Loss",
            "CRITICAL",
            "Management heartbeat ping timeout or power alarm triggered on network device."
        )
    if "HIGH_LATENCY" in types_set:
        return (
            "Backhaul Congestion / Path Degradation",
            max_sev if PRIORITY_RANK.get(max_sev, 0) >= 3 else "HIGH",
            "Round-trip delay and packet loss threshold exceeded on transmission path."
        )
    if "AUTH_FAILURE" in types_set:
        return (
            "AAA/RADIUS Service Rejection",
            max_sev if PRIORITY_RANK.get(max_sev, 0) >= 2 else "MEDIUM",
            "Subscriber or administrator authentication request failure limit exceeded."
        )
        
    return ("Unclassified Network Event", max_sev, "Correlated event cluster requiring manual NOC review.")


def generate_recommended_actions(alert_types, priority, device):
    """
    Generate tailored troubleshooting actions, estimated impact, and next best action.
    """
    types_set = set(alert_types)
    actions = []

    if "LINK_DOWN" in types_set:
        actions.extend([
            "Check physical cable/fiber optic connection & transceivers on interface.",
            "Verify interface administrative & operational status via CLI (show interface).",
            "Measure optical RX/TX power levels using digital optical monitoring (DOM).",
            "Check neighboring/peer device link state and interface logs.",
            "Consider immediate traffic rerouting to bypass degraded fiber link."
        ])
    
    if "DEVICE_UNREACHABLE" in types_set:
        actions.extend([
            "Check device physical power feeds, PDU status, and site UPS backup.",
            "Inspect out-of-band (OOB) console & management interface reachability.",
            "Verify network connectivity from neighboring peer devices (ping/traceroute).",
            "Check site facilities & backhaul transport link health."
        ])

    if "HIGH_LATENCY" in types_set:
        actions.extend([
            "Inspect interface packet loss rates, frame errors, and buffer queue drops.",
            "Check real-time interface bandwidth utilization and throughput spikes.",
            "Audit active BGP/OSPF routing paths for sub-optimal routing hops.",
            "Apply QoS congestion management or reroute non-critical traffic."
        ])

    if "AUTH_FAILURE" in types_set:
        actions.extend([
            "Verify AAA/RADIUS/TACACS+ service daemon status and authentication logs.",
            "Check network connectivity between gateway node and AAA authentication server.",
            "Audit repeated unauthorized login attempts for potential brute-force activity.",
            "Verify subscriber authentication credentials & RADIUS shared secrets."
        ])

    # Deduplicate while preserving order
    seen = set()
    deduped_actions = []
    for act in actions:
        if act not in seen:
            seen.add(act)
            deduped_actions.append(act)

    if not deduped_actions:
        deduped_actions = [
            "Perform standard NOC diagnostic health check on device.",
            "Review system syslog and SNMP traps.",
            "Contact Tier-2 operations team for manual verification."
        ]

    # Next Best Action: single immediate recommendation
    if "LINK_DOWN" in types_set and "DEVICE_UNREACHABLE" in types_set:
        next_best = f"Dispatch field technician to inspect physical fiber trunk & local site power at {device} immediately."
    elif "LINK_DOWN" in types_set:
        next_best = f"Verify optical RX/TX power on {device} and trigger automated traffic rerouting."
    elif "DEVICE_UNREACHABLE" in types_set:
        next_best = f"Verify site power status & attempt Out-of-Band (OOB) console connection to {device}."
    elif "HIGH_LATENCY" in types_set:
        next_best = f"Check buffer congestion & re-route high-priority traffic on {device} path."
    elif "AUTH_FAILURE" in types_set:
        next_best = f"Check AAA RADIUS service daemon status & verify authentication server reachability for {device}."
    else:
        next_best = f"Perform immediate system diagnostic check on {device}."

    # Estimated Impact
    p = priority.upper()
    if p == "CRITICAL":
        estimated_impact = f"High Subscriber Impact: Complete service interruption or node outage on {device}. Risk of SLA breach & major downtime."
    elif p == "HIGH":
        estimated_impact = f"Moderate Subscriber Impact: Degraded quality of service, packet loss, or authentication delay on {device}."
    elif p == "MEDIUM":
        estimated_impact = f"Low-to-Moderate Impact: Port or redundant link disturbance on {device}. Primary traffic maintained via secondary path."
    else:
        estimated_impact = f"Minimal Impact: Low-severity administrative event on {device}. No immediate subscriber service disruption."

    return deduped_actions, estimated_impact, next_best


def correlate_alerts(alerts):
    """
    Group related network alerts into unified active incidents based on device co-location,
    alert type combinations, and temporal correlation (within 24-hour active window).
    Prevents duplicate incidents for the same ongoing device problem.
    """
    if not alerts:
        return []

    # Sort alerts chronologically
    sorted_alerts = sorted(alerts, key=lambda a: parse_timestamp(a.get("timestamp", "")))
    
    incidents = []
    incident_counter = 1
    
    for alert in sorted_alerts:
        alert_dev = alert.get("device", "unknown-device")
        alert_ts = parse_timestamp(alert.get("timestamp", ""))
        
        # Look for existing active incident on the same device
        matched_incident = None
        for inc in incidents:
            if inc["affected_device"] == alert_dev and inc["status"] == "ACTIVE":
                last_alert_ts = parse_timestamp(inc["related_alerts"][-1].get("timestamp", ""))
                time_diff_hours = abs((alert_ts - last_alert_ts).total_seconds()) / 3600.0
                
                # Active incident window: 24 hours
                if time_diff_hours <= 24.0:
                    matched_incident = inc
                    break
        
        if matched_incident:
            # Append alert to existing incident
            matched_incident["related_alerts"].append(alert)
            
            # Recalculate incident attributes with updated alert cluster
            alert_cluster = matched_incident["related_alerts"]
            alert_types = [a.get("type") for a in alert_cluster]
            alert_messages = [a.get("message", "") for a in alert_cluster]
            alert_severities = [a.get("severity", "LOW") for a in alert_cluster]
            
            root_cause, priority, explanation = determine_root_cause_and_priority(alert_types, alert_messages, alert_severities)
            actions, estimated_impact, next_best_action = generate_recommended_actions(alert_types, priority, alert_dev)
            
            matched_incident["probable_root_cause"] = root_cause
            matched_incident["priority"] = priority
            matched_incident["explanation"] = explanation
            matched_incident["recommended_actions"] = actions
            matched_incident["estimated_impact"] = estimated_impact
            matched_incident["next_best_action"] = next_best_action
        else:
            # Create a new active incident
            alert_cluster = [alert]
            alert_types = [alert.get("type")]
            alert_messages = [alert.get("message", "")]
            alert_severities = [alert.get("severity", "LOW")]
            
            root_cause, priority, explanation = determine_root_cause_and_priority(alert_types, alert_messages, alert_severities)
            actions, estimated_impact, next_best_action = generate_recommended_actions(alert_types, priority, alert_dev)
            
            new_inc = {
                "incident_id": f"INC-2026-{incident_counter:03d}",
                "affected_device": alert_dev,
                "status": "ACTIVE",
                "related_alerts": alert_cluster,
                "probable_root_cause": root_cause,
                "priority": priority,
                "explanation": explanation,
                "recommended_actions": actions,
                "estimated_impact": estimated_impact,
                "next_best_action": next_best_action
            }
            incidents.append(new_inc)
            incident_counter += 1

    return incidents
