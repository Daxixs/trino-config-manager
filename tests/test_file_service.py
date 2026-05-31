import pytest
import asyncio
from pathlib import Path
from app.services.file_service import FileService


@pytest.mark.asyncio
async def test_write_and_read(tmp_path):
    path = tmp_path / "test.properties"
    await FileService.write_file(path, "connector.name=tpch\n")
    content = await FileService.read_file(path)
    assert content == "connector.name=tpch\n"


@pytest.mark.asyncio
async def test_write_creates_backup(tmp_path):
    path = tmp_path / "test.properties"
    await FileService.write_file(path, "version=1\n")
    backup = await FileService.write_file(path, "version=2\n")
    assert backup is not None
    assert backup.exists()
    content = await FileService.read_file(backup)
    assert "version=1" in content


@pytest.mark.asyncio
async def test_write_no_backup_for_new_file(tmp_path):
    path = tmp_path / "new.properties"
    backup = await FileService.write_file(path, "connector.name=tpch\n")
    assert backup is None


@pytest.mark.asyncio
async def test_read_nonexistent_returns_empty(tmp_path):
    path = tmp_path / "nonexistent.txt"
    content = await FileService.read_file(path)
    assert content == ""


@pytest.mark.asyncio
async def test_delete_catalog(tmp_path, monkeypatch):
    from app import config
    monkeypatch.setattr(config.settings, "TRINO_CATALOG_DIR", tmp_path)

    path = tmp_path / "mycat.properties"
    path.write_text("connector.name=tpch\n")

    result = await FileService.delete_catalog("mycat")
    assert result is True
    assert not path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_catalog(tmp_path, monkeypatch):
    from app import config
    monkeypatch.setattr(config.settings, "TRINO_CATALOG_DIR", tmp_path)
    result = await FileService.delete_catalog("doesnotexist")
    assert result is False


def test_list_catalogs(tmp_path, monkeypatch):
    from app import config
    monkeypatch.setattr(config.settings, "TRINO_CATALOG_DIR", tmp_path)

    (tmp_path / "pg.properties").write_text("connector.name=postgresql\n")
    (tmp_path / "hive.properties").write_text("connector.name=hive\n")

    catalogs = FileService.list_catalogs()
    assert sorted(catalogs) == ["hive", "pg"]


def test_list_catalogs_empty(tmp_path, monkeypatch):
    from app import config
    monkeypatch.setattr(config.settings, "TRINO_CATALOG_DIR", tmp_path)
    assert FileService.list_catalogs() == []


def test_list_backups(tmp_path):
    path = tmp_path / "test.properties"
    path.write_text("v1")
    bak1 = tmp_path / "test.bak.20240101_120000"
    bak2 = tmp_path / "test.bak.20240102_120000"
    bak1.write_text("old")
    bak2.write_text("older")

    backups = FileService.list_backups(path)
    assert len(backups) == 2
    assert all("bak" in b["name"] for b in backups)
