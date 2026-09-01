# AERIS-X

**AI-Driven AWS Anomaly Intelligence & Resilience System** for SIH26073.

A real-time command center that detects anomalous Automatic Weather Station observations and explains whether the anomaly is a genuine atmospheric event or a likely sensor/data fault.

## Hero workflow

`Observation → Adaptive Baseline → Ensemble Anomaly Score → Counterfactual Weather Twin → Event vs Sensor Fault → Explainable Alert → Sensor Health`

## Included

- FastAPI backend with real-time anomaly analysis
- Statistical + Isolation Forest anomaly ensemble
- Counterfactual observed-vs-expected weather twin
- Multivariate event/fault discrimination
- Fault simulation: spike, freeze, drift, dropout, coherent event
- Network health, station map and anomaly feed
- Operator-focused AERIS Copilot explanation layer
- PostgreSQL/Supabase production schema
- Docker Compose deployment

## Run

```bash
docker compose up --build
```

Open `http://localhost:5173`. API docs are at `http://localhost:8000/docs`.

## Demo

1. Open Command Center and select `TN-042`.
2. Choose **Temperature Spike** → **Inject & Analyze**.
3. Show the anomaly feed and Counterfactual Weather Twin.
4. Choose **Genuine Weather Event** → **Inject & Analyze**.
5. Show that both cases can be anomalous while the diagnosis differs.
6. Ask **AERIS Copilot** for the operator explanation.

## Architecture

```text
AWS / CSV / MQTT
      ↓
  Ingestion API
      ↓
 Validation + Features
      ↓
Statistical + ML Ensemble
      ↓
Counterfactual Weather Twin
      ↓
 Event / Sensor Fault
      ↓
 XAI + Health + Alerts
      ↓
Command Center + Copilot
```

## Production path

The hackathon build uses an in-memory demo store for speed. The supplied SQL schema moves persistence to PostgreSQL/Supabase. Keep raw observations immutable and store quality flags/corrections separately for auditability.

## Evaluation honesty

The simulator uses controlled synthetic data. Do not claim accuracy/F1/false-alarm improvements until a reproducible benchmark against a labeled dataset has been run.
