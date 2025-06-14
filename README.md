# Opticamp Backend (FastAPI)

Este repositorio contiene el backend de Opticamp para análisis de campañas y generación de PDFs, listo para desplegar en Render.com o cualquier servicio compatible con FastAPI.

## Estructura

- `api.py` — Entrypoint principal de la API (FastAPI)
- `components/` — Funciones auxiliares (PDF, login, etc.)
- `logic/` — Lógica de negocio y procesamiento de archivos
- `exportados/` — (opcional) wkhtmltopdf.exe y archivos exportados
- `csv_importados/` — (opcional) para archivos subidos/procesados
- `estilos/` — CSS para dashboards
- `formulario.html`, `pdf.html` — Formularios de ejemplo

## Despliegue en Render.com

1. Sube esta carpeta (`gpt/`) como raíz de tu repo en GitHub.
2. En Render, selecciona este repo y pon `gpt` como Root Directory.
3. Start Command:
   ```
   uvicorn api:app --host 0.0.0.0 --port 10000
   ```
4. Build Command:
   ```
   pip install -r requirements.txt
   ```

## Requisitos

- Python 3.9+
- FastAPI, Uvicorn, Pandas, Jinja2, ReportLab, python-multipart

## Notas
- El ejecutable `wkhtmltopdf.exe` debe estar en `exportados/` o ajusta la ruta en `api.py`.
- El logo para los PDFs debe estar en `components/logo.png` o ajusta la ruta.

---

Cualquier duda, abre un issue o contacta con el desarrollador.
