# Тип репозитория

**Тип**: `Downstream/instrument`
**Система (SoI)**: Созидатель
**Содержание**: code
**Для кого**: personal
**Source-of-truth**: no

## Upstream dependencies

- [aisystant/PACK-personal](https://github.com/aisystant/PACK-personal) — source-of-truth области созидателя

## Downstream outputs

- Структурированный индекс персональных знаний
- Скрипты нормализации и поиска
- Публичные посты и заготовки для клуба (`posts/`)

## Non-goals

- НЕ является source-of-truth предметной области
- НЕ содержит формализованных знаний домена (это Pack)

## Правило: публичные посты

Все публичные посты (и заготовки) хранятся в `posts/`.
Конвенция имён: `YYYY-MM-DD-english-name.md`.
Каждый пост ДОЛЖЕН содержать в frontmatter поле `source_knowledge` со ссылкой на source-of-truth (Pack или Framework), откуда взято знание.
