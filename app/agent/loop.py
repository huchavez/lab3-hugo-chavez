from __future__ import annotations

import json
from typing import Any

from app.agent.logger import log_step
from app.agent.tools import buscar_regla_prd

# Baranda #1 · BUDGET · límite de iteraciones del loop
MAX_STEPS = 5

# Baranda #2 · SCOPE · en el SYSTEM_PROMPT
SYSTEM_PROMPT = (
    "Solo respondés sobre el PRD del Historial de Transacciones · LegacyPay. "
    "Si te preguntan otra cosa decís 'fuera de alcance'. No ejecutás acciones "
    "destructivas. No inventás resultados. Responde SIEMPRE en JSON con "
    "los campos thought, action y action_input. Las acciones permitidas son "
    "'buscar_regla_prd' y 'final'."
)


def _parse_decision(raw: str) -> tuple[str, str, dict[str, Any]]:
    """Parsea la decisión del LLM según el formato ReAct esperado."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - validación defensiva
        raise ValueError(f"La respuesta del LLM no es JSON válido: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("La respuesta del LLM debe ser un objeto JSON.")

    thought = str(payload.get("thought", ""))
    action = str(payload.get("action", "")).strip()
    action_input = payload.get("action_input", {})

    if not isinstance(action_input, dict):
        raise ValueError("El campo action_input debe ser un diccionario.")

    if action not in {"buscar_regla_prd", "final"}:
        raise ValueError(f"Acción no soportada: {action}")

    return thought, action, action_input


def run_react_loop(prompt: str, client: Any) -> str:
    """Ejecuta el ciclo ReAct del agente para contestar consultas sobre el PRD."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )
        raw = response.choices[0].message.content or ""

        try:
            thought, action, action_input = _parse_decision(raw)
        except ValueError as exc:
            raise RuntimeError(
                f"Decisión inválida del LLM en el paso {step}: {exc}"
            ) from exc

        if action == "final":
            respuesta = str(
                action_input.get("respuesta", action_input.get("answer", ""))
            )
            if not respuesta:
                raise RuntimeError(
                    "El LLM respondió 'final' sin una respuesta en action_input."
                )
            return respuesta

        if action == "buscar_regla_prd":
            termino = str(action_input.get("termino", ""))
            if not termino:
                result = "Debe indicar un término de búsqueda no vacío."
            else:
                result = buscar_regla_prd(termino)
            log_step(step, "buscar_regla_prd", {"termino": termino}, result)
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Observation: {result}"})
            continue

    raise RuntimeError(
        f"Se alcanzó el límite de MAX_STEPS={MAX_STEPS} sin respuesta final."
    )
