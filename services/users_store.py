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
        return {"approved": [], "pending": []}
    with open(USERS_FILE) as f:
        return json.load(f)


def _save(data: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _migrate(data: dict) -> dict:
    """Migra formato viejo {id: sheet_id} al nuevo formato de lista."""
    if isinstance(data.get("approved"), dict):
        data["approved"] = list(data["approved"].keys())
    if isinstance(data.get("pending"), dict):
        data["pending"] = list(data["pending"].keys())
    return data


def is_approved(user_id: int) -> bool:
    with _lock:
        data = _migrate(_load())
        return str(user_id) in data["approved"]


def is_pending(user_id: int) -> bool:
    with _lock:
        data = _migrate(_load())
        return str(user_id) in data["pending"]


def add_pending(user_id: int):
    with _lock:
        data = _migrate(_load())
        if str(user_id) not in data["pending"]:
            data["pending"].append(str(user_id))
        _save(data)


def approve(user_id: int) -> bool:
    with _lock:
        data = _migrate(_load())
        uid = str(user_id)
        if uid in data["pending"]:
            data["pending"].remove(uid)
        if uid not in data["approved"]:
            data["approved"].append(uid)
        _save(data)
        return True


def reject(user_id: int) -> bool:
    with _lock:
        data = _migrate(_load())
        uid = str(user_id)
        if uid not in data["pending"]:
            return False
        data["pending"].remove(uid)
        _save(data)
        return True


def get_approved_ids() -> list[int]:
    with _lock:
        data = _migrate(_load())
        return [int(k) for k in data["approved"]]


def reminders_on(user_id: int) -> bool:
    with _lock:
        data = _migrate(_load())
        return str(user_id) in data.get("reminders", [])


def set_reminders(user_id: int, active: bool):
    with _lock:
        data = _migrate(_load())
        reminders = data.setdefault("reminders", [])
        uid = str(user_id)
        if active and uid not in reminders:
            reminders.append(uid)
        elif not active and uid in reminders:
            reminders.remove(uid)
        _save(data)


def get_reminder_ids() -> list[int]:
    with _lock:
        data = _migrate(_load())
        return [int(k) for k in data.get("reminders", [])]
