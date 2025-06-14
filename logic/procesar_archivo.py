# Funciones para procesar y normalizar archivos CSV
import pandas as pd
from .feedback import parse_float

def parse_float_robusto(x):
    if pd.isnull(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        # Elimina % y espacios, reemplaza coma por punto
        x = x.replace('%', '').replace(' ', '').replace('\u202f', '').replace('\xa0', '').replace('"', '')
        x = x.replace(',', '.')
        # Si hay varios valores concatenados, toma solo el primero
        for sep in [';', '\t', '|']:
            if sep in x:
                x = x.split(sep)[0]
        try:
            return float(x)
        except Exception:
            return 0.0
    return 0.0

def procesar_archivo(df, archivo_nombre):
    df.columns = df.columns.str.strip()
    mapeo_columnas = {
        # Google Ads (ES)
        'Mes': 'Mes',
        'Campaña': 'Nombre',  # Solo mapea Campaña a Nombre
        'Clics': 'Clics',
        'Impr.': 'Impresiones',
        'CTR': 'CTR',
        'CPC medio': 'CPC',
        'Coste': 'Gasto',
        'Conversiones': 'Conversiones',
        'Coste/conv.': 'CPA',
        'Tasa de conv.': 'CVR',
        # Google Ads (EN)
        'Campaign': 'Nombre',
        'Cost': 'Gasto',
        'Clicks': 'Clics',
        'All conversions': 'Conversiones',
        'Impressions': 'Impresiones',
        'Avg. CPC': 'CPC',
        # Facebook Ads (EN)
        'Campaign name': 'Nombre',
        'Amount spent': 'Gasto',
        'Link clicks': 'Clics',
        'Results': 'Conversiones',
        'Impressions': 'Impresiones',
        'Cost per link click': 'CPC',
        # Pinterest
        'Spend': 'Gasto',
        'Clicks': 'Clics',
        'Conversions': 'Conversiones',
        # TikTok
        'Ad name': 'Nombre',
        'Total spend': 'Gasto',
        'Website clicks': 'Clics',
        'Reach': 'Impresiones',
        'Click-through rate': 'CTR',
        'Cost per click': 'CPC',
        # Meta/Facebook Ads (ES)
        'Nombre del grupo publicitario': 'Nombre',
        'Gasto total': 'Gasto',
        'Clics en el Pin': 'Clics',
        'Resultado': 'Conversiones',
        'Campaña de Performance': 'Campaña',
        'Campaña Premiere Spotlight': 'Campaña',
        'CPM': 'CPM',
    }
    df = df.rename(columns=mapeo_columnas)
    columnas_requeridas = ['Nombre', 'Gasto', 'Clics', 'Conversiones']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if columnas_faltantes:
        return None, columnas_faltantes, list(df.columns)
    for col in ['Gasto', 'Clics', 'Conversiones', 'CTR', 'CPC', 'CPA', 'CVR', 'Impresiones']:
        if col in df.columns:
            df[col] = df[col].apply(parse_float_robusto)
    if 'CTR' not in df.columns and 'Impresiones' in df.columns:
        df['CTR'] = (df['Clics'] / df['Impresiones'].replace(0, 1)) * 100
    if 'CPC' not in df.columns:
        df['CPC'] = df['Gasto'] / df['Clics'].replace(0, 1)
    if 'CVR' not in df.columns:
        df['CVR'] = (df['Conversiones'] / df['Clics'].replace(0, 1)) * 100
    # Añadir columna de ranking por gasto
    if 'Gasto' in df.columns:
        df['RankingGasto'] = df['Gasto'].rank(ascending=False, method='min').astype(int)
    # Añadir columna de color sugerido (paleta básica)
    colores = ['#2563eb', '#10b981', '#f59e42', '#ef4444', '#a855f7', '#fbbf24', '#14b8a6', '#6366f1', '#eab308', '#f472b6']
    if 'Nombre' in df.columns:
        nombres_unicos = df['Nombre'].unique()
        color_map = {nombre: colores[i % len(colores)] for i, nombre in enumerate(nombres_unicos)}
        df['ColorCampaña'] = df['Nombre'].map(color_map)
    return df, None, None

def leer_csv_robusto(archivo_path, encodings=None):
    """
    Intenta leer un CSV probando varios delimitadores y encodings. Si falla, prueba autodetección de delimitador con utf-16/utf-16le.
    Devuelve el DataFrame, el delimitador y encoding usados, y si falla, un preview de las primeras filas y columnas detectadas.
    """
    import pandas as pd
    if encodings is None:
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'utf-16', 'utf-16le']
    delimitadores = [';', ',', '\t']
    errores = []
    # 1. Prueba todos los delimitadores con todos los encodings
    for encoding in encodings:
        for delim in delimitadores:
            try:
                df = pd.read_csv(archivo_path, delimiter=delim, encoding=encoding)
                if len(df.columns) > 1:
                    return df, (delim, encoding), None
            except Exception as e:
                errores.append(f"Delimitador '{delim}', encoding '{encoding}': {str(e)}")
    # 2. Prueba delimitador ';' explícitamente con utf-16 y utf-16le (por si BOM y delimitador juntos)
    for encoding in ['utf-16', 'utf-16le']:
        try:
            df = pd.read_csv(archivo_path, delimiter=';', encoding=encoding)
            if len(df.columns) > 1:
                return df, (';', encoding), None
        except Exception as e:
            errores.append(f"Delimitador ';', encoding '{encoding}' (extra): {str(e)}")
    # 3. Prueba autodetección de delimitador con utf-16 y utf-16le
    for encoding in ['utf-16', 'utf-16le']:
        try:
            df = pd.read_csv(archivo_path, encoding=encoding)
            if len(df.columns) > 1:
                return df, (None, encoding), None
        except Exception as e:
            errores.append(f"Autodetect, encoding '{encoding}': {str(e)}")
    # 4. Preview de error (lectura manual si todo falla)
    try:
        # Buscar la línea de cabecera real (la que contiene 'Mes\tCampaña')
        with open(archivo_path, encoding='utf-16') as f:
            lineas = []
            header_idx = None
            for idx, linea in enumerate(f):
                lineas.append(linea)
                if 'Mes\tCampaña' in linea:
                    header_idx = idx
                    break
            # Leer 4 líneas más para preview
            for _ in range(4):
                try:
                    lineas.append(next(f))
                except StopIteration:
                    break
        # Si se encontró la cabecera, intentar leer con pandas desde esa línea
        if header_idx is not None:
            try:
                df = pd.read_csv(archivo_path, delimiter='\t', encoding='utf-16', header=header_idx)
                if len(df.columns) > 1:
                    return df, ('\t', 'utf-16', header_idx), None
            except Exception as e:
                errores.append(f"Lectura avanzada con header en línea {header_idx}: {str(e)}")
        # Preview manual
        preview_manual = [l.strip().split('\t') for l in lineas]
        columnas = preview_manual[header_idx] if header_idx is not None else []
    except Exception as e:
        preview_manual = str(e)
        columnas = []
    return None, None, {
        'errores': errores,
        'preview_manual': preview_manual,
        'columnas_detectadas': columnas
    }
