import os
from flask import Flask, jsonify, render_template, request
from src.alert_loader import get_all_alerts, get_alert_by_id, get_alerts_summary
from src.incident_correlator import correlate_alerts
from src.copilot_engine import answer_copilot_query
from src.alert_simulator import simulate_new_alert

app = Flask(__name__, template_folder='frontend', static_folder='frontend')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/alerts', methods=['GET'])
def api_get_alerts():
    alerts = get_all_alerts()
    return jsonify({
        "status": "success",
        "count": len(alerts),
        "alerts": alerts
    })

@app.route('/api/alerts/summary', methods=['GET'])
def api_get_alerts_summary():
    summary = get_alerts_summary()
    return jsonify({
        "status": "success",
        "summary": summary
    })

@app.route('/api/alerts/<alert_id>', methods=['GET'])
def api_get_alert_by_id(alert_id):
    alert = get_alert_by_id(alert_id)
    if alert:
        return jsonify({
            "status": "success",
            "alert": alert
        })
    return jsonify({
        "status": "error",
        "message": f"Alert with ID '{alert_id}' not found."
    }), 404

@app.route('/api/incidents', methods=['GET'])
def api_get_incidents():
    alerts = get_all_alerts()
    incidents = correlate_alerts(alerts)
    return jsonify({
        "status": "success",
        "count": len(incidents),
        "incidents": incidents
    })

@app.route('/api/incidents/<incident_id>', methods=['GET'])
def api_get_incident_by_id(incident_id):
    alerts = get_all_alerts()
    incidents = correlate_alerts(alerts)
    for inc in incidents:
        if inc.get("incident_id") == incident_id:
            return jsonify({
                "status": "success",
                "incident": inc
            })
    return jsonify({
        "status": "error",
        "message": f"Incident with ID '{incident_id}' not found."
    }), 404

@app.route('/api/copilot/chat', methods=['POST'])
def api_copilot_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    response_payload = answer_copilot_query(message)
    return jsonify({
        "status": "success",
        "response": response_payload
    })

@app.route('/api/alerts/simulate', methods=['POST'])
def api_simulate_alert():
    new_alert = simulate_new_alert()
    all_alerts = get_all_alerts()
    incidents = correlate_alerts(all_alerts)
    
    # Find incident containing newly created alert
    target_inc = None
    for inc in incidents:
        rel_ids = [a.get("id") for a in inc.get("related_alerts", [])]
        if new_alert["id"] in rel_ids:
            target_inc = inc
            break

    return jsonify({
        "status": "success",
        "simulated_alert": new_alert,
        "incident_count": len(incidents),
        "correlated_incident": target_inc
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
