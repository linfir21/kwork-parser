"""Работа с SQLite для хранения заказов Kwork."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "kwork.db"


def init_db():
    """Создаёт таблицы, если их нет."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            project_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            budget TEXT,
            deadline TEXT,
            category TEXT,
            category_id INTEGER,
            url TEXT,
            responses_count INTEGER DEFAULT 0,
            customer_name TEXT,
            customer_rating REAL,
            status TEXT DEFAULT 'new',
            red_flags TEXT,
            green_flags TEXT,
            score INTEGER DEFAULT 0,
            parsed_at TEXT,
            updated_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parsing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            page INTEGER,
            projects_found INTEGER,
            projects_new INTEGER,
            error TEXT,
            timestamp TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def insert_or_update_project(project: dict) -> bool:
    """
    Вставляет новый заказ или обновляет ВСЕ поля существующего.
    Возвращает True, если заказ был новым.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute(
        "SELECT id FROM projects WHERE project_id = ?",
        (project["project_id"],)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Обновляем ВСЕ поля — перепарсили, данные могли измениться
        cursor.execute("""
            UPDATE projects SET
                title = ?,
                description = ?,
                budget = ?,
                deadline = ?,
                category = ?,
                category_id = ?,
                url = ?,
                responses_count = ?,
                customer_name = ?,
                customer_rating = ?,
                red_flags = ?,
                green_flags = ?,
                score = ?,
                updated_at = ?
            WHERE project_id = ?
        """, (
            project.get("title", ""),
            project.get("description", ""),
            project.get("budget", ""),
            project.get("deadline", ""),
            project.get("category", ""),
            project.get("category_id", 0),
            project.get("url", ""),
            project.get("responses_count", 0),
            project.get("customer_name", ""),
            project.get("customer_rating", 0.0),
            project.get("red_flags", "[]"),
            project.get("green_flags", "[]"),
            project.get("score", 0),
            now,
            project["project_id"],
        ))
        is_new = False
    else:
        cursor.execute("""
            INSERT INTO projects (
                project_id, title, description, budget, deadline,
                category, category_id, url, responses_count,
                customer_name, customer_rating, status,
                red_flags, green_flags, score, parsed_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project["project_id"],
            project.get("title", ""),
            project.get("description", ""),
            project.get("budget", ""),
            project.get("deadline", ""),
            project.get("category", ""),
            project.get("category_id", 0),
            project.get("url", ""),
            project.get("responses_count", 0),
            project.get("customer_name", ""),
            project.get("customer_rating", 0.0),
            project.get("status", "new"),
            project.get("red_flags", "[]"),
            project.get("green_flags", "[]"),
            project.get("score", 0),
            now,
            now,
        ))
        is_new = True
    
    conn.commit()
    conn.close()
    return is_new


def get_projects(status: str = None, limit: int = 50) -> list:
    """Возвращает заказы из БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute(
            "SELECT * FROM projects WHERE status = ? ORDER BY score DESC, parsed_at DESC LIMIT ?",
            (status, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM projects ORDER BY score DESC, parsed_at DESC LIMIT ?",
            (limit,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_status(project_id: str, status: str):
    """Обновляет статус заказа."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE projects SET status = ?, updated_at = ? WHERE project_id = ?",
        (status, datetime.now().isoformat(), project_id)
    )
    conn.commit()
    conn.close()


def log_parsing(category_id: int, page: int, found: int, new_count: int, error: str = None):
    """Логирует попытку парсинга."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO parsing_log (category_id, page, projects_found, projects_new, error, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (category_id, page, found, new_count, error, datetime.now().isoformat()))
    conn.commit()
    conn.close()
