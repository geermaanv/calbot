import os
import json
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["timestamp", "texto_usuario", "plato", "calorias"]
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")


def _get_client():
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def _get_tab(tab_name: str):
    gc = _get_client()
    spreadsheet = gc.open_by_key(SHEET_ID)
    try:
        return spreadsheet.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=4)
        sheet.append_row(HEADERS)
        return sheet


def create_user_tab(tab_name: str):
    """Crea la pestaña del usuario si no existe."""
    _get_tab(tab_name)


def append_entry(tab_name: str, texto: str, plato: str, calorias: int, fecha: str | None = None):
    sheet = _get_tab(tab_name)
    date_part = fecha if fecha else datetime.now().strftime("%d/%m/%Y")
    ts = f"{date_part} {datetime.now().strftime('%H:%M')}"
    sheet.append_row([ts, texto, plato, str(calorias)])


def get_daily_total(tab_name: str, fecha: str | None = None) -> int:
    sheet = _get_tab(tab_name)
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        return 0
    day = fecha if fecha else datetime.now().strftime("%d/%m/%Y")
    total = 0
    for row in rows[1:]:
        if len(row) >= 4 and row[0].startswith(day):
            try:
                total += int(row[3])
            except ValueError:
                pass
    return total


def get_last_entry(tab_name: str) -> dict | None:
    sheet = _get_tab(tab_name)
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        return None
    last = rows[-1]
    if len(last) < 4:
        return None
    return {
        "timestamp": last[0],
        "texto_usuario": last[1],
        "plato": last[2],
        "calorias": last[3],
        "row_index": len(rows),
    }


def get_resumen(tab_name: str) -> dict:
    """Retorna totales de hoy, esta semana y este mes."""
    sheet = _get_tab(tab_name)
    rows = sheet.get_all_values()
    hoy = datetime.now()
    hoy_str = hoy.strftime("%d/%m/%Y")
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    totales = {"hoy": 0, "semana": 0, "mes": 0}
    dias_semana: set = set()
    dias_mes: set = set()

    for row in rows[1:]:
        if len(row) < 4:
            continue
        try:
            fecha = datetime.strptime(row[0][:10], "%d/%m/%Y")
            cals = int(row[3])
        except (ValueError, IndexError):
            continue
        if row[0].startswith(hoy_str):
            totales["hoy"] += cals
        if fecha >= inicio_semana:
            totales["semana"] += cals
            dias_semana.add(row[0][:10])
        if fecha >= inicio_mes:
            totales["mes"] += cals
            dias_mes.add(row[0][:10])

    totales["dias_semana"] = len(dias_semana)
    totales["dias_mes"] = len(dias_mes)
    return totales


def update_last_entry(tab_name: str, plato: str, calorias: int):
    sheet = _get_tab(tab_name)
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        return
    row = len(rows)
    sheet.update_cell(row, 3, plato)
    sheet.update_cell(row, 4, str(calorias))
