# Postmortem · Proyecto Final · Hugo Chávez · 2026-08-31

## Qué funcionó

- El agente RAG basado en patrón ReAct quedó estructurado con los módulos principales `app/agent/tools.py`, `app/agent/loop.py` y `app/agent/logger.py`, con `MAX_STEPS = 5` y un `SYSTEM_PROMPT` que limita explícitamente el alcance a la PRD del proyecto. Esto evitó que el agente responda fuera de contexto o invente resultados.
- La tool `buscar_regla_prd(termino: str) -> str` funcionó como búsqueda lexical sobre `docs/prd/PRD.md`, devolviendo coincidencias con contexto ±3 líneas, manejando casos sin coincidencias y archivos faltantes sin romper la ejecución.
- La validación del flujo del agente quedó cubierta por un evaluador de 3 casos en `evals/eval_agent.py` para: rango de 90 días, exposición del PAN y consulta fuera de alcance. El resultado verificado en la auditoría fue `3/3` casos correctos en el flujo con mock LLM.
- La corrección del import path en el runner de evaluación fue clave: al ejecutarse desde `evals/`, se añadió la raíz del repositorio a `sys.path` antes de importar `app`, resolviendo el `ModuleNotFoundError` que bloqueaba la ejecución del evaluador.
- La suite de pruebas del proyecto terminó en estado verificado: `74/74` pruebas pasando con cobertura del `95.05%`, por encima del umbral requerido del `60%`. La evidencia se registró en `docs/terminal_responses_proyecto_final.txt`.
- El trabajo de auditoría y documentación quedó trazado en varios artefactos del repositorio (`AUDIT_SUMMARY.md`, `AUDIT_FINDINGS.md`, `AUDIT_CHECKLIST.md`, `AUDIT_CAMBIOS_AGENTE.md`) y en el historial de commits disponible en Git, lo cual permitió reconstruir el estado final del proyecto con evidencia.

## Qué no funcionó

- El primer bloqueo real apareció al ejecutar el evaluador desde `evals/`: Python no incluía la raíz del proyecto en `sys.path`, por lo que `from app.agent.loop import ...` fallaba con `ModuleNotFoundError`. Esta fue una causa de entorno, no de lógica del agente.
- La cobertura inicial de la suite no cumplía el umbral mínimo. El proyecto se encontraba en `57%` de cobertura antes de reforzar pruebas del paquete `app.agent`, y la corrección consistió en ampliar la batería de pruebas sin cambiar la lógica principal del agente.
- Hubo advertencias de compatibilidad futuras (`datetime.utcnow()` y `starlette.testclient` con `httpx`), pero estas no bloquearon la ejecución ni incumplieron el requisito funcional ni de cobertura. Se registraron como warnings no críticos.
- Se evidenció la necesidad de mantener el alcance explícito desde el inicio; sin esa barrera, el agente puede derivar a consultas no contempladas por el PRD. El cambio de diseño con `SYSTEM_PROMPT` y `MAX_STEPS` fue la respuesta para estabilizar esa conducta.

## Qué haría distinto

- Definiría antes la política de alcance y el límite de pasos como criterio de diseño explícito, en lugar de revisarlo después. El prompt con scope controlado fue determinante para evitar respuestas fuera de contexto.
- Añadiría una validación más temprana del runner de evaluación desde subdirectorios del repositorio, para detectar antes errores de import path y no bloquear la ejecución del flujo de pruebas.
- Mantendría la documentación de validación y los artefactos de auditoría en un flujo más lineal: evidencias de terminal, resultados de tests y decisiones del agente registrados en tiempo real, para reducir la reconstrucción posterior.
- Seguiría priorizando pruebas pequeñas y reproducibles sobre cambios de lógica del agente; la combinación de `temperature=0` y mock LLM permitió un comportamiento determinista y verificable.

## 3 lecciones aprendidas

1. Sobre agentes: la barra de alcance es una condición necesaria. El `SYSTEM_PROMPT` con la regla “solo respondés sobre el PRD; si te preguntan otra cosa decís ‘fuera de alcance’” redujo la deriva de comportamiento y evitó respuestas inventadas.
2. Sobre RAG: en dominios pequeños y acotados, la búsqueda lexical con contexto es una solución simple, reproducible y suficiente. Los mensajes de `sin coincidencias` y el manejo de PRD inexistente fueron esenciales para la robustez del flujo.
3. Sobre trabajo con IA: documentar en tiempo real y conservar la evidencia de ejecución (pruebas, terminal, commits y auditorías) es más valioso que reconstruir el proceso después. La trazabilidad disponible en el repositorio fue clave para cerrar el proyecto con una conclusión verificable.

## Cierre

El proyecto quedó en un estado validado y reproducible: el agente responde únicamente sobre la PRD, la evaluación con mock LLM fue ejecutada y comprobada, y la suite final alcanzó `74/74` pruebas pasando con `95.05%` de cobertura, cumpliendo el requisito del `60%`. El principal aprendizaje del trabajo fue que la determinismo y la robustez del agente no vienen de “hacerlo menos inteligente”, sino de limitar el alcance, controlar el número de pasos y dejar evidencias verificables de cada decisión.
