# Sistema de Extracción Automatizada de CVs (v0 — Recuperado)

> ⚠️ Este código fue **reconstruido desde los archivos `.pyc` compilados** del agente-reclutamiento-v1,
> cuyos archivos fuente `.py` se corrompieron durante sincronización de OneDrive.

## 📋 Descripción

Sistema inteligente para procesar currículums vitae en formatos PDF, .doc y .docx,
extrayendo información estructurada mediante **Google Gemini 2.0 Flash** y exportándola
a un archivo Excel con formato profesional.

## 🏗️ Arquitectura

```
main.py                 ← Orquestador principal
├── config.py           ← Configuración centralizada (@dataclass + .env)
├── file_manager.py     ← Gestión de archivos procesados (JSON + hash)
├── pdf_extractor.py    ← Extracción de texto de PDFs (pdfplumber)
├── word_extractor.py   ← Extracción de texto de Word (.doc/.docx)
├── gemini_analyzer.py  ← Análisis con IA (Google Gemini 2.0 Flash)
└── excel_exporter.py   ← Exportación a Excel (pandas + openpyxl)
```

## ⚙️ Instalación

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual (Windows)
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar y configurar .env
copy .env.example .env
# Editar .env con tu API Key de Gemini y la ruta a la carpeta de CVs
```

## 🚀 Uso

```bash
python main.py
```

El sistema:
1. Lee todos los CVs (.pdf, .doc, .docx) de la carpeta configurada
2. Filtra solo archivos nuevos o modificados
3. Extrae texto de cada archivo
4. Analiza con Gemini para extraer datos estructurados
5. Exporta los resultados a Excel

## 📊 Campos extraídos

| Campo | Descripción |
|---|---|
| Nombre | Primer nombre del candidato |
| Apellido | Apellido(s) |
| Email | Correo electrónico |
| Teléfono | Número de teléfono |
| Educación | Resumen de estudios |
| Idiomas | Lista con nivel |
| Trabajo más reciente | Cargo, empresa, funciones |
| Crecimiento | Evolución profesional |
| Contradicciones | Inconsistencias detectadas |
| Herramientas | Tecnologías con contexto de uso |

## 📝 Notas sobre la reconstrucción

- Los módulos `config.py`, `file_manager.py`, `pdf_extractor.py`, `word_extractor.py`,
  `gemini_analyzer.py` y `excel_exporter.py` fueron reconstruidos fielmente desde el
  bytecote Python 3.11 (archivos `.cpython-311.pyc`).
- El archivo `main.py` **no tenía .pyc**, fue reconstruido basándose en cómo
  interactúan los demás módulos.
- Los prompts de Gemini fueron extraídos textualmente de las constantes del bytecode.
