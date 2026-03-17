# Sistema de Extracción Automatizada de CVs

## 📋 Descripción

Sistema inteligente para procesar currículums vitae en formato PDF, extrayendo información estructurada mediante **Google Gemini 1.5 Flash** y organizándola en un archivo Excel para análisis por parte del equipo de Recursos Humanos.

### Características principales:
- ✅ Lectura automática de texto digital en PDFs
- 🖼️ OCR visual para PDFs escaneados (usando Gemini multimodal)
- 🔄 Procesamiento incremental (solo archivos nuevos)
- 📊 Exportación a Excel con formato profesional
- 🧠 Análisis inteligente de trayectorias y detección de inconsistencias

---

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   PDF Source    │────▶│   pdfplumber     │────▶│  Texto Digital  │
│   (Carpeta)     │     │   (Extracción)   │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                      #Python (Cloud) ☃ ──────────────────────────────┐      ──────────────────────────────┐
                                       1. Entrada PDF    │───▶│     ┌──────────────────────────────┐
                                           | │     2. Gemini 1.5 Flash   │    └──────────────────────────────┘
                                           | │     3. Extracción  …   │    └──────────────────────────────┘
                                           | …    └──────────────────────────────┘
                                           | │     4. Excel    │
                                            ┘─────────────────┘
                                             JSON │    └─────────────────────────────┐
                                                 │
┘─────────────────┘
                                             Controler │    │───▶│
                                            ┘─────────────────┘

                                              JS

```

### ▐┌────────────────┘ Files chave

- `.gitignore`: Configuración de archivos a ignorar
- `agente-reclutamiento-v1/README.md`: Documentación término del agente v1
- `agente-reclutamiento-v1/archivos/`: Carpeta para PDFs de CV
- `agente-reclutamiento-v1/utils/`: Funciones utilitarias
- `agente-reclutamiento-v1/cvs_text.txt`: output de texto extraído
- `agente-reclutamiento-v2�README.md`: Documentación término del agente v2
- `agente-reclutamiento-v2/config.json`: Configuración
- `agente-reclutamiento-v2/index.js`: Archivo principal del agente v2
- `agente-reclutamiento-v2/run.js`: Script de ejecución del agente v2
- `agente-reclutamiento-v2/tarsonkifyer.js`: Extractor de CVs
- `agente-reclutamiento-v2/input-view.js`: Vista para constiguiendo datos de entrada
- `agente-reclutamiento-v2/queryu-find-view.js`: Vista para búsquedas
