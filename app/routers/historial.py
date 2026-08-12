from __future__ import annotations

from datetime import date
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.schemas.transaction_create_request import TransactionCreateRequest
from app.services.historial_service import query_transacciones

router = APIRouter(prefix="/api/v1", tags=["Historial"])


def _extract_comercio_id(
    authorization: Optional[str] = Header(None),
    x_comercio_id: Optional[str] = Header(None),
) -> str:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif x_comercio_id:
        token = x_comercio_id.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Authorization token is required")

    try:
        UUID(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization token")

    return token


@router.get("/transacciones")
def get_transacciones(
    comercio_id: str = Depends(_extract_comercio_id),
    desde: Optional[date] = Query(None, description="Fecha inicial en formato YYYY-MM-DD"),
    hasta: Optional[date] = Query(None, description="Fecha final en formato YYYY-MM-DD"),
    estado: Optional[Literal["pending", "approved", "rejected", "refunded", "cancelled"]]
    = Query(None, description="Estado a filtrar"),
    page_size: int = Query(50, ge=1, le=200, description="Tamaño de página entre 1 y 200"),
    cursor: Optional[str] = Query(None, description="Cursor opaco para paginación"),
) -> dict:
    try:
        return query_transacciones(
            comercio_id=comercio_id,
            desde=desde,
            hasta=hasta,
            estado=estado,
            page_size=page_size,
            cursor=cursor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/transacciones", status_code=201)
def create_transaccion(payload: TransactionCreateRequest) -> dict:
    return payload.model_dump()
