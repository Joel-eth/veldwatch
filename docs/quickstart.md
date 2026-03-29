# Quick Start

## Install the SDK

```bash
pip install veldwatch
```

## Instrument your agent

```python
from veldwatch.sdk import watch, trace

@watch(agent_id="my-researcher")
def run_agent(prompt):
    result = call_llm(prompt)
    return result
```

## Run the full stack locally

```bash
git clone https://github.com/Joel-eth/veldwatch
cd veldwatch
cp .env.example .env
docker compose -f docker/docker-compose.yml up
```

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
