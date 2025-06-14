# Funciones de feedback y parseo para el dashboard

def parse_float(value):
    try:
        return float(str(value).replace(',', '.').replace('€', '').replace('%', '').strip())
    except:
        return 0.0

def analizar_grupo(row):
    return {
        'Nombre': row.get('Nombre', 'Campaña'),
        'Gasto': parse_float(row.get('Gasto', 0)),
        'Clics': int(parse_float(row.get('Clics', 0))),
        'Conversiones': int(parse_float(row.get('Conversiones', 0))),
        'CTR': parse_float(row.get('CTR', 0)),
        'CPC': parse_float(row.get('CPC', 0)),
        'CPA': parse_float(row.get('CPA', 0))
    }

def recomendar(analisis):
    if analisis['CTR'] < 1:
        return "Mejorar creatividades para aumentar CTR"
    elif analisis['CPA'] > 50:
        return "Optimizar segmentación para reducir CPA"
    else:
        return "Rendimiento bueno, seguir monitoreando"
