"""Конфигурация парсера Kwork."""

BASE_URL = "https://kwork.ru"
PROJECTS_URL = f"{BASE_URL}/projects"

# Категории: c=41 — Программирование и IT
CATEGORIES = {
    41: "Программирование и IT",
    11: "Дизайн",
    17: "Аудио и видео",
}

# Задержки между запросами (сек)
DELAY_MIN = 2
DELAY_MAX = 5

# User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# Красные флаги в описании заказа (lower case)
RED_FLAGS = [
    "взлом", "hack", "хак", "обход", "обойти", "ban", "бан",
    "спам", "рассылка", "ферма", "фейк", "подделка",
    "пароль", "password", "логин", "login", "credentials",
    "ddos", "ботнет", "botnet", "фишинг", "phishing",
    "нарушение", "tos", "terms of service",
    "whatsapp рассылка", "ватсап рассылка", "sms рассылка",
    "накрутка", "накрутить", "likes", "подписчики",
    "парсер личных данных", "персональные данные", "gdpr",
]

# Зелёные флаги — соответствие вашим скиллам
GREEN_FLAGS = [
    "python", "django", "flask", "fastapi", "парсер", "parser",
    "бот", "bot", "telegram", "телеграм", "api", "rest api",
    "sqlite", "postgresql", "база данных", "backend", "бэкенд",
    "тестирование", "pytest", "unittest", "django testing",
    "html", "css", "bootstrap", "шаблон", "template",
    "docker", "git", "github", "deploy", "deployment",
]
