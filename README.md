# Proyecto Final · Hugo Chàvez
Agente RAG que responde preguntas sobre el PRD "Historial de Transacciones LegacyPay". Basado en el patrón ReAct con retriever lexical sobre `docs/prd/PRD.md`.

## Cómo probarlo en 5 minutos

1. Clonar y sincronizar:
```bash
git clone https://github.com/huchavez/lab3-hugo-chavez.git
cd lab3-hugo-chavez
git switch proyecto-final
uv sync
```

Levantar el mock LLM (terminal aparte):
```bash
uv run --frozen uvicorn app.mock_llm:mock_app --port 8001
```

Test rápido para probar que responde (terminal 1 u otra terminal)
```bash
curl -s http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"plan"}]}' 
```

Para asegurar las ejecuciones siguientes, corre además el siguiente comando que instala la librería utilizada en el agente.
```bash
uv sync --extra llm
```

Correr el agente:
```bash
uv run --frozen python -c "
from openai import OpenAI
from app.agent.loop import run_react_loop
client = OpenAI(base_url='http://localhost:8001/v1', api_key='mock')
print(run_react_loop('¿cuál es el rango máximo del historial?', client))"
```

```bash
uv run --frozen python -c "
from openai import OpenAI
from app.agent.loop import run_react_loop
client = OpenAI(base_url='http://localhost:8001/v1', api_key='mock')
print(run_react_loop('¿cuál es la capital de Francia?', client))"
```

Correr el eval set:
```bash
uv run --frozen python evals/eval_agent.py
```

## Arquitectura del agente
Tools: `buscar_regla_prd` (registrada en `app/agent/tools.py`).\
Loop: patrón ReAct con `MAX_STEPS = 5`.\
RAG: retriever lexical sobre `docs/prd/PRD.md`.\
Log auditable: cada paso serializado en `logs/agent_run.jsonl`.

## Barandas aplicadas
Scope explícito en `SYSTEM_PROMPT` (`app/agent/loop.py`).\
Budget con `MAX_STEPS = 5` (`app/agent/loop.py`).
## Criterios de aceptación
[x] Al menos 2/3 casos del Eval Set pasan.\
[x] Cada corrida genera log auditable en `logs/agent_run.jsonl`.\
[x] Agente se abstiene ante preguntas fuera de alcance.\
[x] CI verde en GitHub Actions.

## Limitaciones conocidas
Retriever lexical sin embeddings · falla ante sinónimos.\
El mock LLM es determinístico · no cubre 100% de respuestas de un LLM real.