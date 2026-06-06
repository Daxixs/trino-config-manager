import aiofiles
import shutil
from pathlib import Path
from datetime import datetime

from app.config import settings


class FileService:
    """Все операции чтения/записи конфигов Trino."""

    @staticmethod
    async def read_file(path: Path) -> str:
        if not path.exists():
            return ""
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            return await f.read()

    @staticmethod
    async def write_file(path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)

        backup_path = None

        if path.exists():
            backup_path = path.with_suffix(
                f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(path, backup_path)

        async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
            await f.write(content)

        return backup_path

    @staticmethod
    def list_catalogs() -> list[str]:
        catalog_dir = settings.TRINO_CATALOG_DIR
        if not catalog_dir.exists():
            return []
        return sorted([f.stem for f in catalog_dir.glob("*.properties")])

    @staticmethod
    async def delete_file(path: Path) -> None:
        if path.exists():
            backup_path = path.with_suffix(
                f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}.deleted"
            )
            shutil.copy2(path, backup_path)
            path.unlink()

    @staticmethod
    async def delete_catalog(name: str) -> bool:
        path = settings.TRINO_CATALOG_DIR / f"{name}.properties"

        if not path.exists():
            return False

        await FileService.delete_file(path)
        return True

    @staticmethod
    def list_backups(path: Path) -> list[dict]:
        pattern = f"{path.stem}.bak.*"

        backups = []

        for p in sorted(path.parent.glob(pattern)):
            backups.append(
                {
                    "name": p.name,
                    "path": str(p),
                }
            )

        return backups
