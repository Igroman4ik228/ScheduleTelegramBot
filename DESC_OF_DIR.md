
### Корневой каталог проекта:
- `.venv/` – виртуальная среда Python.
- `logs/` – папка для хранения логов.
- `src/` – основная папка с исходным кодом проекта.


### Папка `src/`:

#### ABC (pack)

**observer_pack**:
- `models.py` – модели для Observer pattern (наблюдатель).

**background_service_pack:**
- `builder.py`, `manager.py` – классы для управления и конфигурации фоновых сервисов.
- `models.py` – модели данных.

#### Business Logic

`main.py` - точка входа проекта, конфигурация сервисов через DI

**bot:**
- *filters: файлы `admin.py`, `number.py` – фильтры для работы с ботом.
- *handlers:
	- *users: `start.py` – обработчики команд пользователя.
- *keyboards*: папки с клавиатурами для бота.
- *middlewares: middleware для бота.
- `bot.py` – основной файл для запуска бота.

**parser_service**:
- Различные модули (`parser.py`, `lesson.py`, и др.) для работы с парсингом расписания и билдом нового.

**ad_service:**
- `ad_sender.py` – отвечает за отправку рекламных сообщений.
- `models.py` – содержит модели данных для этого сервиса.

**notify_service**:
- `notify.py` – сервис уведомлений.

**database:**
- `db.py` – взаимодействие с базой данных.
- `redis_cache.py` – работа с кэшем Redis.
- *migrations – для управления миграциями базы данных.
- *models*:
	- `base.py`, `departments.py`, `groups.py`, `users.py`, и др. – модели данных для различных сущностей (расписания, группы, пользователи).
- *repositories*:
    - Репозитории для доступа к данным, сгруппированные по сущностям

**loader:**
- `schedule_loader.py` – None

**utils**:
- `config.py`, `constants.py`, и другие утилиты, связанные с проектом.

**Конфигурационные файлы проекта** (например, `.env`, `Dockerfile`, `Makefile`, `poetry.lock`).
