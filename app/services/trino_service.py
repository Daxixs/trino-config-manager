import asyncio

from app.config import settings


class TrinoService:

    @staticmethod
    async def reload_config() -> dict:
        """Отправляет команду Trino перечитать конфиги."""
        try:
            proc = await asyncio.create_subprocess_shell(
                settings.TRINO_RELOAD_COMMAND,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            return {
                "success": proc.returncode == 0,
                "output": stdout.decode().strip(),
                "error": stderr.decode().strip(),
                "returncode": proc.returncode,
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "output": "",
                "error": "Timeout: команда не завершилась за 30 секунд",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1,
            }

    @staticmethod
    async def check_health() -> bool:
        """Проверяет доступность Trino."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"http://{settings.TRINO_HOST}:{settings.TRINO_PORT}/v1/info",
                    timeout=5,
                )
                return r.status_code == 200
        except Exception:
            return False
