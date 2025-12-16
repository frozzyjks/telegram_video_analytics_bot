# Telegram-бот для аналитики по видео

Telegram-бот, который принимает вопросы на естественном русском языке и
возвращает числовые аналитические метрики по данным о видео-креаторах.

Бот работает поверх PostgreSQL и использует LLM для преобразования текстовых
запросов в структурированные обращения к базе данных.

---

## Стек технологий

- Python 3.10+
- PostgreSQL
- aiogram (Telegram Bot API)
- OpenAI API
- psycopg2
- python-dateutil

---

## Структура проекта

.
├── app/
│ ├── bot.py # Telegram-бот
│ ├── parser.py # Разбор естественного языка
│ ├── llm.py # Взаимодействие с LLM
│ ├── queries.py # SQL-логика
│ ├── db.py # Подключение к PostgreSQL
│ └── config.py # Переменные окружения
│
├── scripts/
│ └── load_json.py # Загрузка данных из JSON в БД
│
├── schema.sql # Схема базы данных
├── requirements.txt
└── README.md

---

## Схема данных

### Таблица `videos`
Итоговая статистика по каждому видео.

- `id` — UUID видео  
- `creator_id` — UUID креатора  
- `video_created_at` — дата публикации  
- `views_count`  
- `likes_count`  
- `comments_count`  
- `reports_count`  
- `created_at`, `updated_at`

### Таблица `video_snapshots`
Почасовые снапшоты статистики по видео.

- `id` — UUID снапшота  
- `video_id` — ссылка на `videos.id`  
- текущие значения:  
  `views_count`, `likes_count`, `comments_count`, `reports_count`
- приращения:  
  `delta_views_count`, `delta_likes_count`, `delta_comments_count`, `delta_reports_count`
- `created_at` — время замера  
- `updated_at`

---

## Подготовка базы данных

1. Создать базу данных PostgreSQL
2. Применить схему:

```bash
psql -d your_database_name -f schema.sql
```
3. Загрузить данные из JSON:

```bash
python scripts/load_json.py --db-name your_database_name --json-path path_to_your_json
```
---
## Переменные окружения
Перед запуском необходимо задать:

BOT_TOKEN=telegram_bot_token
OPENAI_API_KEY=openai_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

## Запуск бота

```bash
pip install -r requirements.txt
python app/bot.py
```