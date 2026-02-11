---
type: post
status: draft
created: 2026-02-10
updated: 2026-02-11
target: club
tags: [architecture, platform, layers, MCP, AI-systems, digital-twin]
source_knowledge: https://github.com/TserenTserenov/PACK-digital-platform/tree/main/pack/digital-platform
---

# Архитектура ИТ-платформы: 3 слоя, 4 характеристики и принцип отчуждаемости

---

## Зачем этот пост

У нас есть платформа. Бот, LMS, агенты, MCP-серверы, цифровой двойник. Но пока нет общей картины — как это всё связано и по каким правилам устроено.

Этот пост — описание архитектуры «как прозрачный ящик». Не маркетинг, не roadmap. Конструкция: из чего состоит, как взаимодействует, почему именно так.

Все описания — в Pack'е: [PACK-digital-platform/pack/digital-platform/](https://github.com/TserenTserenov/PACK-digital-platform/tree/main/pack/digital-platform). Это source-of-truth. Пост — обзор для навигации.

---

## 3 слоя платформы

```
┌─────────────────────────────────────────────────────────────┐
│  СЛОЙ 3: ИНТЕРФЕЙСЫ (тонкие клиенты)                        │
│  Telegram Bot │ Web LMS │ ChatGPT Apps │ Mobile │ API       │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  СЛОЙ 2: ОБРАБОТКА                                           │
│  ┌─────────────────────────┐  ┌───────────────────────────┐ │
│  │ Зона А: ИИ-системы      │◄►│ Зона Б: Детерминированные │ │
│  │ (LLM, stateless)        │  │ (код, stateful, MCP)      │ │
│  │ Стратег, Проводник,     │  │ Twin, Hub, CRM, LMS,      │ │
│  │ Консультант, KE, …      │  │ Биллинг, ORY, Event Bus,  │ │
│  └─────────────────────────┘  └───────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  СЛОЙ 1: ДАННЫЕ + ИНФРАСТРУКТУРА                             │
│  GitHub Repos │ PostgreSQL │ SurrealDB │ Embeddings │ Cache  │
└─────────────────────────────────────────────────────────────┘
```

ИИ-системы и детерминированные системы — **пиры** внутри слоя обработки (горизонтальное взаимодействие). Интерфейс не обращается к данным напрямую. ИИ-система не знает, через какой UI пришёл пользователь.

| Слой | Назначение | Характер | Примеры |
|------|------------|----------|---------|
| **3. Интерфейсы** | Точки входа для пользователей | Тонкие клиенты, без бизнес-логики | Telegram Bot, Web LMS, ChatGPT Apps |
| **2. Обработка** | Логика, принятие решений, доступ к данным | Две зоны-пира (ИИ + детерминированные) | Стратег, Проводник, Twin, Hub, MCP |
| **1. Данные** | Персистентность данных | Физическое хранение | GitHub, PostgreSQL, SurrealDB |

> Полное описание: [DP.ARCH.001 — Архитектура ИТ-платформы](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.ARCH.001-platform-architecture.md)

---

## Четыре архитектурные характеристики

Характеристика — не лозунг. Это измеряемое качество с конкретным индикатором.

### 1. Эволюционируемость

**Вопрос:** Можно ли добавить новый сервис, базу данных или MCP-сервер без изменения существующей структуры?

**Как обеспечиваем:**
- MCP-протокол стандартизирует интерфейс → новый источник = новый MCP, без изменения ИИ-систем
- MCP Registry (yaml) → добавление = строка в конфиге
- Event Bus → слабая связанность, новый потребитель не меняет продюсера
- ИИ-система = репо с config.yaml → новая система = новый репо

**Индикатор:** Количество шагов для добавления нового MCP-сервера. Целевое: ≤3.

### 2. Масштабируемость

**Вопрос:** Требует ли подключение нового пользователя изменений в архитектуре?

**Как обеспечиваем:**
- ИИ-системы stateless → горизонтальное масштабирование
- Интерфейсы — тонкие клиенты → не хранят состояние
- User-space изолирован → данные одного не влияют на другого
- MCP per-user → персональные данные разграничены на уровне протокола

### 3. Обучаемость

**Вопрос:** Улучшается ли качество решений платформы со временем без ручного вмешательства?

**Как обеспечиваем:**
- Capture-to-Pack фиксирует знания из каждой сессии → Pack обогащается → ИИ-системы получают лучший контекст
- Знание-Экстрактор повышает точность на основе ревью (feedback loop)
- Memory хранит операционный контекст → каждая следующая сессия эффективнее предыдущей

### 4. Генеративность

**Вопрос:** Может ли новый пользователь развернуть работающую систему из шаблона платформы за один сеанс?

**Как обеспечиваем:**
- **Общее знание** (Platform-space): Pack, SPF, FPF — структурированные знания, доступные всем
- **Шаблоны развёртывания**: Template-репо экзокортекса → fork & deploy → работающая система
- **Правила наследования**: пользователь строит User-space поверх Platform-space, не с нуля
- **Feedback loop**: captures пользователей обогащают общее знание → следующий стартует с лучшей базы

Платформа помогает людям быть созидателями — не просто предоставляет инструменты, а порождает новые автономные системы из своих знаний и шаблонов.

---

## Ключевые механизмы

### Цифровой двойник (слой 2, зона Б)

Единое хранилище состояния человека на платформе.

| Тип данных | Префикс | Что хранит |
|------------|---------|------------|
| События | E.* | Все действия (обучение, задания, активность) |
| Слоты | SLT.* | Время, выделенное на развитие |
| Рабочие продукты | W.* | Конспекты, модели, артефакты |
| Маршруты | ROUTE.* | Планы и шаги развития |
| Ступени | STAGE.* | Текущий уровень |
| Метрики | MET.* | Агрегированные показатели |

### MCP Registry (слой 2, зона Б)

Три категории MCP-серверов:

| Категория | Характер | Примеры | Доступ |
|-----------|----------|---------|--------|
| **Базы знаний** | Read-only | guides-mcp, pack-MCP | Все пользователи |
| **Персональные данные** | Read/Write per user | digital-twin-mcp, user-repos | Только владелец |
| **Сервисы** | Read/Write | fsm-mcp, linear, github | По авторизации |

### Экзокортекс-интерфейс (слой 3 ↔ пользователь, слой 2 ↔ ИИ)

Модульный CLAUDE.md + Memory — конфигурация взаимодействия пользователя с ИИ-системами. Platform-space (общие модули, шаблоны) + user-space (персональный контекст, план, цели).

> Подробнее: [DP.EXOCORTEX.001 — Модульный экзокортекс](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.EXOCORTEX.001-modular-exocortex.md)

### Токены за активность

```
LMS/Клуб → Activity Hub → Proof-of-Impact → Token Economy
(события)   (сбор)        (ML-оценка)       (начисление)
```

Развитие выгодно. Действия фиксируются → оцениваются → конвертируются в токены.

---

## Принцип отчуждаемости

> Platform-space ≠ User-space

Каждый компонент платформы строится для передачи другим людям.

| Аспект | Platform-space | User-space |
|--------|---------------|------------|
| **Что** | Модули, шаблоны, правила, ИИ-системы | РП, репо, captures, предпочтения |
| **Кто обновляет** | Разработчики платформы | Пользователь + его ИИ-системы |
| **Переносимость** | Одинаково для всех | Уникально для каждого |

**Правило:** Если компонент содержит hardcoded данные конкретного пользователя — это нарушение отчуждаемости. Персонализация — через конфигурацию (user-space), не через код (platform-space).

---

## IPO: универсальный паттерн описания компонентов

Каждый компонент (ИИ-система, сервис, MCP) описывается единым паттерном:

```
ВХОДЫ (Inputs) → ОБРАБОТКА (Processing) → ВЫХОДЫ (Outputs)
```

| Элемент | Что описывает | Пример (Стратег) |
|---------|--------------|-----------------|
| **Входы** | Данные, триггеры | Коммиты из git, планы из DS-my-strategy, cron 7:00 |
| **Обработка** | Логика, промпты | Агрегация РП, генерация плана дня |
| **Выходы** | Артефакты, события | DayPlan.md, WeekPlan.md, PLAN.DayCreated |

Это не формализм ради формализма. Когда 10+ компонентов описаны одинаково — навигация и интеграция резко упрощаются.

---

## Карта знаний: где что лежит

### Source-of-truth (Pack)

Все описания — в одном Pack'е. Вот что внутри:

| Документ | Что описывает | Ссылка |
|----------|--------------|--------|
| **DP.ARCH.001** | Архитектура (3 слоя, 4 характеристики, принципы) | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.ARCH.001-platform-architecture.md) |
| **DP.CONCEPT.001** | Концепция: что платформа даёт человеку | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.CONCEPT.001-platform-concept.md) |
| **DP.AGENT.001** | Реестр ИИ-систем (агенты + ассистенты) | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.AGENT.001-ai-agents.md) |
| **DP.SYS.001** | Детерминированные системы (LMS, CRM, Twin) | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.SYS.001-deterministic-systems.md) |
| **DP.EXOCORTEX.001** | Модульный экзокортекс пользователя | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.EXOCORTEX.001-modular-exocortex.md) |
| **DP.NAV.001** | Навигация знаний между репозиториями | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.NAV.001-knowledge-navigation.md) |
| **DP.AISYS.013** | Знание-Экстрактор (метод + паспорт) | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/02-domain-entities/DP.AISYS.013-knowledge-extractor.md) |
| **01B-distinctions** | 15 различений (что с чем нельзя путать) | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/01-domain-contract/01B-distinctions.md) |
| **Pack Manifest** | Scope, зависимости, downstream | [→ файл](https://github.com/TserenTserenov/PACK-digital-platform/blob/main/pack/digital-platform/00-pack-manifest.md) |

### Downstream (реализации)

| Репо | Тип | Что делает |
|------|-----|-----------|
| [aist_bot](https://github.com/aisystant/aist_bot) | instrument | Telegram-бот (тонкий клиент, слой 3) |
| [digital-twin-mcp](https://github.com/aisystant/digital-twin-mcp) | instrument | MCP-реализация цифрового двойника (слой 2, зона Б) |
| [DS-strategist-agent](https://github.com/TserenTserenov/DS-strategist-agent) | instrument | Агент Стратег (слой 2, зона А) |
| [DS-extractor-agent](https://github.com/TserenTserenov/DS-extractor-agent) | instrument | Знание-Экстрактор — prompt-based ИИ-система (слой 2, зона А) |
| [DS-exocortex-setup-agent](https://github.com/TserenTserenov/DS-exocortex-setup-agent) | instrument | Агент развёртывания экзокортекса |
| [FMT-exocortex-template](https://github.com/TserenTserenov/FMT-exocortex-template) | format | Шаблон экзокортекса (CLAUDE.md + memory + стратег) |
| [DS-ecosystem-development](https://github.com/aisystant/DS-ecosystem-development) | governance | Планы, реестры, процессы |
| [DS-my-strategy](https://github.com/TserenTserenov/DS-my-strategy) | governance | Личный стратегический хаб |

### Upstream (откуда берём принципы)

| Репо | Что даёт |
|------|---------|
| [FPF](https://github.com/ailev/FPF) | Первые принципы (мета-онтология) |
| [SPF](https://github.com/TserenTserenov/SPF) | Вторые принципы (форма, процесс, Pack-формат) |
| [PACK-personal](https://github.com/aisystant/PACK-personal) | Контракт индикаторов созидателя |

---

## Текущее состояние

Архитектура описана. Реализованы:
- **Бот** — работает, FSM-архитектура, но баг-фиксы ещё идут
- **Стратег** — работает по расписанию (launchd), генерирует планы
- **Экзокортекс** — 3-слойная архитектура инструкций, используется ежедневно
- **Экзокортекс-шаблон + setup-agent** — fork & deploy для новых пользователей (bash-скрипт или Claude Code prompt)
- **Знание-Экстрактор** — MVP: 3 prompt-сценария (session-close, on-demand, bulk-extraction)
- **Pack** — 8 доменных сущностей, 15 различений, 2 failure modes

Не реализованы:
- Digital Twin MCP (в проектировании)
- Token Economy (концепция есть, кода нет)
- Proof-of-Impact (концепция)
- Hub, CRM, Биллинг (концепции)
- Cross-Repo-Sync и Knowledge-Audit (спроектированы, не реализованы)

Это честная картина. Архитектура описывает целевое состояние. Часть — уже работает, часть — ещё предстоит.

---

## Вопросы для обсуждения

1. **MCP как стандарт интеграции** — насколько MCP-протокол подходит для нашего масштаба? Не overengineering ли это для текущего этапа?

2. **Отчуждаемость vs скорость** — принцип «строить для передачи» замедляет разработку. Когда это оправдано, а когда можно hardcode?

3. **ИИ-системы stateless** — текущий Стратег хранит состояние в файлах (DS-my-strategy). Это нарушение stateless или допустимый паттерн?

4. **Порядок реализации** — что строить следующим: Digital Twin MCP, Token Economy или Hub?

---

> **Source-of-truth:** [PACK-digital-platform/pack/digital-platform/](https://github.com/TserenTserenov/PACK-digital-platform/tree/main/pack/digital-platform) — все описания архитектуры, компонентов и принципов.

*10 февраля 2026*
