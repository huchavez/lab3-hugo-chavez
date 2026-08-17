from __future__ import annotations

from datetime import date, datetime
from typing import Any, TypedDict


# 1. Definimos la estructura exacta de la transacción
class Transaccion(TypedDict):
    transaccion_id: str
    comercio_id: str
    monto: int
    created_at: datetime
    estado: str
    ultimos_4_pan: str
    codigo_autorizacion: str

# 2. Tipamos la lista explícitamente
FAKE_TRANSACCIONES: list[Transaccion] = [
    {
        "transaccion_id": "a1111111-1111-1111-1111-111111111111",
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 1000,
        "created_at": datetime(2026, 8, 1, 12, 0, 0),
        "estado": "approved",
        "ultimos_4_pan": "4242",
        "codigo_autorizacion": "AUTH01",
    },
    {
        "transaccion_id": "b2222222-2222-2222-2222-222222222222",
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 2500,
        "created_at": datetime(2026, 8, 2, 10, 0, 0),
        "estado": "pending",
        "ultimos_4_pan": "5555",
        "codigo_autorizacion": "AUTH02",
    },
    {
        "transaccion_id": "c3333333-3333-3333-3333-333333333333",
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 4200,
        "created_at": datetime(2026, 8, 3, 9, 30, 0),
        "estado": "rejected",
        "ultimos_4_pan": "1234",
        "codigo_autorizacion": "AUTH03",
    },
    {
        "transaccion_id": "d4444444-4444-4444-4444-444444444444",
        "comercio_id": "999e4567-e89b-42d3-a456-426614174999",
        "monto": 3300,
        "created_at": datetime(2026, 8, 4, 15, 0, 0),
        "estado": "approved",
        "ultimos_4_pan": "9876",
        "codigo_autorizacion": "AUTH04",
    },
    {
        "transaccion_id": "e5555555-5555-5555-5555-555555555555",
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 1500,
        "created_at": datetime(2026, 8, 5, 16, 45, 0),
        "estado": "approved",
        "ultimos_4_pan": "4242",
        "codigo_autorizacion": "AUTH05",
    },
]


def _encode_cursor(created_at: datetime, transaccion_id: str) -> str:
    return f"{created_at.isoformat()}|{transaccion_id}"


def _decode_cursor(cursor: str) -> tuple[datetime, str]:
    parts = cursor.split("|", 1)
    if len(parts) != 2:
        raise ValueError("Cursor inválido")
    return datetime.fromisoformat(parts[0]), parts[1]


# 3. (Opcional pero recomendado) Mejoramos el tipado de retorno cambiando `dict` por `dict[str, Any]`
def query_transacciones_in_memory(
    comercio_id: str,
    desde: date | None,
    hasta: date | None,
    estado: str | None,
    page_size: int,
    cursor: str | None,
) -> dict[str, Any]:
    items = [
        item
        for item in FAKE_TRANSACCIONES
        if item["comercio_id"] == comercio_id
        and (desde is None or item["created_at"].date() >= desde)
        and (hasta is None or item["created_at"].date() <= hasta)
        and (estado is None or item["estado"] == estado)
    ]

    items.sort(key=lambda x: (x["created_at"], x["transaccion_id"]), reverse=True)

    if cursor:
        cursor_time, cursor_id = _decode_cursor(cursor)
        start_index = 0
        for index, item in enumerate(items):
            if item["created_at"] < cursor_time or (
                item["created_at"] == cursor_time and item["transaccion_id"] < cursor_id
            ):
                start_index = index
                break
        else:
            start_index = len(items)
    else:
        start_index = 0

    page = items[start_index : start_index + page_size]
    next_cursor = None
    if start_index + page_size < len(items):
        last = page[-1]
        next_cursor = _encode_cursor(last["created_at"], last["transaccion_id"])

    return {"items": page, "next_cursor": next_cursor}
