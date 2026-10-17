# Kwork Parser

Парсер заказов с Kwork для личного использования. Собирает заказы из категории "Программирование и IT", анализирует их на соответствие навыкам (Python, Django, боты) и выявляет подозрительные заказы (спам, обход защит).

## Установка

```bash

# Виртуальное окружение
python -m venv venv
source venv/Scripts/activate  # Windows

# Зависимости
pip install -r requirements.txt

Использование

python parser.py
#  Парсит 2 страницы категории IT (41), сохраняет в kwork.db.
python viewer.py best

Просмотр результатов

# Новые заказы
python viewer.py new
# Топ по скорингу
python viewer.py best
# Пометить статус
python viewer.py status <project_id> <new|viewed|rejected|accepted>

Скоринг

Зелёные флаги (+10): python, django, бот, telegram, api, парсер...
Красные флаги (-30): обход, спам, взлом, ферма, накрутка...
Рекомендация: брать заказы со скором >= 20, без красных флагов, < 20 откликов.

Структура

kwork-parser/
├── config.py          # Настройки, флаги, категории
├── database.py          # SQLite: таблицы, CRUD
├── parser.py            # Playwright + window.stateData
├── viewer.py            # Просмотр и управление
├── requirements.txt     # Зависимости
└── kwork.db             # База данных (создаётся автоматически)

Планируется

[ ] Telegram-уведомления о хороших заказах
[ ] Автозапуск по расписанию (Task Scheduler)
[ ] Дополнительные категории
# kwork-parser
