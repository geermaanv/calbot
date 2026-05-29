import pytest
from unittest.mock import patch
from services.ai_client import _parse_json, classify, estimate_calories


def test_parse_json_clean():
    result = _parse_json('{"plato": "milanesa", "calorias": 500, "fecha": "28/05/2026"}')
    assert result == {"plato": "milanesa", "calorias": 500, "fecha": "28/05/2026"}


def test_parse_json_wrapped_in_markdown():
    result = _parse_json('```json\n{"plato": "sopa", "calorias": 200}\n```')
    assert result["plato"] == "sopa"
    assert result["calorias"] == 200


def test_parse_json_with_extra_text():
    result = _parse_json('Aquí está el resultado: {"plato": "asado", "calorias": 800}')
    assert result["plato"] == "asado"


def test_parse_json_invalid_raises():
    with pytest.raises(Exception):
        _parse_json("esto no es json")


def test_classify_comida():
    with patch("services.ai_client._chat", return_value="comida"):
        assert classify("almorcé milanesa") == "comida"


def test_classify_correccion():
    with patch("services.ai_client._chat", return_value="correccion"):
        assert classify("en realidad era pollo") == "correccion"


def test_classify_otro():
    with patch("services.ai_client._chat", return_value="otro"):
        assert classify("hola cómo estás") == "otro"


def test_classify_normaliza_mayusculas():
    with patch("services.ai_client._chat", return_value="COMIDA"):
        assert classify("almorcé algo") == "comida"


def test_estimate_calories_devuelve_dict():
    mock_response = '{"plato": "empanadas", "calorias": 300, "fecha": "28/05/2026"}'
    with patch("services.ai_client._chat", return_value=mock_response):
        result = estimate_calories("comí empanadas")
    assert result["plato"] == "empanadas"
    assert result["calorias"] == 300
    assert "fecha" in result
