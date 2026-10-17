"""Парсер заказов с Kwork через Playwright + window.stateData.

Данные заказов Kwork встраивает в JS-переменную window.stateData.wantsListData.
Это JSON с полями: id, name, description, priceLimit, max_days, user, timeLeft и т.д.
"""

import json
import random
import time

from playwright.sync_api import sync_playwright

from config import BASE_URL, CATEGORIES, DELAY_MIN, DELAY_MAX, RED_FLAGS, GREEN_FLAGS
from database import insert_or_update_project, log_parsing


def analyze_text(text: str) -> tuple:
    """Анализирует текст на красные и зелёные флаги."""
    text_lower = text.lower()
    red_found = [flag for flag in RED_FLAGS if flag in text_lower]
    green_found = [flag for flag in GREEN_FLAGS if flag in text_lower]
    score = len(green_found) * 10 - len(red_found) * 30
    return red_found, green_found, score


def extract_wants_from_page(page) -> list:
    """Извлекает заказы из window.stateData через Playwright."""
    try:
        page.wait_for_function(
            "() => window.stateData && window.stateData.wantsListData && window.stateData.wantsListData.wants",
            timeout=10000
        )
        
        wants_json = page.evaluate("""
            () => {
                const data = window.stateData.wantsListData.wants;
                return JSON.stringify(data);
            }
        """)
        
        return json.loads(wants_json)
    except Exception as e:
        print(f"Failed to extract wants from stateData: {e}")
        return []


def parse_want(want: dict, category_id: int, category_name: str) -> dict | None:
    """Преобразует сырые данные Kwork в наш формат."""
    try:
        project_id = str(want.get("id", ""))
        if not project_id:
            return None
        
        title = want.get("name", "").strip()
        description = want.get("description", "").strip()
        
        # Бюджет — priceLimit или possiblePriceLimit
        price_limit = want.get("priceLimit", "")
        possible_limit = want.get("possiblePriceLimit", "")
        
        budget = ""
        if price_limit and str(price_limit) not in ("", "0", "0.00", "None"):
            budget = f"{price_limit} ₽"
        elif possible_limit and str(possible_limit) not in ("", "0", "None"):
            budget = f"до {possible_limit} ₽"
        
        # Срок
        max_days = want.get("max_days", "")
        time_left = want.get("timeLeft", "")
        deadline = ""
        if max_days and str(max_days) not in ("", "0", "None"):
            deadline = f"{max_days} дн."
        if time_left and str(time_left) not in ("", "None"):
            if deadline:
                deadline += f" (осталось: {time_left})"
            else:
                deadline = f"осталось: {time_left}"
        
        # Отклики
        responses = want.get("kwork_count", 0)
        if not responses:
            responses = 0
        
        # Заказчик
        user = want.get("user", {})
        customer = ""
        if isinstance(user, dict):
            customer = user.get("username", "")
        
        # URL
        url = f"{BASE_URL}/projects/{project_id}"
        
        # Анализ текста
        full_text = f"{title} {description}"
        red, green, score = analyze_text(full_text)
        
        return {
            "project_id": project_id,
            "title": title,
            "description": description,
            "budget": budget,
            "deadline": deadline,
            "category": category_name,
            "category_id": category_id,
            "url": url,
            "responses_count": responses,
            "customer_name": customer,
            "customer_rating": 0.0,
            "red_flags": json.dumps(red, ensure_ascii=False),
            "green_flags": json.dumps(green, ensure_ascii=False),
            "score": score,
        }
    except Exception as e:
        print(f"Error parsing want: {e}")
        return None


def parse_page(category_id: int, page_num: int = 1) -> list:
    """Парсит одну страницу через Playwright + stateData."""
    category_name = CATEGORIES.get(category_id, "Unknown")
    url = f"{BASE_URL}/projects?c={category_id}&page={page_num}"
    
    print(f"Parsing {url}...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="ru-RU",
                timezone_id="Europe/Moscow",
            )
            
            page_obj = context.new_page()
            page_obj.goto(url, wait_until="networkidle", timeout=30000)
            
            page_obj.wait_for_selector(".want-card", timeout=10000)
            time.sleep(2)
            
            raw_wants = extract_wants_from_page(page_obj)
            browser.close()
    
    except Exception as e:
        print(f"Playwright error: {e}")
        log_parsing(category_id, page_num, 0, 0, str(e))
        return []
    
    print(f"Found {len(raw_wants)} wants in stateData")
    
    projects = []
    new_count = 0
    
    for want in raw_wants:
        project = parse_want(want, category_id, category_name)
        if project:
            is_new = insert_or_update_project(project)
            if is_new:
                new_count += 1
            projects.append(project)
    
    log_parsing(category_id, page_num, len(projects), new_count)
    print(f"Saved {len(projects)} projects ({new_count} new)")
    
    return projects


def parse_category(category_id: int, max_pages: int = 3):
    """Парсит категорию по страницам."""
    for page in range(1, max_pages + 1):
        parse_page(category_id, page)
        if page < max_pages:
            delay = random.uniform(DELAY_MIN, DELAY_MAX)
            print(f"Sleeping {delay:.1f}s...")
            time.sleep(delay)


def main():
    from database import init_db
    init_db()
    
    parse_category(41, max_pages=2)
    
    print("\nDone. Use: python viewer.py new")


if __name__ == "__main__":
    main()
