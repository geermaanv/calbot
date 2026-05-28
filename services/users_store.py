"""
Gestión de usuarios aprobados y pendientes en users.json.
Thread-safe para acceso concurrente del bot.
"""
import json
import threading
from pathlib import Path

USERS_FILE = Path("users.json")
_lock = threading.Lock()


def _load() -> dict:
    if not USERS_FILE.exists():
        return {"approved": {}, "pending": {}}
    with open(USERS_FILE) as f:
        return json.load(f)


def _save(data: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_sheet_id(user_id: int) -> str | None:
    with _lock:
        data = _load()
        return data["approved"].get(str(user_id))


def is_approved(user_id: int) -> bool:
    return get_sheet_id(user_id) is not None


def is_pending(user_id: int) -> bool:
    with _lock:
        data = _load()
        return str(user_id) in data["pending"]


def add_pending(user_id: int, sheet_id: str):
    with _lock:
        data = _load()
        data["pending"][str(user_id)] = sheet_id
        _save(data)


def approve(user_id: int) -> str | None:
    """Mueve usuario de pending a approved. Retorna sheet_id o None."""
    with _lock:
        data = _load()
        sheet_id = data["pending"].pop(str(user_id), None)
        if sheet_id:
            data["approved"][str(user_id)] = sheet_id
            _save(data)
        return sheet_id


def reject(user_id: int) -> bool:
    """Elimina usuario de pending. Retorna True si existía."""
    with _lock:
        data = _load()
        existed = str(user_id) in data["pending"]
        data["pending"].pop(str(user_id), None)
        _save(data)
        return existed


def get_approved_ids() -> list[int]:
    with _lock:
        data = _load()
        return [int(k) for k in data["approved"].keys()]
