# Временный дебаг-скрипт, сохраните как debug.py и запустите
import requests
from bs4 import BeautifulSoup
from config import HEADERS

url = "https://kwork.ru/projects?c=41&page=1"
response = requests.get(url, headers=HEADERS, timeout=20)
soup = BeautifulSoup(response.text, "html.parser")

# Все div с class
divs = soup.find_all("div", class_=True)
classes = set()
for d in divs:
    classes.update(d.get("class", []))

print("Все классы div на странице:")
for c in sorted(classes):
    print(f"  {c}")

# Попробуем найти ссылки на /projects/
links = soup.find_all("a", href=lambda x: x and "/projects/" in x)
print(f"\nНайдено ссылок на проекты: {len(links)}")
for link in links[:5]:
    print(f"  href={link.get('href')}  text={link.get_text(strip=True)[:60]}")
