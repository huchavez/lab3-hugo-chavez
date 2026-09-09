from __future__ import annotations

from pathlib import Path

PRD_PATH = Path(__file__).resolve().parents[2] / "docs" / "prd" / "PRD.md"

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "buscar_regla_prd",
            "description": (
                "Busca lexicalmente un término dentro del PRD del Historial de "
                "Transacciones de LegacyPay y devuelve coincidencias con contexto."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "termino": {
                        "type": "string",
                        "description": "Término a buscar dentro del PRD.",
                    }
                },
                "required": ["termino"],
            },
        },
    }
]


def buscar_regla_prd(termino: str) -> str:
    """Busca lexicalmente un término en el PRD y devuelve hasta 3 hits con contexto."""
    if not isinstance(termino, str) or not termino.strip():
        return "Debe indicar un término de búsqueda no vacío."

    if not PRD_PATH.exists():
        return f"PRD no encontrado en la ruta esperada: {PRD_PATH}."

    lines = PRD_PATH.read_text(encoding="utf-8").splitlines()
    needle = termino.strip().lower()
    hits: list[str] = []

    for index, line in enumerate(lines):
        if needle in line.lower():
            start = max(0, index - 3)
            end = min(len(lines), index + 4)
            context = "\n".join(
                f"{line_no + 1}: {lines[line_no]}" for line_no in range(start, end)
            )
            hits.append(f"[línea {index + 1}]\n{context}")
            if len(hits) >= 3:
                break

    if not hits:
        return f"Sin coincidencias en docs/prd/PRD.md para '{termino}'."

    return (
        f"Coincidencias para '{termino}' en docs/prd/PRD.md (máximo 3 hits):\n\n"
        + "\n\n---\n\n".join(hits)
    )
