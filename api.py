import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import pandas as pd
import io
import json
import os
import bcrypt
from .components.exportar_pdf import exportar_dashboard_pdf
from .logic.procesar_archivo import procesar_archivo, leer_csv_robusto
from .logic.filtros import aplicar_filtros
from .logic.feedback import analizar_grupo, recomendar

app = FastAPI()

# Permitir peticiones desde cualquier origen (ajusta origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # LOCAL: abierto para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BLOQUE CORS PARA PRODUCCIÓN (descomenta y personaliza cuando subas a Render) ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://astrorituals.es",
#         "https://www.astrorituals.es"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# -------------------------------------------------------------------------------

# RECORDATORIO PARA PASO A PRODUCCIÓN:
# 1. Cambia las URLs del frontend a la de Render (https://opticamp.onrender.com)
# 2. Comenta el bloque CORS de desarrollo (allow_origins=["*"])
# 3. Descomenta el bloque CORS de producción (allow_origins=["https://astrorituals.es", ...])
# 4. Sube y despliega en Render
# 5. Prueba el login y dashboard en https://astrorituals.es/opticamp/
# -------------------------------------------------------------------------------

USUARIOS_PATH = os.path.join(os.path.dirname(__file__), 'components', 'usuarios.json')

def cargar_usuarios():
    if not os.path.isfile(USUARIOS_PATH):
        return []
    with open(USUARIOS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def verificar_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

@app.post("/login/")
async def login(form_data: dict):
    """
    Login de usuario. Recibe JSON: {"usuario": "...", "password": "..."
    Devuelve: {"usuario": ..., "plan": ..., "token": ...}
    """
    usuario = form_data.get("usuario")
    password = form_data.get("password")
    if not usuario or not password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña requeridos")
    usuarios = cargar_usuarios()
    user = next((u for u in usuarios if u["usuario"] == usuario), None)
    if not user or not verificar_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    # Token simple (puedes mejorar con JWT)
    token = f"token-{usuario}"
    return {"usuario": usuario, "plan": user["plan"], "token": token}

@app.post("/analizar/")
async def analizar_csv(file: UploadFile = File(...)):
    """
    Sube un CSV de campañas y devuelve KPIs, feedback, gráficas globales e individuales y tabla resumen en JSON (modo BASIC mejorado).
    """
    import tempfile
    content = await file.read()
    try:
        # Guardar archivo temporalmente para pasarlo a leer_csv_robusto
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        df_raw, delim, error_info = leer_csv_robusto(tmp_path)
        os.unlink(tmp_path)
        if df_raw is None:
            return JSONResponse(content={
                "error": "No se pudo leer el archivo CSV. Prueba con otro delimitador o revisa el formato.",
                "diagnostico": error_info
            }, status_code=400)
        df, columnas_faltantes, columnas_encontradas = procesar_archivo(df_raw, file.filename)
        if columnas_faltantes:
            return JSONResponse(content={
                "error": f"Faltan columnas requeridas: {columnas_faltantes}. Columnas encontradas: {columnas_encontradas}"
            }, status_code=400)
        # Añadir columna de recomendación si no existe
        if 'Recomendación' not in df.columns:
            df['Recomendación'] = df.apply(analizar_grupo, axis=1).apply(recomendar)
        # KPIs principales globales
        gasto_total = float(df['Gasto'].sum()) if 'Gasto' in df.columns else None
        conversiones = int(df['Conversiones'].sum()) if 'Conversiones' in df.columns else None
        ctr = float(df['CTR'].mean()) if 'CTR' in df.columns else None
        cpa = float(df['Gasto'].sum() / df['Conversiones'].sum()) if 'Gasto' in df.columns and 'Conversiones' in df.columns and df['Conversiones'].sum() > 0 else None
        # Feedback global sencillo
        if conversiones == 0:
            feedback = "No se han registrado conversiones. Revisa la segmentación, la oferta y la landing page."
        elif ctr and ctr < 1:
            feedback = "El CTR es bajo. Prueba nuevas creatividades y segmentaciones."
        elif cpa and cpa > 50:
            feedback = "El CPA es alto. Optimiza la segmentación y revisa la oferta."
        else:
            feedback = "Buen rendimiento general. Sigue optimizando y probando cambios."
        # --- GRAFICA GLOBAL: por mes (si existe columna 'Mes') ---
        grafica_global = None
        if 'Mes' in df.columns and 'Gasto' in df.columns:
            meses = df['Mes'].unique().tolist()
            datos_gasto = [float(df[df['Mes'] == m]['Gasto'].sum()) for m in meses]
            grafica_global = {"labels": meses, "gasto": datos_gasto}
        # --- GRAFICAS Y KPIs POR CAMPAÑA ---
        campanas = []
        if 'Campaña' in df.columns:
            for nombre, df_camp in df.groupby('Campaña'):
                kpi_camp = {
                    "gasto": float(df_camp['Gasto'].sum()) if 'Gasto' in df_camp.columns else None,
                    "conversiones": int(df_camp['Conversiones'].sum()) if 'Conversiones' in df_camp.columns else None,
                    "ctr": float(df_camp['CTR'].mean()) if 'CTR' in df_camp.columns else None,
                    "cpa": float(df_camp['Gasto'].sum() / df_camp['Conversiones'].sum()) if 'Gasto' in df_camp.columns and 'Conversiones' in df_camp.columns and df_camp['Conversiones'].sum() > 0 else None
                }
                feedback_camp = df_camp['Recomendación'].iloc[0] if 'Recomendación' in df_camp.columns else ""
                # Gráfica individual por mes
                grafica = None
                if 'Mes' in df_camp.columns and 'Gasto' in df_camp.columns:
                    meses = df_camp['Mes'].unique().tolist()
                    datos_gasto = [float(df_camp[df_camp['Mes'] == m]['Gasto'].sum()) for m in meses]
                    grafica = {"labels": meses, "gasto": datos_gasto}
                campanas.append({
                    "nombre": nombre,
                    "kpis": kpi_camp,
                    "feedback": feedback_camp,
                    "grafica": grafica
                })
        # Tabla resumen (primeras 20 filas)
        columnas_tabla = [col for col in ['Campaña','Nombre','Gasto','Clics','Conversiones','CTR','CPC','CPA','ROAS','CPM','Recomendación'] if col in df.columns]
        tabla = df[columnas_tabla].head(20).to_dict(orient="records")
        return JSONResponse(content={
            "kpis": {
                "gasto_total": gasto_total,
                "conversiones": conversiones,
                "ctr": ctr,
                "cpa": cpa
            },
            "feedback": feedback,
            "grafica_global": grafica_global,
            "campanas": campanas,
            "tabla": tabla
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.post("/generar_pdf/")
async def generar_pdf(file: UploadFile = File(...)):
    """
    Sube un CSV y devuelve el PDF del dashboard generado.
    """
    content = await file.read()
    try:
        df_raw = pd.read_csv(io.BytesIO(content))
        df, _, _ = procesar_archivo(df_raw, file.filename)
        columnas_pdf = [col for col in ['Campaña','Nombre','Gasto','Clics','Conversiones','CTR','CPC','CPA','ROAS','CPM','Recomendación'] if col in df.columns]
        df_export = df[columnas_pdf]
        feedback_global = "Resumen generado desde API"
        # Ajusta la ruta a tu ejecutable de wkhtmltopdf si es necesario
        wkhtml_path = r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
        # Ajusta la ruta a tu logo si lo quieres en el PDF
        logo_path = "gpt/components/logo.png"
        pdf_bytes, _ = exportar_dashboard_pdf(
            df_export=df_export,
            feedback_global=feedback_global,
            wkhtml_path=wkhtml_path,
            logo_path=logo_path
        )
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

"""
INSTRUCCIONES RÁPIDAS:

- Lanza la API con:
    uvicorn gpt.api:app --reload

- Endpoints:
    POST /analizar/    # Sube un CSV y recibe KPIs en JSON
    POST /generar_pdf/ # Sube un CSV y recibe el PDF generado

- Consúmelo desde WordPress vía AJAX, WPForms Webhook, o cualquier frontend.
- Si necesitas seguridad, añade autenticación por token o API key.
"""