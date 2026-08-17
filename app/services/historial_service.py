from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Literal

from app.repositories.historial_repo import (
    query_transacciones_in_memory,
)

Estado = Literal["pending", "approved", "rejected", "refunded", "cancelled"]


MAX_DIAS = 90


def _mask_ultimos_4_pan(ultimos_4_pan: str) -> str:
    return f"**** **** **** {ultimos_4_pan}"


def _validate_date_range(desde: date | None, hasta: date | None) -> None:
    if desde and hasta and desde > hasta:
        raise ValueError("El rango de fecha es inválido")

    if desde:
        max_antiguo = datetime.utcnow().date() - timedelta(days=MAX_DIAS)
        if desde < max_antiguo:
            raise ValueError("El rango excede el máximo permitido (90 días)")


def query_transacciones(
    comercio_id: str,
    desde: date | None,
    hasta: date | None,
    estado: Estado | None,
    page_size: int,
    cursor: str | None,
) -> dict:
    _validate_date_range(desde, hasta)

    transacciones = query_transacciones_in_memory(
        comercio_id=comercio_id,
        desde=desde,
        hasta=hasta,
        estado=estado,
        page_size=page_size,
        cursor=cursor,
    )

    data = [
        {
            "transaccion_id": item["transaccion_id"],
            "comercio_id": item["comercio_id"],
            "monto": item["monto"],
            "created_at": item["created_at"].isoformat(),
            "estado": item["estado"],
            "ultimos_4_pan": _mask_ultimos_4_pan(item["ultimos_4_pan"]),
            "codigo_autorizacion": item["codigo_autorizacion"],
        }
        for item in transacciones["items"]
    ]

    return {
        "data": data,
        "pagination": {
            "next_cursor": transacciones["next_cursor"],
            "page_size": page_size,
        },
    }
