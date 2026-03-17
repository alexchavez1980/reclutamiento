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
9. [Referencia de Apoyo — Categorización Jerárquica del Repositorio](#referencia-de-apoyo--categorización-jerárquica-del-repositorio)

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

---

## Referencia de Apoyo — Categorización Jerárquica del Repositorio

> Esta sección describe la estructura de carpetas y subcarpetas del repositorio físico de CVs que el agente gestiona.

### Nivel 1: MACRO CATEGORÍAS

> Se recomienda usar numeración al inicio de las carpetas principales para forzar el orden deseado en Windows.

- 📁 **01_Perfiles_IT_y_Tecnologia** — El "Core" de los perfiles
- 📁 **02_Perfiles_Comerciales_y_Preventa**
- 📁 **03_Perfiles_Staff_y_Administracion**
- 📁 **04_Busquedas_Especificas_y_Proyectos** — Para guardar CVs de búsquedas en curso
- 📁 **05_Fuentes_y_Eventos** — Bases de datos masivas por eventos
- 📁 **06_Interno_y_Referidos**
- 📁 **07_Archivo_y_Por_Clasificar** — Para carpetas desactualizadas o pendientes

---

### Nivel 2 y 3: DESGLOSE RECOMENDADO

#### 📁 01_Perfiles_IT_y_Tecnologia

- 📁 01_Desarrollo_y_Programacion *(Ej: Java, Desarrollador .NET, Weblogic, Middleware)*
- 📁 02_Infraestructura_y_Cloud *(Ej: Cloud, Linux, Admin Solaris, Virtualización, DBA)*
- 📁 03_Redes_y_Seguridad *(Ej: Networking, Ciberseguridad, Técnico de Redes)*
- 📁 04_Datos_y_BI *(Ej: Big Data y Analytics, BI, Analista funcional de datos)*
- 📁 05_Gestion_Metodologias_y_Diseño *(Ej: PM, QA, DevOps, Analista Funcional, UX-UI)*
- 📁 06_Soporte_y_HelpDesk *(Ej: HelpDesk - call center, Adm IT - Soporte Interno)*
- 📁 07_Sistemas_Empresariales *(Ej: SAP, Salesforce)*

#### 📁 02_Perfiles_Comerciales_y_Preventa

- 📁 01_Ventas_y_Comercial *(Ej: BDM DELL, BDM Huawei, Comercial, Asistente Comercial)*
- 📁 02_Preventa *(Ej: Preventa Infraestructura, Preventa Seguridad, Consultor preventa Oracle JR)*
- 📁 03_Marketing_y_Comunicacion *(Ej: MKT)*

#### 📁 03_Perfiles_Staff_y_Administracion

- 📁 01_RRHH_y_Talento *(Ej: Analista de RRHH)*
- 📁 02_Administracion_y_Finanzas *(Ej: Administrativo contable, Analista de Facturación, Asistente Contable)*
- 📁 03_Legales_y_Compliance *(Ej: Abogado, Analista de Compliance)*
- 📁 04_Operaciones_y_Servicios_Generales *(Ej: Cadete, Recepción, Logística)*

#### 📁 04_Busquedas_Especificas_y_Proyectos

> Aquí irían las carpetas exclusivas para búsquedas puntuales o clientes que no deben mezclarse directamente con la base general hasta que termine la búsqueda.

- 📁 Búsqueda_HSBC
- 📁 Licitación_Nicaragua
- 📁 Roca *(Dividido en Dibujante y Supervisor)*
- 📁 Búsquedas_Activas_2024

#### 📁 05_Fuentes_y_Eventos

- 📁 Codo_a_Codo
- 📁 ExpoJoven_2021
- 📁 Human_Camp

#### 📁 06_Interno_y_Referidos

- 📁 Referidos *(Se mantiene aislada)*
- 📁 Empleados_Actuales *(Ej: CVs empleados)*

#### 📁 07_Archivo_y_Por_Clasificar

- 📁 Archivo_Historico_Bases *(Ej: CVs base Romi)*
- 📁 Por_Organizar *(Aquí se enviarían todas las carpetas como "Nueva carpeta", "Pasar", o las generadas como _files, para ser depuradas progresivamente)*
- 📁 Duplicados

---

### ¿Por qué esta estructura es idónea para un repositorio?

| Ventaja | Descripción |
|---|---|
| **Escalabilidad** | Al separar la "Materia Prima" (el perfil profesional neto) del "Contexto" (cuándo ingresó, a qué proyecto fue), el equipo siempre sabrá dónde buscar. Ej: un DevOps → Nivel 1 → Nivel 2 (Gestión). |
| **Evita la redundancia** | Limpia la raíz de las múltiples carpetas desorganizadas y resume todos los CVs en 7 espacios lógicos limitados. |
| **Facilita búsquedas** | Disminuye radicalmente el tiempo necesario para ubicar candidatos antiguos para nuevas búsquedas de perfiles similares (agrupación semántica funcional). |
