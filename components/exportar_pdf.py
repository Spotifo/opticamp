import os
import tempfile
from typing import Optional

def exportar_dashboard_pdf(df_export, feedback_global: str, wkhtml_path: str, logo_path: Optional[str] = None):
    """
    Genera un PDF con la tabla de campañas (solo columnas clave y en orden).
    Si se proporciona logo_path y existe, lo incluye en el PDF.
    Devuelve (pdf_bytes, errores: list[str])
    """
    import pdfkit
    errores = []
    pdf_bytes = None
    # --- Tabla solo con las columnas clave y en orden ---
    columnas_orden = [
        'Campaña', 'Gasto', 'Clics', 'Conversiones', 'CTR', 'CPC', 'CPA', 'Recomendación'
    ]
    df_aux = df_export.copy()
    # Alias para asegurar que siempre haya columna 'Campaña'
    if 'Nombre' in df_aux.columns and 'Campaña' not in df_aux.columns:
        df_aux['Campaña'] = df_aux['Nombre']
    if 'Nombre' in df_aux.columns:
        df_aux = df_aux.drop(columns=['Nombre'])
    renames = {
        'Campaña': 'Nombre campaña',
        'Gasto': 'Gasto (€)',
        'Clics': 'Clics',
        'Conversiones': 'Conversiones',
        'CTR': 'CTR (%)',
        'CPC': 'CPC (€)',
        'CPA': 'CPA (€)',
        'Recomendación': 'Acción recomendada'
    }
    columnas_final = [col for col in columnas_orden if col in df_aux.columns]
    df_aux = df_aux[columnas_final].rename(columns=renames)
    tabla_html = df_aux.to_html(index=False, border=0, classes='tabla-campanas', justify='center')
    # --- Logo opcional ---
    logo_html = ''
    if logo_path and os.path.isfile(logo_path):
        logo_html = f'<img src="{logo_path}" alt="Logo" style="height:60px;margin-bottom:1.5rem;">'
    # --- HTML final ---
    html = f'''
    <html><head><meta charset="utf-8">
    <style>
    body {{ font-family: Inter, Arial, sans-serif; color: #111; background: #fff; }}
    h1 {{ color: #2563eb; }}
    .tabla-campanas {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
    .tabla-campanas th, .tabla-campanas td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: center; }}
    .tabla-campanas th {{ background: #e0e7ef; color: #2563eb; font-weight: 700; }}
    .tabla-campanas td {{ background: #f8fafc; }}
    </style></head><body>
    {logo_html}
    <h1>Resumen de Campañas</h1>
    {tabla_html}
    </body></html>
    '''
    # --- Forzar nombre de archivo temporal único para cada PDF generado ---
    import uuid
    unique_id = uuid.uuid4().hex
    try:
        if not os.path.isfile(wkhtml_path):
            errores.append(f"❌ No se encontró el ejecutable 'wkhtmltopdf.exe' en: {wkhtml_path}")
            raise FileNotFoundError(wkhtml_path)
        if not os.access(wkhtml_path, os.X_OK):
            errores.append(f"❌ El ejecutable 'wkhtmltopdf.exe' no tiene permisos de ejecución en: {wkhtml_path}")
            raise PermissionError(wkhtml_path)
        config = pdfkit.configuration(wkhtmltopdf=wkhtml_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{unique_id}.html") as f_html:
            f_html.write(html.encode("utf-8"))
            html_path = f_html.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{unique_id}.pdf") as f_pdf:
            pdfkit.from_file(html_path, f_pdf.name, configuration=config)
            f_pdf.seek(0)
            pdf_bytes = f_pdf.read()
            if not pdf_bytes or len(pdf_bytes) < 1000:
                errores.append(f"❌ El PDF generado está vacío o corrupto. Revisa la ruta y permisos de wkhtmltopdf.exe: {wkhtml_path}")
    except Exception as e:
        errores.append(f"❌ Error al generar el PDF. Ruta ejecutable: {wkhtml_path}\n\n{str(e)}")
    return pdf_bytes, errores
