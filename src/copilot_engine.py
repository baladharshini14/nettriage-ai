import re
from src.alert_loader import get_all_alerts
from src.incident_correlator import correlate_alerts

def answer_copilot_query(query_text):
    """
    Process NOC operator queries using incident/alert context & intelligent intent matching.
    Returns structured answer object:
    {
      "answer": "...",
      "referenced_incident": "INC-2026-001",
      "next_action": "...",
      "source": "NetTriage AI Engine"
    }
    """
    if not query_text or not str(query_text).strip():
        return {
            "answer": "Please ask a question about active network incidents or alerts.",
            "referenced_incident": None,
            "next_action": None
        }

    q = str(query_text).strip().lower()
    alerts = get_all_alerts()
    incidents = correlate_alerts(alerts)

    # Search for mentioned incident ID (e.g. INC-2026-001, inc-001, inc 001)
    inc_match = re.search(r"inc[-_\s]*(?:2026[-_\s]*)?(\d{1,3})", q)
    target_inc = None
    if inc_match:
        inc_num_str = f"{int(inc_match.group(1)):03d}"
        for inc in incidents:
            if inc.get("incident_id", "").endswith(f"-{inc_num_str}"):
                target_inc = inc
                break

    # Search for mentioned device name
    target_device = None
    if not target_inc:
        for inc in incidents:
            dev = inc.get("affected_device", "").lower()
            if dev and dev in q:
                target_device = dev
                target_inc = inc
                break

    # Intent 1: Top / Most Critical Incident
    if any(k in q for k in ["most critical", "highest priority", "most severe", "top incident"]):
        critical_incs = [i for i in incidents if i.get("priority") == "CRITICAL"]
        top_inc = critical_incs[0] if critical_incs else (incidents[0] if incidents else None)
        if top_inc:
            ans = f"The most critical incident is **{top_inc['incident_id']}** affecting **{top_inc['affected_device']}**.\n\n" \
                  f"• **Root Cause**: {top_inc['probable_root_cause']}\n" \
                  f"• **Impact**: {top_inc['estimated_impact']}\n" \
                  f"• **Related Alerts**: {len(top_inc['related_alerts'])} active alerts."
            return {
                "answer": ans,
                "referenced_incident": top_inc["incident_id"],
                "next_action": top_inc["next_best_action"]
            }

    # Intent 2: Show all critical incidents
    if "critical" in q and any(k in q for k in ["all", "show", "list", "how many"]):
        critical_incs = [i for i in incidents if i.get("priority") == "CRITICAL"]
        if critical_incs:
            inc_list = "\n".join([f"• **{i['incident_id']}** ({i['affected_device']}): {i['probable_root_cause']}" for i in critical_incs])
            ans = f"There are currently **{len(critical_incs)} CRITICAL incidents** active:\n\n{inc_list}"
            return {
                "answer": ans,
                "referenced_incident": critical_incs[0]["incident_id"],
                "next_action": critical_incs[0]["next_best_action"]
            }
        else:
            return {
                "answer": "There are currently no CRITICAL priority incidents active in the network stream.",
                "referenced_incident": None,
                "next_action": None
            }

    # Intent 3: "Why is INC-XXXX critical?" / "Why critical"
    if target_inc and any(k in q for k in ["why", "reason", "cause"]):
        alert_types_str = ", ".join([a['type'] for a in target_inc['related_alerts']])
        ans = f"Incident **{target_inc['incident_id']}** ({target_inc['affected_device']}) is classified as **{target_inc['priority']}** priority because:\n\n" \
              f"• **Diagnosis**: {target_inc['explanation']}\n" \
              f"• **Probable Root Cause**: {target_inc['probable_root_cause']}\n" \
              f"• **Alert Pattern**: [{alert_types_str}]"
        return {
            "answer": ans,
            "referenced_incident": target_inc["incident_id"],
            "next_action": target_inc["next_best_action"]
        }

    # Intent 4: "What should I do first for INC-XXXX?" / "What do I do" / "Next action"
    if target_inc and any(k in q for k in ["first", "what should i do", "action", "how to fix", "next step", "troubleshoot"]):
        actions_list = "\n".join([f"  {idx+1}. {act}" for idx, act in enumerate(target_inc['recommended_actions'][:4])])
        ans = f"For incident **{target_inc['incident_id']}** ({target_inc['affected_device']}), here is the recommended procedure:\n\n" \
              f"👉 **Immediate Action**: {target_inc['next_best_action']}\n\n" \
              f"**Follow-up Checklist**:\n{actions_list}"
        return {
            "answer": ans,
            "referenced_incident": target_inc["incident_id"],
            "next_action": target_inc["next_best_action"]
        }

    # Intent 5: "Which alerts are related to core-router-dal-01 / INC-XXXX?"
    if any(k in q for k in ["alerts related", "alerts on", "show alerts"]):
        if target_inc:
            alert_items = [f"• `{a['id']}` - **{a['type']}** ({a['severity']}): {a['message']}" for a in target_inc['related_alerts']]
            ans = f"Incident **{target_inc['incident_id']}** on device **{target_inc['affected_device']}** has **{len(alert_items)} related alerts**:\n\n" + "\n".join(alert_items)
            return {
                "answer": ans,
                "referenced_incident": target_inc["incident_id"],
                "next_action": target_inc["next_best_action"]
            }

    # Intent 6: "What is the estimated impact?"
    if target_inc and any(k in q for k in ["impact", "affected subscribers", "sla"]):
        ans = f"Estimated Impact for **{target_inc['incident_id']}** ({target_inc['affected_device']}):\n\n" \
              f"⚠️ **Impact Summary**: {target_inc['estimated_impact']}\n" \
              f"• **Priority Level**: {target_inc['priority']}"
        return {
            "answer": ans,
            "referenced_incident": target_inc["incident_id"],
            "next_action": target_inc["next_best_action"]
        }

    # Intent 7: "What is the probable root cause?"
    if target_inc and any(k in q for k in ["root cause", "probable cause"]):
        ans = f"The probable root cause for **{target_inc['incident_id']}** ({target_inc['affected_device']}) is:\n\n" \
              f"🔍 **Root Cause**: {target_inc['probable_root_cause']}\n" \
              f"• **Explanation**: {target_inc['explanation']}"
        return {
            "answer": ans,
            "referenced_incident": target_inc["incident_id"],
            "next_action": target_inc["next_best_action"]
        }

    # Intent 8: Mention of a specific Incident ID without specific intent
    if target_inc:
        ans = f"Incident Details for **{target_inc['incident_id']}** ({target_inc['affected_device']}):\n\n" \
              f"• **Priority**: {target_inc['priority']}\n" \
              f"• **Root Cause**: {target_inc['probable_root_cause']}\n" \
              f"• **Impact**: {target_inc['estimated_impact']}\n" \
              f"• **Diagnosis**: {target_inc['explanation']}"
        return {
            "answer": ans,
            "referenced_incident": target_inc["incident_id"],
            "next_action": target_inc["next_best_action"]
        }

    # Keyword Search across all incidents & alerts
    matching_incidents = []
    for inc in incidents:
        searchable_text = f"{inc['incident_id']} {inc['affected_device']} {inc['probable_root_cause']} {inc['explanation']} {inc['estimated_impact']}".lower()
        if any(term in searchable_text for term in q.split() if len(term) > 3):
            matching_incidents.append(inc)

    if matching_incidents:
        top_match = matching_incidents[0]
        ans = f"Match found for **{top_match['incident_id']}** ({top_match['affected_device']}):\n\n" \
              f"• **Root Cause**: {top_match['probable_root_cause']}\n" \
              f"• **Priority**: {top_match['priority']}\n" \
              f"• **Impact**: {top_match['estimated_impact']}"
        return {
            "answer": ans,
            "referenced_incident": top_match["incident_id"],
            "next_action": top_match["next_best_action"]
        }

    # General Fallback
    return {
        "answer": f"I analyzed your request against {len(incidents)} active incidents and {len(alerts)} network alerts. No direct match was found.\n\nTry asking:\n" \
                  f"• *'What is the most critical incident?'*\n" \
                  f"• *'Why is INC-2026-001 critical?'*\n" \
                  f"• *'What should I do first for INC-2026-001?'*\n" \
                  f"• *'Which alerts are related to core-router-dal-01?'*",
        "referenced_incident": None,
        "next_action": "Review the active incidents table on the dashboard."
    }
