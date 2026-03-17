# Arquitectura del Sistema de Reclutamiento
> Workflow Agéntico · Patrones: Routing + Tool Calling · NLP para análisis de idoneidad

---

## Índice

1. [Módulo 1 — Definición de la naturaleza](#módulo-1--definición-de-la-naturaleza)
2. [Módulo 2 — Ingesta](#módulo-2--ingesta)
3. [Módulo 3 — Procesamiento](#módulo-3--procesamiento)
4. [Módulo 4 — Salida / Respuesta / Resultado](#módulo-4--salida--respuesta--resultado)
5. [Módulo 5 — Documentación](#módulo-5--documentación)
6. [Módulo 6 — Proyección financiera y Modelo de negocio](#módulo-6--proyección-financiera-y-modelo-de-negocio)
7. [Módulo 7 — Observabilidad y Trazabilidad](#módulo-7--observabilidad-y-trazabilidad)
8. [Capa de Configuraciones Generales](#capa-de-configuraciones-generales)

---

## Módulo 1 — Definición de la naturaleza

**Función:** Establecer el marco arquitectónico y el alcance operativo del sistema.

**Tareas:**
- Definir el sistema como un **Workflow Agéntico** (Patrones *Routing* y *Tool Calling*).
- Establecer el objetivo: automatización del análisis de idoneidad mediante NLP.
- Determinar el nivel de autonomía: ejecución orquestada con decisiones semánticas.

---

## Módulo 2 — Ingesta

**Función:** Gestión de la entrada de datos y normalización del repositorio físico.

### Submódulo: Orden

**Función:** Ejecutar la migración y estandarización del sistema de archivos.

**Tareas:**
- **Migración Inmutable:** lectura y copiado exclusivo desde el Repositorio Viejo (Legacy). El origen no se modifica.
- **Estandarización:** renombrado automático a `CV — [Nombre] [Apellido]`. Inclusión de sufijos para Referidos.
- **Estructuración:** creación de carpetas por **Posición** en el Repositorio Nuevo.

### Tareas Generales

- Detección de eventos (*Event-Driven*) en OneDrive y Email.
- Validación de integridad mediante hashes SHA-256 para evitar duplicados.

---

## Módulo 3 — Procesamiento

**Función:** Transformación de archivos no estructurados en datos de inteligencia.

**Tareas:**
- **Parsing y Normalización:** limpieza de texto y extracción de entidades (validación rigurosa de nombres).
- **Motor de Match Heurístico:** comparación semántica entre candidatos y perfiles.
- **Módulo de Razonamiento:** generación de score (1–100) y justificación técnica del resultado.

---

## Módulo 4 — Salida / Respuesta / Resultado

**Función:** Persistencia y comunicación de los resultados del flujo.

**Tareas:**
- Escritura de datos estructurados en Excel centralizado: funciona como **tablero de control de usuarios**.
- Escritura de datos estructurados en Excel centralizado: otro archivo que funciona como **resultados de la evaluación de reclutamiento**.
- Envío de e-mail con información de la evaluación del candidato.

---

## Módulo 5 — Documentación

> **Formato:** Markdown (`.md`) · **Destino:** GitHub

**Función:** Repositorio de ingeniería para el autor (Alex). Referencia técnica y funcional del sistema.

**Tareas:**

- **Documentación Técnica:**
  - Especificación de la arquitectura de capas.
  - Diagramas de flujo.
  - Documentación de APIs externas (Gemini, Microsoft Graph, Telegram).
  - Gestión de secretos y configuraciones.

- **Documentación Funcional:**
  - Definición de la lógica del scoring.
  - Criterios del motor heurístico.
  - Guía de mantenimiento del flujo.

- **Referencia de Prompts:** registro versionado de los System Prompts utilizados.

---

## Módulo 6 — Proyección financiera y Modelo de negocio

**Función:** Análisis de viabilidad y estrategia de activos.

**Tareas:**
- Cálculo de costo operativo por registro (tokens de API).
- Estrategia de defensa de Propiedad Intelectual (IP) del código.
- Modelado de venta: consultoría o licenciamiento.

---

## Módulo 7 — Observabilidad y Trazabilidad

**Función:** Control de salud, métricas y auditoría.

**Tareas:**
- **Logging:** registro con *Correlation ID* para seguimiento de la migración (Viejo → Nuevo).
- **Dashboard:** monitoreo de Uptime, tasa de acierto y consumo financiero en tiempo real.

---

## Capa de Configuraciones Generales

> Fuera del flujo principal

| Componente | Descripción |
|---|---|
| **Control de Versiones** | Repositorio en GitHub |
| **Gobernanza** | Normas de comportamiento del agente y seguridad de datos |
