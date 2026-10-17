"""Просмотр и анализ собранных заказов."""

import json
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from database import get_projects, update_status


def print_project(p: dict):
    """Красивый вывод одного заказа."""
    red = json.loads(p["red_flags"])
    green = json.loads(p["green_flags"])
    
    print("═" * 60)
    print(f"📌 {p['title']}")
    print(f"🔗 {p['url']}")
    print(f"💰 {p['budget']} | ⏰ {p['deadline']} | 📊 {p['responses_count']} откликов")
    print(f"🏷  Категория: {p['category']}")
    print(f"⭐ Скор: {p['score']} | Статус: {p['status']}")
    
    if green:
        print(f"🟢 Совпадения: {', '.join(green)}")
    if red:
        print(f"🔴 Красные флаги: {', '.join(red)}")
    
    if p["description"]:
        desc = p["description"][:200] + "..." if len(p["description"]) > 200 else p["description"]
        print(f"📝 {desc}")
    
    print()


def show_new():
    """Показывает новые заказы."""
    projects = get_projects(status="new")
    print(f"\n📋 Новых заказов: {len(projects)}\n")
    for p in projects:
        print_project(p)


def show_best():
    """Показывает лучшие по скорингу (кроме отклонённых)."""
    projects = [p for p in get_projects(limit=100) if p["status"] != "rejected"][:20]
    print("\n🏆 Топ-20 заказов по скорингу:\n")
    for p in projects:
        print_project(p)


def mark_status(project_id: str, status: str):
    """Меняет статус заказа."""
    update_status(project_id, status)
    print(f"Заказ {project_id} -> {status}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_new()
        print("Usage:")
        print("  python viewer.py new     — показать новые")
        print("  python viewer.py best    — показать топ по скору")
        print("  python viewer.py status <id> <new|viewed|rejected|accepted>")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "new":
        show_new()
    elif cmd == "best":
        show_best()
    elif cmd == "status" and len(sys.argv) == 4:
        mark_status(sys.argv[2], sys.argv[3])
    else:
        print("Unknown command")
