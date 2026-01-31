# Agentic AI for Smart Payment Operations

An intelligent, real-time agentic system for optimizing payment operations. This system observes payment streams, uses bandits and circuit breakers to reason about failures, and autonomously intervenes to improve success rates.

## Architecture

- **Agents**:
  - `router.py`: Thompson Sampling Multi-Armed Bandit for gateway selection.
  - `sentinel.py`: Sliding window circuit breaker.
  - `recovery.py`: LLM-based failure analysis and recovery strategy.
- **Core**:
  - `graph.py`: LangGraph workflow orchestration.
  - `kafka.py`: Event streaming abstraction.
- **Safety**:
  - `validators.py`: Input sanitization and anomaly detection.
  - `config.co`: Guardrails configuration.
- **UI**:
  - `dashboard.py`: Streamlit-based realtime operations dashboard.

## Usage

The system is managed via the `manage.sh` script which handles Docker containers.

```bash
# Start all services (API + Dashboard)
./manage.sh start

# Stop all services
./manage.sh stop

# Restart services
./manage.sh restart

# View logs
./manage.sh logs
```

The services will be available at:
- **API**: [http://localhost:8000](http://localhost:8000)
- **Dashboard**: [http://localhost:8502](http://localhost:8502)
