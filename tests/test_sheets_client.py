from datetime import datetime
from unittest.mock import patch, MagicMock
from services.sheets_client import get_daily_total, get_last_entry, get_resumen


def _mock_sheet(rows):
    sheet = MagicMock()
    sheet.get_all_values.return_value = rows
    return sheet


def _patch_tab(rows):
    return patch("services.sheets_client._get_tab", return_value=_mock_sheet(rows))


HOY = datetime.now().strftime("%d/%m/%Y")


def test_get_daily_total_sin_registros():
    with _patch_tab([["timestamp", "texto", "plato", "calorias"]]):
        assert get_daily_total("user") == 0


def test_get_daily_total_solo_hoy():
    rows = [
        ["timestamp", "texto", "plato", "calorias"],
        [f"{HOY} 10:00", "desayuno", "tostadas", "300"],
        [f"{HOY} 14:00", "almuerzo", "milanesa", "700"],
    ]
    with _patch_tab(rows):
        assert get_daily_total("user") == 1000


def test_get_daily_total_ignora_otros_dias():
    rows = [
        ["timestamp", "texto", "plato", "calorias"],
        ["01/01/2026 10:00", "viejo", "algo", "999"],
        [f"{HOY} 12:00", "hoy", "ensalada", "200"],
    ]
    with _patch_tab(rows):
        assert get_daily_total("user") == 200


def test_get_daily_total_fecha_especifica():
    rows = [
        ["timestamp", "texto", "plato", "calorias"],
        ["27/05/2026 21:00", "cena ayer", "sopa", "400"],
        [f"{HOY} 10:00", "hoy", "café", "50"],
    ]
    with _patch_tab(rows):
        assert get_daily_total("user", "27/05/2026") == 400


def test_get_last_entry_sin_datos():
    with _patch_tab([["timestamp", "texto", "plato", "calorias"]]):
        assert get_last_entry("user") is None


def test_get_last_entry_retorna_ultima_fila():
    rows = [
        ["timestamp", "texto", "plato", "calorias"],
        [f"{HOY} 10:00", "desayuno tostadas", "tostadas", "300"],
        [f"{HOY} 14:00", "almuerzo milanesa", "milanesa", "700"],
    ]
    with _patch_tab(rows):
        entry = get_last_entry("user")
    assert entry["plato"] == "milanesa"
    assert entry["texto_usuario"] == "almuerzo milanesa"
    assert entry["row_index"] == 3


def test_get_resumen_totales():
    rows = [
        ["timestamp", "texto", "plato", "calorias"],
        [f"{HOY} 10:00", "d", "tostadas", "300"],
        [f"{HOY} 14:00", "a", "milanesa", "700"],
    ]
    with _patch_tab(rows):
        r = get_resumen("user")
    assert r["hoy"] == 1000
    assert r["semana"] >= 1000
    assert r["mes"] >= 1000
    assert r["dias_semana"] >= 1
    assert r["dias_mes"] >= 1


def test_get_resumen_ignora_filas_invalidas():
    rows = [
        ["timestamp", "texto", "plato", "calorias"],
        [f"{HOY} 10:00", "ok", "algo", "500"],
        ["fecha-invalida", "roto", "algo", "999"],
        [f"{HOY} 12:00", "ok2", "algo2", "no-numero"],
    ]
    with _patch_tab(rows):
        r = get_resumen("user")
    assert r["hoy"] == 500
