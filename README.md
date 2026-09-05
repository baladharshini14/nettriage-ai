#  NetTriage AI – Network Incident Triage Assistant

> Real-time alert correlation and automated telecom network incident triage system.

NetTriage AI is a network operations assistant designed to help NOC operators analyze multiple network alerts, correlate related events, identify probable root causes, prioritize incidents, and recommend the next troubleshooting action.

---

##  Live Demo

 https://nettriage-ai-tsq9.onrender.com

---

##  Source Code

 https://github.com/baladharshini14/nettriage-ai

---

##  Problem Statement

In telecom networks, a single network failure can generate multiple alerts from different devices.

For example:

- Link Down
- High Latency
- Device Unreachable
- Authentication Failure
- Power Failure

Manually analyzing these alerts takes time and can create alert overload for NOC operators.

The main challenge is:

**Multiple Alerts → One Underlying Problem**

NetTriage AI helps operators identify the relationship between alerts and consolidate them into meaningful network incidents.

---

## 💡 Solution

NetTriage AI provides a centralized NOC dashboard that:

1. Collects network alerts
2. Correlates related alerts
3. Groups alerts into incidents
4. Identifies probable root causes
5. Assigns incident priority
6. Recommends troubleshooting actions
7. Displays incident details
8. Provides an AI Copilot for incident queries
9. Supports real-time alert simulation

---

## ✨ Key Features

### 🔗 Intelligent Alert Correlation

Related alerts from the same device or related network conditions are grouped into a single incident.

Example:

```text
LINK_DOWN
     +
HIGH_LATENCY
     +
AUTH_FAILURE
     ↓
Correlated Network Incident
