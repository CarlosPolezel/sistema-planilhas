import pandas as pd
import io
import re

def normalizar_colunas(colunas):
    """Remove acentos, espaços extras e coloca tudo em minúsculas para padronizar a leitura."""
    col_limpas = []
    for c in colunas:
        c = str(c).lower().strip()
        c = re.sub(r'[áàâã]', 'a', c)
        c = re.sub(r'[éèê]', 'e', c)
        c = re.sub(r'[íìî]', 'i', c)
        c = re.sub(r'[óòôõ]', 'o', c)
        c = re.sub(r'[úùû]', 'u', c)
        c = c.replace('ç', 'c')
        col_limpas.append(c)
    return col_limpas

def ler_arquivo_importacao(arquivo, extensao) -> pd.DataFrame:
    """Lê o ficheiro carregado em memória e devolve um DataFrame com colunas normalizadas."""
    try:
        if extensao == 'csv':
            df = pd.read_csv(arquivo, sep=';', encoding='utf-8')
        elif extensao in ['xls', 'xlsx']:
            df = pd.read_excel(arquivo, engine='openpyxl')
        else:
            return None
        
        df.columns = normalizar_colunas(df.columns)
        return df
    except Exception as e:
        return None

def exportar_excel(df: pd.DataFrame) -> bytes:
    """Recebe um DataFrame e gera um ficheiro Excel (.xlsx) em memória."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Exportação')
    return output.getvalue()

def exportar_csv(df: pd.DataFrame) -> str:
    """Recebe um DataFrame e gera uma string em formato CSV compatível com o Excel padrão (separador ;)."""
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig')