import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["timestamp", "texto_usuario", "plato", "calorias"]


def _get_sheet(sheet_id: str):
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id).sheet1


def init_sheet(sheet_id: str):
    """Escribe fila de encabezados si la hoja está vacía."""
    sheet = _get_sheet(sheet_id)
    if not sheet.get_all_values():
        sheet.append_row(HEADERS)


def append_entry(sheet_id: str, texto: str, plato: str, calorias: int):
    """Agrega una fila con timestamp actual."""
    sheet = _get_sheet(sheet_id)
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    sheet.append_row([ts, texto, plato, str(calorias)])


def get_daily_total(sheet_id: str) -> int:
    """Suma las calorías registradas hoy para este usuario."""
    sheet = _get_sheet(sheet_id)
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        return 0
    today = datetime.now().strftime("%d/%m/%Y")
    total = 0
    for row in rows[1:]:  # saltar encabezados
        if len(row) >= 4 and row[0].startswith(today):
            try:
                total += int(row[3])
            except ValueError:
                pass
    return total


def get_last_entry(sheet_id: str) -> dict | None:
    """Retorna la última fila como dict o None si no hay entradas."""
    sheet = _get_sheet(sheet_id)
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


def update_last_entry(sheet_id: str, plato: str, calorias: int):
    """Actualiza plato y calorías de la última fila."""
    entry = get_last_entry(sheet_id)
    if not entry:
        return
    sheet = _get_sheet(sheet_id)
    row = entry["row_index"]
    sheet.update_cell(row, 3, plato)
    sheet.update_cell(row, 4, str(calorias))
