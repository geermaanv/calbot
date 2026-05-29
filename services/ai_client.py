import os
import json
import re
from openai import OpenAI

MODEL = "google/gemini-2.5-flash-lite"
_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        )
    return _client

CLASSIFY_PROMPT = """Clasificá el siguiente mensaje en una de estas categorías:
- "comida": el usuario describe algo que comió o va a comer
- "correccion": el usuario quiere modificar su último registro (frases como "en realidad", "me equivoqué", "era", "fue", "corregí", "modificá")
- "otro": cualquier otra cosa
Respondé ÚNICAMENTE con una de estas tres palabras, sin texto adicional."""

CALORIE_PROMPT = """Sos un nutricionista experto en cocina argentina y latinoamericana.
El usuario describe lo que comió en español rioplatense.
Hoy es {hoy}.
Si el mensaje menciona una fecha distinta (ayer, el lunes, 27/05, etc.), usala. Si no menciona fecha, usá hoy.
Estimá las calorías totales y respondé ÚNICAMENTE con este JSON, sin texto adicional:
{{"plato": "<nombre breve del plato principal>", "calorias": <número entero>, "fecha": "DD/MM/YYYY"}}"""


def _chat(system: str, user: str, max_tokens: int) -> str:
    response = _get_client().chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content.strip()


def classify(text: str) -> str:
    return _chat(CLASSIFY_PROMPT, text, 10).lower()


def _parse_json(text: str) -> dict:
    match = re.search(r'\{[^{}]+\}', text)
    if match:
        return json.loads(match.group())
    return json.loads(text)


_DIAS = {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
         "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"}


def estimate_calories(text: str) -> dict:
    from datetime import datetime
    now = datetime.now()
    dia_es = _DIAS[now.strftime("%A")]
    hoy = f"{now.strftime('%d/%m/%Y')} ({dia_es})"
    prompt = CALORIE_PROMPT.format(hoy=hoy)
    return _parse_json(_chat(prompt, text, 120))


def correct_entry(entrada_original: str, mensaje_usuario: str) -> dict:
    system = (
        f"El usuario registró esta comida: {entrada_original}\n"
        f"Ahora indica esta corrección: {mensaje_usuario}\n"
        "Devolvé el registro corregido ÚNICAMENTE con este JSON, sin texto adicional:\n"
        '{"plato": "<nombre breve corregido>", "calorias": <número entero>}'
    )
    return _parse_json(_chat(system, mensaje_usuario, 120))
