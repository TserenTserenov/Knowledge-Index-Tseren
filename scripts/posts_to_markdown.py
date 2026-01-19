#!/usr/bin/env python3
"""
Скрипт для конвертации постов из user_archive.csv в отдельные Markdown файлы.

Использование:
    python scripts/posts_to_markdown.py
"""

import csv
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from markdownify import markdownify as md


def clean_filename(title: str, max_length: int = 50) -> str:
    """Создаёт безопасное имя файла из заголовка."""
    # Транслитерация кириллицы
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    result = ''
    for char in title:
        result += translit_map.get(char, char)

    # Удаляем всё кроме букв, цифр, пробелов и дефисов
    result = re.sub(r'[^\w\s-]', '', result)
    # Заменяем пробелы на дефисы
    result = re.sub(r'\s+', '-', result)
    # Убираем множественные дефисы
    result = re.sub(r'-+', '-', result)
    # Обрезаем
    result = result[:max_length].strip('-')

    return result.lower() or 'untitled'


def clean_html_content(html: str) -> str:
    """Очищает HTML от WordPress комментариев и лишних тегов."""
    # Удаляем WordPress комментарии
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # Удаляем пустые параграфы
    html = re.sub(r'<p>\s*</p>', '', html)
    return html


def html_to_markdown(html: str) -> str:
    """Конвертирует HTML в Markdown."""
    html = clean_html_content(html)

    # Конвертируем в Markdown
    markdown = md(html, heading_style='ATX', bullets='-')

    # Очищаем результат
    # Удаляем множественные пустые строки
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    # Удаляем пробелы в конце строк
    markdown = '\n'.join(line.rstrip() for line in markdown.split('\n'))

    return markdown.strip()


def parse_date(date_str: str) -> str:
    """Парсит дату из CSV и возвращает форматированную строку."""
    try:
        # Формат: 2020-05-31T13:53:27.000Z
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str[:10] if len(date_str) >= 10 else 'unknown'


def main():
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / 'data' / 'csv' / 'user_archive.csv'
    docs_dir = script_dir / 'docs'

    # Очищаем папку docs (кроме example.md и test.md)
    for f in docs_dir.glob('*.md'):
        if f.name not in ['example.md', 'test.md']:
            f.unlink()

    # Создаём папку если нет
    docs_dir.mkdir(exist_ok=True)

    # Словарь для отслеживания тем (группируем посты по теме)
    topics = {}

    print(f"Читаю {csv_path}...")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Пропускаем личные сообщения
            if row.get('is_pm', '').lower() in ['да', 'yes', 'true', '1']:
                continue

            title = row.get('topic_title', '').strip()
            if not title:
                continue

            content = row.get('post_raw', '').strip()
            if not content:
                continue

            category = row.get('categories', '').strip()
            url = row.get('url', '').strip()
            created_at = row.get('created_at', '').strip()

            # Используем URL как уникальный идентификатор
            post_id = hashlib.md5(url.encode()).hexdigest()[:8] if url else hashlib.md5(content[:100].encode()).hexdigest()[:8]

            # Группируем по теме
            if title not in topics:
                topics[title] = {
                    'title': title,
                    'category': category,
                    'url': url,
                    'created_at': created_at,
                    'posts': []
                }

            topics[title]['posts'].append({
                'content': content,
                'url': url,
                'created_at': created_at
            })

    print(f"Найдено {len(topics)} уникальных тем")

    # Создаём файлы
    created = 0
    for title, topic_data in topics.items():
        date_str = parse_date(topic_data['created_at'])
        filename = f"{date_str}-{clean_filename(title)}.md"
        filepath = docs_dir / filename

        # Объединяем все посты темы
        posts = topic_data['posts']

        # Собираем контент
        md_content = f"# {title}\n\n"
        md_content += f"**Категория:** {topic_data['category']}\n\n"
        md_content += f"**Дата:** {date_str}\n\n"
        if topic_data['url']:
            md_content += f"**URL:** {topic_data['url']}\n\n"
        md_content += "---\n\n"

        for i, post in enumerate(posts):
            content_md = html_to_markdown(post['content'])
            md_content += content_md
            if i < len(posts) - 1:
                md_content += "\n\n---\n\n"

        # Записываем файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        created += 1
        if created % 100 == 0:
            print(f"Создано {created} файлов...")

    print(f"\nГотово! Создано {created} файлов в {docs_dir}")


if __name__ == '__main__':
    main()
