# Diagrama de secuencia · Consultar historial de transacciones

```mermaid
sequenceDiagram
    autonumber
    participant Comercio
    participant API
    participant Autorizacion
    participant ConsultaTransacciones
    participant Repositorio

    Comercio->>API: GET /api/v1/transacciones?desde=...&hasta=...&estado=...
    API->>Autorizacion: Verificar JWT y comercio_id
    Autorizacion-->>API: Comercio válido / JWT válido
    API->>API: Validar filtros (fecha, rango 90 días, page_size)
    alt filtros válidos
        API->>ConsultaTransacciones: Ejecutar caso de uso de historial
        ConsultaTransacciones->>Repositorio: Consultar transacciones filtradas y paginadas
        Repositorio-->>ConsultaTransacciones: Resultado de transacciones + cursor
        ConsultaTransacciones-->>API: Datos paginados
        API-->>Comercio: 200 OK + JSON {data, pagination}
    else filtro inválido
        API-->>Comercio: 400 Bad Request + mensaje de error
    end

    alt autorización fallida
        Autorizacion-->>API: JWT inválido / comercio no autorizado
        API-->>Comercio: 401 Unauthorized
    end
```

## Notas

- El diagrama evita servicios externos no mencionados en el PRD.
- Se muestra el flujo normal y dos flujos alternativos: filtro inválido y autorización fallida.
