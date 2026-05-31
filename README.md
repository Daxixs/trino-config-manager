# Trino Config Manager

Веб-сервис для управления конфигурацией [Trino](https://trino.io) через удобный браузерный интерфейс.

## Что умеет

- **Каталоги (Catalogs)** — создание, редактирование, удаление файлов `catalog/*.properties` с валидацией коннекторов (PostgreSQL, MySQL, Hive, Iceberg и др.)
- **Роли и доступ** — редактирование `access-control/rules.json` с проверкой структуры правил
- **Resource Groups** — управление `resource_groups.json` (квоты CPU/памяти/параллелизма)
- **Конфигурация Trino** — редактирование `config.properties`, `jvm.config`, `node.properties`
- **Reload** — отправка сигнала Trino перечитать конфиги одной кнопкой
- **Валидация** — все файлы проверяются до сохранения, ошибки показываются в UI
- **Бэкапы** — перед каждым сохранением создаётся `.bak` файл

## Быстрый старт

```bash
# 1. Клонировать
git clone https://github.com/<YOUR_USERNAME>/trino-config-manager
cd trino-config-manager

# 2. Создать .env
cp .env.example .env
# Отредактировать переменные под свою среду

# 3. Создать папку для конфигов
mkdir -p trino_configs_local/catalog

# 4. Запустить
docker-compose up --build

# 5. Открыть браузер
open http://localhost:8000
# Логин: admin / admin (меняется в .env)
```

## Локальная разработка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Запуск с автоперезагрузкой
uvicorn app.main:app --reload --port 8000
```

## Тесты

```bash
pytest tests/ -v
```

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `TRINO_CONFIG_DIR` | `/etc/trino` | Директория конфигов Trino |
| `TRINO_CATALOG_DIR` | `/etc/trino/catalog` | Директория каталогов |
| `TRINO_RELOAD_COMMAND` | `kill -HUP ...` | Команда для перезагрузки |
| `ADMIN_USERNAME` | `admin` | Логин в веб-интерфейс |
| `ADMIN_PASSWORD` | `admin` | Пароль в веб-интерфейс |
| `SECRET_KEY` | — | Секрет для сессий (обязательно сменить!) |
| `TRINO_HOST` | `localhost` | Хост Trino для проверки статуса |
| `TRINO_PORT` | `8080` | Порт Trino |

## Структура проекта

```
app/
├── main.py                  # FastAPI entrypoint, auth middleware
├── config.py                # Настройки из .env
├── routers/
│   ├── catalogs.py          # CRUD для catalog/*.properties
│   ├── roles.py             # Ролевая система (rules.json)
│   ├── resource_groups.py   # Квоты (resource_groups.json)
│   ├── trino_config.py      # config.properties, jvm.config, node.properties
│   └── reload.py            # Reload Trino + health check
├── validators/
│   ├── catalog_validator.py
│   ├── role_validator.py
│   ├── resource_group_validator.py
│   └── config_validator.py
├── services/
│   ├── file_service.py      # Чтение/запись/бэкап файлов
│   └── trino_service.py     # Reload + health check
└── templates/               # Jinja2 HTML (тёмная тема)
```

## Лицензия

MIT
