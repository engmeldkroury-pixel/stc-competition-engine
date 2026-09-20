import pytest

from app import storage


@pytest.fixture(autouse=True)
def isolated_stc_db(tmp_path, monkeypatch):
    db_path = tmp_path / "stc-test.db"
    monkeypatch.setattr(storage, "DB_PATH", db_path)
    storage.init_db()
    yield
