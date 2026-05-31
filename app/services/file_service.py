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
    async def write_file(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup_path = path.with_suffix(
                f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(path, backup_path)
        async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
            await f.write(content)

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
    def list_backups(path: Path) -> list[str]:
        pattern = f"{path.stem}.bak.*"
        return sorted([str(p.name) for p in path.parent.glob(pattern)])
