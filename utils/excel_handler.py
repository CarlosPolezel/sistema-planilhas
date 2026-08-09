import pandas as pd
import io

def exportar_excel(df: pd.DataFrame) -> bytes:
    """Recebe um DataFrame e gera um ficheiro Excel (.xlsx) em memória."""
    output = io.BytesIO()
    # openpyxl foi definido nos requirements para suportar o formato xlsx
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Exportação')
    return output.getvalue()

def exportar_csv(df: pd.DataFrame) -> str:
    """Recebe um DataFrame e gera uma string em formato CSV compatível com o Excel padrão (separador ;)."""
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig')