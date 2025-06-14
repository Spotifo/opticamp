# Funciones de filtros y utilidades para el dashboard
import pandas as pd
from .feedback import analizar_grupo, recomendar

def aplicar_filtros(df, canal, tipo, rango_gasto):
    df_filtrado = df.copy()
    if canal != 'Todos' and 'Canal' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Canal'] == canal]
    if tipo != 'Todos' and 'Tipo' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo]
    df_filtrado = df_filtrado[(df_filtrado['Gasto'] >= rango_gasto[0]) & (df_filtrado['Gasto'] <= rango_gasto[1])]
    if 'Recomendación' not in df_filtrado.columns:
        df_filtrado['Recomendación'] = df_filtrado.apply(analizar_grupo, axis=1).apply(recomendar)
    return df_filtrado
