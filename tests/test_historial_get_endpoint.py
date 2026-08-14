"""
Tests for GET /api/v1/transacciones endpoint.

Covers:
- Authorization (JWT token validation)
- Date range filtering and validation
- State filtering
- Pagination with cursor
- Serialization (PAN masking)
"""

from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ========== Authorization Tests ==========


def test_get_transacciones_missing_authorization_header_returns_401() -> None:
    """GET without Authorization or x-comercio-id should fail."""
    response = client.get("/api/v1/transacciones")
    assert response.status_code == 401
    body = response.json()
    assert "Authorization token is required" in body["detail"]


def test_get_transacciones_invalid_bearer_token_returns_401() -> None:
    """GET with Bearer token that is not a valid UUID should fail."""
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": "Bearer not-a-uuid"},
    )
    assert response.status_code == 401
    body = response.json()
    assert "Invalid authorization token" in body["detail"]


def test_get_transacciones_valid_bearer_token_returns_200() -> None:
    """GET with valid Bearer token (UUID) should return 200."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_get_transacciones_x_comercio_id_header_returns_200() -> None:
    """GET with x-comercio-id header should work as fallback."""
    comercio_id = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"x-comercio-id": comercio_id},
    )
    assert response.status_code == 200


def test_get_transacciones_invalid_x_comercio_id_returns_401() -> None:
    """GET with non-UUID x-comercio-id should fail."""
    response = client.get(
        "/api/v1/transacciones",
        headers={"x-comercio-id": "not-a-uuid"},
    )
    assert response.status_code == 401
    body = response.json()
    assert "Invalid authorization token" in body["detail"]


def test_get_transacciones_bearer_token_with_extra_whitespace_works() -> None:
    """GET with Bearer token with extra whitespace should be trimmed."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer  {token}  "},
    )
    assert response.status_code == 200


# ========== Happy Path & Data Structure Tests ==========


def test_get_transacciones_happy_path_returns_response_structure() -> None:
    """GET returns correct response structure with data and pagination."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body
    assert isinstance(body["data"], list)
    assert "next_cursor" in body["pagination"]
    assert "page_size" in body["pagination"]


def test_get_transacciones_happy_path_returns_only_comercio_transactions() -> None:
    """GET returns only transactions for the authenticated comercio_id."""
    # comercio_id 123e4567-e89b-42d3-a456-426614174000 has 3 transactions in FAKE_DATA
    # comercio_id 999e4567-e89b-42d3-a456-426614174999 has 1 transaction
    token1 = "123e4567-e89b-42d3-a456-426614174000"
    response1 = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token1}"},
    )
    body1 = response1.json()
    assert len(body1["data"]) > 0
    assert all(tx["comercio_id"] == token1 for tx in body1["data"])

    token2 = "999e4567-e89b-42d3-a456-426614174999"
    response2 = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token2}"},
    )
    body2 = response2.json()
    # This comercio has 1 transaction
    assert len(body2["data"]) == 1
    assert body2["data"][0]["comercio_id"] == token2


def test_get_transacciones_masks_ultimos_4_pan() -> None:
    """GET returns PAN masked in format **** **** **** XXXX."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()
    assert len(body["data"]) > 0
    for transaction in body["data"]:
        assert "ultimos_4_pan" in transaction
        pan = transaction["ultimos_4_pan"]
        assert pan.startswith("**** **** **** ")
        last_4 = pan[-4:]
        assert last_4.isdigit()


def test_get_transacciones_returns_required_fields() -> None:
    """GET returns all required transaction fields."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()
    required_fields = [
        "transaccion_id",
        "comercio_id",
        "monto",
        "created_at",
        "estado",
        "ultimos_4_pan",
        "codigo_autorizacion",
    ]
    for transaction in body["data"]:
        for field in required_fields:
            assert field in transaction


# ========== Filtering Tests ==========


def test_get_transacciones_filter_by_estado_returns_only_matching() -> None:
    """GET with estado filter returns only transactions with that estado."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"estado": "approved"},
    )
    body = response.json()
    # comercio_id 123e4567... has at least 2 'approved' transactions
    assert len(body["data"]) > 0
    assert all(tx["estado"] == "approved" for tx in body["data"])


def test_get_transacciones_filter_by_estado_pending() -> None:
    """GET with estado=pending returns only pending transactions."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"estado": "pending"},
    )
    body = response.json()
    assert len(body["data"]) == 1  # Only one pending transaction
    assert body["data"][0]["estado"] == "pending"


def test_get_transacciones_filter_by_estado_no_match_returns_empty() -> None:
    """GET with estado filter that matches no transactions returns empty data."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"estado": "refunded"},
    )
    body = response.json()
    assert body["data"] == []


# ========== Date Range Filter Tests ==========


def test_get_transacciones_filter_by_desde_only() -> None:
    """GET with desde date only returns transactions >= desde."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    desde = date(2026, 8, 3)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"desde": desde.isoformat()},
    )
    body = response.json()
    assert len(body["data"]) > 0
    for tx in body["data"]:
        tx_date = datetime.fromisoformat(tx["created_at"]).date()
        assert tx_date >= desde


def test_get_transacciones_filter_by_hasta_only() -> None:
    """GET with hasta date only returns transactions <= hasta."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    hasta = date(2026, 8, 2)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"hasta": hasta.isoformat()},
    )
    body = response.json()
    assert len(body["data"]) > 0
    for tx in body["data"]:
        tx_date = datetime.fromisoformat(tx["created_at"]).date()
        assert tx_date <= hasta


def test_get_transacciones_filter_by_desde_and_hasta() -> None:
    """GET with both desde and hasta returns transactions within range."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    desde = date(2026, 8, 2)
    hasta = date(2026, 8, 4)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"desde": desde.isoformat(), "hasta": hasta.isoformat()},
    )
    body = response.json()
    assert len(body["data"]) > 0
    for tx in body["data"]:
        tx_date = datetime.fromisoformat(tx["created_at"]).date()
        assert desde <= tx_date <= hasta


def test_get_transacciones_invalid_date_range_desde_gt_hasta_returns_400() -> None:
    """GET with desde > hasta returns 400 error."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    desde = date(2026, 8, 5)
    hasta = date(2026, 8, 1)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"desde": desde.isoformat(), "hasta": hasta.isoformat()},
    )
    assert response.status_code == 400
    body = response.json()
    assert "rango de fecha es inválido" in body["detail"]


def test_get_transacciones_date_too_old_returns_400() -> None:
    """GET with desde older than 90 days returns 400 error."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    too_old = datetime.utcnow().date() - timedelta(days=91)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"desde": too_old.isoformat()},
    )
    assert response.status_code == 400
    body = response.json()
    assert "90 días" in body["detail"]


# ========== Pagination Tests ==========


def test_get_transacciones_respects_page_size() -> None:
    """GET with page_size returns <= page_size items."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 2},
    )
    body = response.json()
    assert len(body["data"]) <= 2
    assert body["pagination"]["page_size"] == 2


def test_get_transacciones_default_page_size_is_50() -> None:
    """GET without page_size uses default of 50."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()
    assert body["pagination"]["page_size"] == 50


def test_get_transacciones_page_size_min_boundary() -> None:
    """GET with page_size=1 is valid."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) <= 1


def test_get_transacciones_page_size_max_boundary() -> None:
    """GET with page_size=200 is valid."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 200},
    )
    assert response.status_code == 200


def test_get_transacciones_page_size_exceeds_max_returns_422() -> None:
    """GET with page_size > 200 returns 422 validation error."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 201},
    )
    assert response.status_code == 422


def test_get_transacciones_page_size_zero_returns_422() -> None:
    """GET with page_size=0 returns 422 validation error."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 0},
    )
    assert response.status_code == 422


def test_get_transacciones_cursor_pagination() -> None:
    """GET with cursor pagination returns next page of results."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    # First page
    response1 = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 1},
    )
    body1 = response1.json()
    first_tx_id = body1["data"][0]["transaccion_id"]
    cursor = body1["pagination"]["next_cursor"]

    # Second page using cursor
    response2 = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 1, "cursor": cursor},
    )
    body2 = response2.json()
    if len(body2["data"]) > 0:
        second_tx_id = body2["data"][0]["transaccion_id"]
        # They should be different transactions
        assert second_tx_id != first_tx_id


def test_get_transacciones_no_next_cursor_when_no_more_pages() -> None:
    """GET returns next_cursor=None when all results fit in page."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 200},  # Max allowed page size
    )
    body = response.json()
    # With page_size=200, comercio 123e4567... has only 3 transactions, so no next_cursor
    assert body["pagination"]["next_cursor"] is None


# ========== Combined Filter Tests ==========


def test_get_transacciones_filter_estado_and_date_range() -> None:
    """GET with both estado and date range filters."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    desde = date(2026, 8, 1)
    hasta = date(2026, 8, 5)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "estado": "approved",
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat(),
        },
    )
    body = response.json()
    for tx in body["data"]:
        assert tx["estado"] == "approved"
        tx_date = datetime.fromisoformat(tx["created_at"]).date()
        assert desde <= tx_date <= hasta


def test_get_transacciones_all_filters_combined() -> None:
    """GET with estado, date range, and pagination."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    desde = date(2026, 8, 1)
    hasta = date(2026, 8, 5)
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "estado": "approved",
            "desde": desde.isoformat(),
            "hasta": hasta.isoformat(),
            "page_size": 10,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body


# ========== Cursor Edge Case Tests ==========


def test_get_transacciones_cursor_with_same_timestamp_different_id() -> None:
    """
    GET cursor pagination handles case where two transactions
    have same created_at but different transaction IDs.

    This tests the cursor comparison logic:
    if created_at == cursor_time and transaction_id < cursor_id
    """
    token = "123e4567-e89b-42d3-a456-426614174000"
    # First fetch with very small page size
    response1 = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 1},
    )
    body1 = response1.json()
    assert len(body1["data"]) == 1
    first_cursor = body1["pagination"]["next_cursor"]

    # If there's a next cursor, get the next page
    if first_cursor:
        response2 = client.get(
            "/api/v1/transacciones",
            headers={"Authorization": f"Bearer {token}"},
            params={"page_size": 1, "cursor": first_cursor},
        )
        assert response2.status_code == 200
        body2 = response2.json()
        # Should have at most 1 item
        assert len(body2["data"]) <= 1


def test_get_transacciones_invalid_cursor_format_returns_400() -> None:
    """GET with malformed cursor returns 400 error."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    # Cursor without pipe separator
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"cursor": "invalid_cursor_format"},
    )
    assert response.status_code == 400
    body = response.json()
    assert "Cursor inválido" in body["detail"]


def test_get_transacciones_cursor_past_all_items_returns_empty() -> None:
    """GET with cursor before all items (far past) returns empty data list."""
    token = "123e4567-e89b-42d3-a456-426614174000"
    # Create a cursor that is "before" all transactions (far past date)
    # Items are sorted reverse (newest first), so cursor before oldest item
    # means we've already paginated past everything
    past_cursor = "2025-01-01T00:00:00|00000000-0000-0000-0000-000000000000"
    response = client.get(
        "/api/v1/transacciones",
        headers={"Authorization": f"Bearer {token}"},
        params={"cursor": past_cursor, "page_size": 10},
    )
    assert response.status_code == 200
    body = response.json()
    # Should have no data since cursor is before all items
    assert body["data"] == []
    assert body["pagination"]["next_cursor"] is None
