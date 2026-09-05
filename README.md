# NetTriage AI - Network Incident Triage Assistant

NetTriage AI is a Python-based backend application designed for automated telecom network incident triage, alert correlation, RAG runbook recommendation, Gemini LLM reasoning, and Tier-3 escalation management.

## Project Structure

```
nettriage-ai/
├── app.py              # Main Flask application entry point
├── requirements.txt    # Project dependencies
├── README.md           # Documentation
├── src/                # Core application logic and modules
├── data/               # Raw and processed network alert data
├── runbooks/           # SOPs and triage runbook documents
└── frontend/           # Web interface assets and UI templates
```

## Setup & Execution

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the assistant:
   Open your browser and visit [http://localhost:8000](http://localhost:8000)

## Roadmap

- [x] Step 1: Project setup & minimal Flask server
- [ ] Step 2: Alert processing & incident grouping
- [ ] Step 3: Runbook retrieval (RAG)
- [ ] Step 4: Gemini embeddings & LLM reasoning integration
- [ ] Step 5: Escalation workflow & dashboard UI
