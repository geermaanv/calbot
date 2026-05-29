import json
import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture(autouse=True)
def tmp_users_file(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    import services.users_store as store
    monkeypatch.setattr(store, "USERS_FILE", users_file)
    yield users_file


from services.users_store import (
    approve, reject, is_approved, is_pending,
    add_pending, get_approved_ids, reminders_on, set_reminders, get_reminder_ids,
)


def test_usuario_nuevo_no_aprobado():
    assert not is_approved(123)


def test_approve_usuario():
    approve(123)
    assert is_approved(123)


def test_approve_idempotente():
    approve(123)
    approve(123)
    assert get_approved_ids().count(123) == 1


def test_add_pending_y_is_pending():
    add_pending(456)
    assert is_pending(456)


def test_approve_mueve_de_pending():
    add_pending(789)
    approve(789)
    assert is_approved(789)
    assert not is_pending(789)


def test_reject_elimina_pending():
    add_pending(111)
    result = reject(111)
    assert result is True
    assert not is_pending(111)


def test_reject_inexistente_retorna_false():
    assert reject(999) is False


def test_get_approved_ids():
    approve(1)
    approve(2)
    ids = get_approved_ids()
    assert 1 in ids
    assert 2 in ids


def test_reminders_apagados_por_defecto():
    approve(123)
    assert not reminders_on(123)


def test_set_reminders_activa():
    approve(123)
    set_reminders(123, True)
    assert reminders_on(123)


def test_set_reminders_desactiva():
    approve(123)
    set_reminders(123, True)
    set_reminders(123, False)
    assert not reminders_on(123)


def test_set_reminders_idempotente():
    approve(123)
    set_reminders(123, True)
    set_reminders(123, True)
    assert get_reminder_ids().count(123) == 1


def test_get_reminder_ids():
    approve(1)
    approve(2)
    set_reminders(1, True)
    ids = get_reminder_ids()
    assert 1 in ids
    assert 2 not in ids
