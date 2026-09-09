from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_transaction_happy_path_returns_201() -> None:
    # Arrange
    payload = {
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 1500,
        "estado": "approved",
        "ultimos_4_pan": "4242",
        "codigo_autorizacion": "A1B2C3",
    }

    # Act
    response = client.post("/api/v1/transacciones", json=payload)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["comercio_id"] == payload["comercio_id"]
    assert body["monto"] == payload["monto"]
    assert body["estado"] == payload["estado"]


def test_create_transaction_rejects_invalid_field_returns_422() -> None:
    # Arrange
    payload = {
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 1500,
        "estado": "approved",
        "ultimos_4_pan": "12A4",
        "codigo_autorizacion": "A1B2C3",
    }

    # Act
    response = client.post("/api/v1/transacciones", json=payload)

    # Assert
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert any("ultimos_4_pan" in str(item.get("loc", [])) for item in body["detail"])


def test_create_transaction_rejects_zero_monto_boundary_value() -> None:
    # Arrange
    payload = {
        "comercio_id": "123e4567-e89b-42d3-a456-426614174000",
        "monto": 0,
        "estado": "approved",
        "ultimos_4_pan": "4242",
        "codigo_autorizacion": "A1B2C3",
    }

    # Act
    response = client.post("/api/v1/transacciones", json=payload)

    # Assert
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert any("monto" in str(item.get("loc", [])) for item in body["detail"])
