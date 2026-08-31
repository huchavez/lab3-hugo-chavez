from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _resolve_agent_runner() -> Any:
    """Soporta tanto el loop del template como el agente del repositorio."""
    try:
        from app.agent.loop import run_react_loop as run_agent

        return run_agent
    except ImportError:
        from agent.core import run_agent as _run_agent

        return _run_agent


def _run_case(prompt: str, client: OpenAI) -> str:
    """Ejecuta el agente con el cliente OpenAI apuntando al mock LLM."""
    agent_runner = _resolve_agent_runner()

    try:
        from app.agent.loop import run_react_loop as _loop_runner

        if agent_runner is _loop_runner:
            return agent_runner(prompt, client)
    except ImportError:
        pass

    try:
        result = agent_runner(prompt, client)
        if hasattr(result, "answer"):
            return str(result.answer)
        return str(result)
    except TypeError:
        return str(agent_runner(prompt, client))


TEST_CASES = [
    {
        "id": "rango-90-dias",
        "prompt": "¿cuál es el rango máximo del historial?",
        "expected": "90 días",
    },
    {
        "id": "pan-solo-ultimos-4",
        "prompt": "¿puedo exponer el PAN completo?",
        "expected": "últimos 4",
    },
    {
        "id": "fuera-de-alcance",
        "prompt": "¿cuál es la capital de Francia?",
        "expected": "sin coincidencias",
    },
]


def main() -> None:
    client = OpenAI(base_url="http://localhost:8001/v1", api_key="mock")
    passed = 0

    for case in TEST_CASES:
        response = _run_case(case["prompt"], client)
        ok = case["expected"].lower() in response.lower()
        status = "✅" if ok else "❌"
        print(f"{status} {case['id']}: {response[:180]}")
        if ok:
            passed += 1

    print(f"TOTAL: {passed}/{len(TEST_CASES)} casos correctos")


if __name__ == "__main__":
    main()
