#!/usr/bin/env python3
"""
Скрипт для конвертации CSV файлов в Markdown таблицы.

Использование:
    python scripts/csv_to_markdown.py                    # Конвертирует все CSV из data/csv в docs/
    python scripts/csv_to_markdown.py --input badges.csv # Конвертирует только указанный файл
    python scripts/csv_to_markdown.py --limit 100        # Ограничить количество строк
"""

import csv
import os
import argparse
from pathlib import Path


def csv_to_markdown_table(csv_path: Path, limit: int = None) -> str:
    """Конвертирует CSV файл в Markdown таблицу."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return f"# {csv_path.stem}\n\n*Файл пустой*\n"

    headers = rows[0]
    data = rows[1:]

    if limit and len(data) > limit:
        data = data[:limit]
        truncated = True
    else:
        truncated = False

    # Создаём Markdown
    md = f"# {csv_path.stem.replace('_', ' ').title()}\n\n"
    md += f"*Источник: `{csv_path.name}`*\n\n"

    if not data:
        md += "*Нет данных*\n"
        return md

    # Заголовок таблицы
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    # Данные
    for row in data:
        # Экранируем | в данных и обрезаем длинные значения
        escaped_row = []
        for cell in row:
            cell = cell.replace("|", "\\|")
            if len(cell) > 50:
                cell = cell[:47] + "..."
            escaped_row.append(cell)

        # Дополняем строку если колонок меньше чем заголовков
        while len(escaped_row) < len(headers):
            escaped_row.append("")

        md += "| " + " | ".join(escaped_row[:len(headers)]) + " |\n"

    if truncated:
        md += f"\n*... показано первых {limit} записей*\n"

    md += f"\n*Всего записей: {len(rows) - 1}*\n"

    return md


def main():
    parser = argparse.ArgumentParser(description='Конвертация CSV в Markdown')
    parser.add_argument('--input', '-i', help='Имя конкретного CSV файла')
    parser.add_argument('--limit', '-l', type=int, default=100, help='Лимит строк (по умолчанию 100)')
    parser.add_argument('--no-limit', action='store_true', help='Без лимита строк')
    args = parser.parse_args()

    # Определяем пути
    script_dir = Path(__file__).parent.parent
    csv_dir = script_dir / 'data' / 'csv'
    docs_dir = script_dir / 'docs'

    # Создаём docs если нет
    docs_dir.mkdir(exist_ok=True)

    limit = None if args.no_limit else args.limit

    if args.input:
        csv_files = [csv_dir / args.input]
    else:
        csv_files = list(csv_dir.glob('*.csv'))

    for csv_file in csv_files:
        if not csv_file.exists():
            print(f"Файл не найден: {csv_file}")
            continue

        md_content = csv_to_markdown_table(csv_file, limit=limit)
        output_file = docs_dir / f"{csv_file.stem}.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Создан: {output_file}")


if __name__ == '__main__':
    main()
