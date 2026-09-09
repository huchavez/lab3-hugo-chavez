# AI_USAGE.md · Proyecto Final · Hugo Chávez

## Registro de decisiones asistidas por IA

## Entrada 1 · 2026-08-31

**Contexto:** se trabajó en la base del agente RAG del proyecto final, con el objetivo de responder consultas sobre las reglas de negocio del PRD del Historial de Transacciones·LegacyPay.

**Herramienta IA:** GitHub Copilot (Copilot Agent / asistente de código del editor).

**Prompt clave:** la solicitud documentada en `docs/terminal_responses_proyecto_final.txt` describe la creación del esqueleto inicial del agente con `app/agent/tools.py`, `app/agent/loop.py` y `app/agent/logger.py`, con una tool `buscar_regla_prd(termino: str) -> str`, `TOOLS_SCHEMA`, loop ReAct y logging JSONL.

**Decisión IA:** propuso la estructura en Python 3.12, aplicó el patrón ReAct, definió `MAX_STEPS = 5`, agregó la barrera de scope explícita y documentó el logging en `logs/agent_run.jsonl`.

**Decisión humana:** acepté la propuesta con ajuste, incorporando la aclaración de barreras y el determinismo reproducible con `temperature=0` en pruebas con mock LLM.

**Aprendizaje:** la restricción de alcance (“solo sobre el PRD”) y el límite de pasos fueron decisiones claves para evitar respuestas fuera de contexto y lógica inventada.

## Entrada 2 · 2026-08-31

**Contexto:** creación del evaluador con 3 casos de validación del agente, según la demanda de `evals/eval_agent.py`.

**Herramienta IA:** GitHub Copilot.

**Prompt clave:** “Creá evals/eval_agent.py con 3 casos: rango-90-dias, pan-solo-ultimos-4 y fuera-de-alcance ... Cada caso ejecuta run_agent con cliente OpenAI...”.

**Decisión IA:** generó el evaluador con los 3 escenarios y la salida `✅/❌` por caso y total final.

**Decisión humana:** se validó la lógica del flujo y se confirmó la intención de evaluar el comportamiento del agente con el mock LLM del proyecto.

**Aprendizaje:** la evaluación debe comprobar no solo la respuesta final, sino que la herramienta de búsqueda y el scope del agente estén funcionando de manera reproducible.

## Entrada 3 · 2026-08-31

**Contexto:** corrección de un problema real de ejecución en el runner de evaluación cuando se ejecutaba desde `evals/`.

**Herramienta IA:** GitHub Copilot.

**Prompt clave:** “`uv run --frozen python evals/eval_agent.py` ... ModuleNotFoundError: No module named 'app' ... resolver el problema que arroja la terminal”.

**Decisión IA:** diagnosticó la causa raíz: Python no añadía la raíz del repositorio a `sys.path` al ejecutar desde una subcarpeta. Se propone agregar la ruta del proyecto antes de importar `app`.

**Decisión humana:** se aplicó la corrección y se validó que el evaluador quedaba ejecutable desde la raíz del proyecto.

**Aprendizaje:** los problemas de import en scripts de evaluación no son lógicos del agente; son un problema de entorno y de path, y se corrigen sin alterar la lógica principal.

## Entrada 4 · 2026-08-31

**Contexto:** revisión y cierre de la validación del proyecto final, incluida la comprobación de que los 3 casos del evaluador responden según la PRD y que la cobertura cumpla el umbral mínimo.

**Herramienta IA:** GitHub Copilot.

**Prompt clave:** el conjunto de evidencias del archivo de terminal muestra la ejecución del proyecto y confirma que los casos se ejecutan con mock LLM, con resultados de `3/3` correctos y luego `74 passed` con `95.05%` de cobertura.

**Decisión IA:** aportó la diagnosis final de la auditoría, identificando la causa del bloqueo de cobertura (pruebas insuficientes en `app.agent`) y la solución: ampliar pruebas sin tocar lógica core del agente.

**Decisión humana:** se decidió corregir solo lo mínimo necesario: path del runner y pruebas específicas de agente, manteniendo la funcionalidad principal intacta.

**Aprendizaje:** la validación final requiere evidencias de ejecución y no simplemente una intención de “que debería funcionar”; al documentar la salida exacta de pytest y coverage se hace trazable el cierre del proyecto.
