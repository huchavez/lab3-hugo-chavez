from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreateRequest(BaseModel):
    """Request body for creating a payment transaction record.

    This model is intentionally strict about input format and shape. Any
    business decision (authorization, duplication checks, reconciliation)
    belongs in the service layer, not in the schema.
    """

    model_config = ConfigDict(extra="forbid")

    comercio_id: str = Field(
        ...,
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
        description="UUID del comercio afiliado.",
    )
    # Se valida como UUID por formato para evitar IDs no válidos, nulos o
    # mal formados antes de que lleguesn al servicio. La validación es
    # determinista y no declara ninguna regla de negocio.

    monto: int = Field(
        ...,
        gt=0,
        description="Monto de la transacción en centavos.",
    )
    # gt=0 evita 0, negativos y valores nulos que no representan una
    # transacción válida. El dominio usa centavos para prevenir errores por
    # punto flotante; el servicio decide la conversión final a moneda.

    estado: Literal["pending", "approved", "rejected", "refunded", "cancelled"] = Field(
        ...,
        description="Estado del ciclo de vida de la transacción.",
    )
    # Literal restringe los valores del enum de negocio al conjunto definido por
    # el PRD; esto evita estados arbitrarios y mantiene la API consistente.

    ultimos_4_pan: str = Field(
        ...,
        min_length=4,
        max_length=4,
        pattern=r"^\d{4}$",
        description="Últimos 4 dígitos del PAN expuestos por cumplimiento PCI-DSS.",
    )
    # La regex exige exactamente 4 dígitos para evitar cualquier exposición del
    # PAN completo o de valores con letras, espacios o longitud incorrecta.

    codigo_autorizacion: str = Field(
        ...,
        min_length=6,
        max_length=12,
        pattern=r"^[A-Z0-9]+$",
        description="Código de autorización emitido por el gateway.",
    )
    # La regex mantiene un formato de código estándar y determinista; impide
    # caracteres especiales, espacios o cadenas vacías que normalmente indican
    # un dato corrupto o un intento de entrada no normalizada.
