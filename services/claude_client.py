import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

CLASSIFY_PROMPT = """Clasificá el siguiente mensaje en una de estas categorías:
- "comida": el usuario describe algo que comió o va a comer
- "correccion": el usuario quiere modificar su último registro (frases como "en realidad", "me equivoqué", "era", "fue", "corregí", "modificá")
- "otro": cualquier otra cosa
Respondé ÚNICAMENTE con una de estas tres palabras, sin texto adicional."""

CALORIE_PROMPT = """Sos un nutricionista experto en cocina argentina y latinoamericana.
El usuario describe lo que comió en español rioplatense.
Estimá las calorías totales y respondé ÚNICAMENTE con este JSON, sin texto adicional:
{"plato": "<nombre breve del plato principal>", "calorias": <número entero>}"""

CORRECTION_PROMPT = """El usuario registró esta comida: {entrada_original}
Ahora indica esta corrección: {mensaje_usuario}
Devolvé el registro corregido ÚNICAMENTE con este JSON, sin texto adicional:
{"plato": "<nombre breve corregido>", "calorias": <número entero>}"""


def classify(text: str) -> str:
    """Retorna 'comida', 'correccion' o 'otro'."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=10,
        system=CLASSIFY_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].text.strip().lower()


def estimate_calories(text: str) -> dict:
    """Retorna {'plato': str, 'calorias': int} o lanza excepción."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=60,
        system=CALORIE_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    return json.loads(response.content[0].text.strip())


def correct_entry(entrada_original: str, mensaje_usuario: str) -> dict:
    """Retorna {'plato': str, 'calorias': int} corregido o lanza excepción."""
    system = CORRECTION_PROMPT.format(
        entrada_original=entrada_original,
        mensaje_usuario=mensaje_usuario,
    )
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=60,
        system=system,
        messages=[{"role": "user", "content": mensaje_usuario}],
    )
    return json.loads(response.content[0].text.strip())
