# ADR 0003: Estrategia de paginación para el historial de transacciones

## Contexto

LegacyPay debe ofrecer a los comercios afiliados un endpoint de historial de transacciones que soporte consultas grandes sin degradar la experiencia. El historial puede crecer mucho para comercios de alto volumen, y el acceso se limita a los últimos 90 días. El endpoint debe ser auditable y presentar resultados paginados. En esta fase no se deben asumir benchmarks ni SLA que no estén aprobados.

## Alternativas

### A. Paginación basada en cursor (cursor-based pagination)
- Se usa un cursor opaco o semántico que codifica `created_at` y `transaccion_id`.
- La API devuelve `next_cursor` y opcionalmente `prev_cursor`.
- El backend consulta índices en la tabla de transacciones para obtener la siguiente página.

Pros:
- Rendimiento estable con crecimiento de datos porque evita saltos costosos en `OFFSET`.
- Mejor experiencia para resultados ordenados por fecha (`created_at DESC`) y para navegación hacia adelante.
- Menor riesgo de duplicados o elementos faltantes cuando hay inserciones concurrentes.

Contras:
- Implementación ligeramente más compleja que `OFFSET`.
- La lógica de `prev_cursor` y navegación bidireccional puede requerir cuidado extra.
- Auditoría del recorrido de páginas requiere almacenar o reconstruir cursores opacos.

### B. Paginación basada en `OFFSET`/`LIMIT`
- El cliente envía `page` o `offset` y `page_size`.
- El backend usa `LIMIT page_size OFFSET offset`.

Pros:
- Muy fácil de implementar y comprender.
- Adecuada para casos de datos pequeños o moderados.
- Simple de auditar porque los parámetros de página son explícitos.

Contras:
- El rendimiento empeora con crecimiento de datos grandes debido a los saltos de `OFFSET` en la base de datos.
- La experiencia de usuario puede ser inconsistente si se insertan o eliminan transacciones durante la paginación.
- No escala tan bien para comercios con muchos datos en 90 días.

### C. Paginación basada en páginas numeradas con límite y filtro de fecha
- Similar a OFFSET/LIMIT, pero restringido a rangos de fecha para limitar el tamaño del conjunto.
- Puede combinar `desde` y `hasta` con `page_size` y `page_number`.

Pros:
- Control de conjunto más explícito; más fácil de rastrear en auditoría.
- Reduce el tamaño de cada procesamiento cuando el filtro de fecha es estricto.

Contras:
- Sigue heredando los problemas de OFFSET para consultas amplias dentro del rango máximo de 90 días.
- Depende de que los usuarios apliquen filtros de fecha estrechos para mantener buen rendimiento.

## Decisión propuesta

Adoptar la alternativa A: paginación basada en cursor para el endpoint de historial de transacciones.

Justificación:
- El historial puede crecer mucho para comercios de alto volumen y la solución debe escalar sin depender del tamaño total de la página.
- El endpoint está ordenado por `created_at DESC`, lo cual encaja bien con cursores basados en orden de creación.
- Cursor-based pagination ofrece mejor experiencia de usuario en escenarios de navegación continua y reduce los efectos de datos en movimiento.
- La implementación puede mantenerse simple para la lectura unidireccional hacia adelante, con `next_cursor` como mínimo obligatorio.

## Consecuencias positivas

- Mejor rendimiento bajo crecimiento de datos en comparación con `OFFSET` en lotes grandes.
- Menor probabilidad de resultados inconsistentes cuando las transacciones se agregan durante la paginación.
- Mejor ajuste al requisito de consultas de alta cardinalidad con paginación eficiente.
- Posibilidad de cachear respuestas por clave `(comercio_id + filtros + cursor)` de forma natural.

## Consecuencias negativas

- Mayor complejidad de implementación respecto a paginación de offset.
- Necesidad de documentar claramente el formato y la validez de los cursores.
- La navegación bidireccional (prev cursor) puede requerir trabajo adicional si se decide soportarla.
- La auditoría del flujo de páginas puede requerir reconstrucción de cursores o registro de parámetros opacos.

## Evidencia pendiente

- Validar con el equipo de producto si `prev_cursor` es un requisito para UX o si basta con `next_cursor`.
- Verificar el costo real de implementación frente a la complejidad del backend actual.
- Confirmar si la base de datos ya está indexada adecuadamente en `comercio_id, created_at DESC` para este patrón.
- Evaluar casos concretos de paginación de comercios con más de 5.000 transacciones/mes.

## Condición de revisión

Revisar esta decisión cuando se confirme cualquiera de estos puntos:
- se definan requisitos UX adicionales para navegación bidireccional o salto arbitrario de páginas;
- se identifique un problema de rendimiento en consultas de paginación con el patrón de cursor propuesto;
- se apruebe un estilo de paginación alternativo por el equipo de producto o arquitectura.
