---
type: post
status: draft
created: 2026-02-13
updated: 2026-02-13
target: club
tags: [SOTA, FPF, SPF, Pack, Downstream, DDD, context-engineering, coupling-model, architecture, knowledge-management]
source_knowledge: https://github.com/TserenTserenov/PACK-digital-platform/tree/main/pack/digital-platform/06-sota
---

# Как 18 SOTA-методов превращают знания в работающие системы

> Пост о том, как FPF, SPF, Pack и Downstream образуют конвейер: от принципов мышления до бота, который отвечает пользователю. И что делает каждый метод на этом пути.

---

## Проблема

LLM умеет генерировать текст. Но текст — это не знание. Знание — это формализованная, проверенная, размещённая в правильном месте информация с ID, связями и критериями истинности.

Вопрос: **как построить систему, где ИИ-агенты работают с доменным знанием, а не с галлюцинациями?**

Ответ — архитектура из четырёх слоёв и 18 методов, которые связывают эти слои в работающий конвейер.

---

## Архитектура: 4 слоя

```
FPF (первые принципы)
 └→ SPF (вторые принципы — спецификация ядра)
     └→ Pack (знания предметной области — source-of-truth)
         └→ Downstream (производные системы: бот, агенты, MCP, курсы)
```

| Слой | Что | Роль | Пример |
|------|-----|------|--------|
| **FPF** | Метапринципы корректного мышления | Первые принципы — как думать правильно | «Различай систему и эпистему», «Не путай модель с объектом» |
| **SPF** | Спецификация ядра предметной области | Вторые принципы — как структурировать знание | Bounded Context, Entity Coding, 3-Layer Loading |
| **Pack** | Формализованные знания домена | Source-of-truth: сущности с ID, frontmatter, связями | `DP.SOTA.001-ddd-strategic.md`, `DP.D.017`, `DP.M.002` |
| **Downstream** | Производные системы | Проекции Pack в работающий код | Бот, Стратег, Экстрактор, MCP-сервер |

**Ключевой принцип:** Pack — единственный source-of-truth. Downstream меняется вслед за Pack, не наоборот. Это не документация рядом с кодом — это знание, из которого код порождается.

---

## Как FPF и SPF участвуют

### FPF: фундамент мышления

FPF не диктует, какие методы использовать. Он определяет **как проверять корректность** любого метода:

- **Различения** (A ≠ B с тестом проверки) — из FPF пришёл сам формат. Каждое различение в Pack — это FPF-паттерн.
- **SoTA Kit** — FPF формализует SOTA как аудируемые, обновляемые объекты с `edition:` и evidence.
- **RSCR-триггеры** — когда пересматривать решения.

FPF работает на уровне мышления: «Ты точно не путаешь модель с данными? А знание с информацией?»

### SPF: спецификация структуры

SPF определяет **слоты**, которые SOTA-методы заполняют:

| SPF-слот | Что определяет | Какой SOTA заполняет |
|----------|---------------|---------------------|
| Bounded Context | Граница ответственности модели | DDD Strategic |
| Словарь (термины) | Единый язык домена | DDD → Ubiquitous Language |
| Boundary Statements | Контракты между системами | Open API Specs |
| Multi-View | Множество представлений одной модели | Multi-Representation Architecture |
| Инварианты | Машинно-проверяемые правила | DSL → DSLM |
| Интеграция контекстов | Связи между системами | Coupling Model |
| Evidence | Подтверждение корректности | DDD tests + contract testing |

**Метафора:** FPF — грамматика. SPF — шаблон документа. Pack — конкретный текст. Downstream — публикация.

---

## 18 методов: что на вход, что на выход, как связаны

### Приоритетная тройка (применяются всегда)

#### 1. Context Engineering (DP.SOTA.002)

> Дисциплина курирования контекста ИИ-агента.

| | |
|---|---|
| **Вход** | Задача агента + все доступные знания (Pack, memory, context files) |
| **Выход** | Оптимизированный контекст: минимальный набор токенов для решения задачи |
| **4 стратегии** | **Write** (создай артефакт) → **Select** (выбери нужное) → **Compress** (сожми до минимума) → **Isolate** (изолируй контексты) |

**Почему первый:** Каждый агент — это LLM с ограниченным окном. Context Engineering определяет, что агент «видит». Плохой контекст = плохой агент, даже с идеальным знанием в Pack.

**Как связан:** Context Engineering определяет КАК Pack попадает в агент. DDD определяет ЧТО попадает.

#### 2. DDD Strategic (DP.SOTA.001)

> Метод добычи и формализации доменного знания через Bounded Context, Context Map, Ubiquitous Language.

| | |
|---|---|
| **Вход** | Доменное знание (текст, диалоги, код, курсы) |
| **Выход** | Bounded Context (границы Pack), Ubiquitous Language (глоссарий), Context Map (карта интеграций) |
| **НЕ включает** | Тактический DDD (Entity, Value Object, Aggregate) — это ООП-специфика |

**Почему второй:** Без DDD Strategic нет структуры. Pack без bounded context — свалка файлов. UL без консистентности — вавилонская башня.

**Как связан:** DDD определяет границы → Context Engineering определяет загрузку внутри границ → Coupling Model оценивает связи между границами.

#### 3. Coupling Model (DP.SOTA.011)

> Многомерная оценка связанности по Хононову (2024).

| | |
|---|---|
| **Вход** | Два компонента системы + их интеграция |
| **Выход** | Оценка по 3 измерениям + рекомендация уровня интеграции |
| **3 измерения** | **Knowledge** (сколько A знает о внутренностях B) · **Distance** (физическое/логическое расстояние) · **Volatility** (как часто меняется контракт) |
| **4 уровня** | Intrusive → Functional → Model → Message (от максимального coupling к минимальному) |

**Почему третий:** Coupling Model — прямой инструмент оценки эволюционируемости. Это ответ на вопрос «что сломается при изменении?» в конкретных, измеримых терминах.

**Как связан:** DDD определяет границы → Coupling Model измеряет качество связей между ними → Context Engineering минимизирует knowledge coupling в контексте агента.

---

### Методы создания знаний (Pack)

#### 4. Real-Time Knowledge Capture (DP.SOTA.008)

| | |
|---|---|
| **Вход** | Наблюдение в момент работы (паттерн, решение, ошибка) |
| **Выход** | Анонс «Capture: X → Y» — кандидат на знание |
| **Принцип** | During-work, not after-work. Знание утрачивается экспоненциально |

**Связка:** Capture → подаёт кандидатов в → AI-Accelerated Ontology Engineering (формализация).

#### 5. AI-Accelerated Ontology Engineering (DP.SOTA.007)

| | |
|---|---|
| **Вход** | Кандидаты на знание (captures, документы, код) |
| **Выход** | Формализованные Pack entities с ID, frontmatter, typed `related:` |
| **Принцип** | LLM делает first pass (draft classification), человек валидирует |

**Связка:** Captures → OE формализует → Pack entities появляются → Context Engineering обновляет контекст агентов.

---

### Методы организации знаний (структура)

#### 6. GraphRAG + Knowledge Graphs (DP.SOTA.004)

| | |
|---|---|
| **Вход** | Pack entities + typed `related:` из frontmatter |
| **Выход** | Vector + graph index для multi-hop reasoning |
| **Метрика** | 87% accuracy на multi-hop vs 23% у базового RAG |

**Связка:** Pack entities (создаёт OE) → GraphRAG индексирует → Context Engineering использует для Select (какие entities подгрузить).

#### 7. Multi-Representation Knowledge Architecture (DP.SOTA.012)

| | |
|---|---|
| **Вход** | Одна модель (Pack = source-of-truth) |
| **Выход** | Множество представлений (views) для разных потребителей |
| **3 паттерна** | `viewOf(model)` — одна модель, другая форма · `compositionViewOf(models[])` — несколько моделей в одно представление · `projectionView(model, concern)` — подмножество по аспекту |

**Связка:** Pack (модель) → Synchronizer проецирует через 3 паттерна → Bot/MCP/Courses (views).

#### 8. Open API Specifications (DP.SOTA.003)

| | |
|---|---|
| **Вход** | Границы между системами (из DDD Context Map) |
| **Выход** | Machine-readable контракты: OpenAPI (sync), AsyncAPI (events), CloudEvents (envelope), Arazzo (workflows) |

**Связка:** DDD определяет границы → Open Specs формализуют контракты → Coupling Model оценивает качество контрактов.

#### 9. DSL → DSLM Evolution (DP.SOTA.010)

| | |
|---|---|
| **Вход** | Доменные правила (инварианты, вторые принципы) |
| **Выход** | Machine-checkable constraints (YAML frontmatter, validators, DSLM) |

**Связка:** SPF определяет инварианты → DSL/DSLM делает их проверяемыми → Evidence/Assurance.

---

### Методы построения систем (Downstream)

#### 10. Agentic Development (DP.SOTA.006)

| | |
|---|---|
| **Вход** | Задача + доступные агенты |
| **Выход** | Оркестрация: каждый агент работает в своём BC параллельно |
| **Принцип** | Инженеры оркестрируют агентов, не пишут код напрямую |

**Связка:** DDD определяет BC каждого агента → Context Engineering определяет контекст → Coupling Model определяет интеграцию между агентами.

#### 11. AI-Native Org Design (DP.SOTA.005)

| | |
|---|---|
| **Вход** | Задачи организации/экосистемы |
| **Выход** | Архитектура: каждый агент = организационная единица с end-to-end accountability |

**Связка:** Agentic Development (как строить) + AI-Native Org (как организовать) = working multi-agent ecosystem.

#### 12. Knowledge-Based Digital Twins (DP.SOTA.009)

| | |
|---|---|
| **Вход** | Pack (модель) + данные (индикаторы) + агенты (inference) |
| **Выход** | Digital twin: модель, отвечающая от лица владельца |

**Связка:** Pack (знания) + PACK-personal (данные) + агенты (Стратег, Проводник) = цифровой двойник.

---

### Методы архитектуры Pack (из SPF.SPEC.003)

Эти шесть методов определяют, как Pack остаётся понятным для ИИ при росте:

#### 13–18. Pack Architecture SOTA

| # | Метод | Вход → Выход |
|---|-------|-------------|
| 13 | **RAPTOR** (Hierarchical Indexing) | Entity cards → 3-layer hierarchy (manifest → MAP → cards) |
| 14 | **Contextual Chunking** | Entity content → `summary` ≤150 символов в frontmatter |
| 15 | **Hybrid Retrieval** | Query → vector search по summary + exact search по ID |
| 16 | **LightRAG** | Typed `related:` → graph traversal по связям |
| 17 | **MemGPT/Letta** | 3-layer memory: core (manifest) + recall (MAP) + archival (cards) |
| 18 | **llms.txt** | Pack manifest → machine-readable index |

---

## Как методы связаны: полный конвейер

```
    ОБНАРУЖЕНИЕ                    ФОРМАЛИЗАЦИЯ                  ОРГАНИЗАЦИЯ
    ───────────                    ────────────                  ───────────
    Real-Time Capture ──────→ AI-Accelerated OE ──────→ Pack entities
    (during work)              (LLM draft + human)        (ID, frontmatter,
                                                           typed related:)
                                       ↓
                                  DDD Strategic
                                  (BC, UL, Context Map)
                                       ↓
    СТРУКТУРИРОВАНИЕ               ОЦЕНКА                     ПРОЕКЦИЯ
    ────────────────               ──────                     ────────
    GraphRAG + KG ←──────── Coupling Model ──────→ Multi-Representation
    (vector + graph)        (knowledge/distance/    (viewOf, compositionViewOf,
                             volatility)             projectionView)
         ↓                        ↓                        ↓
    RETRIEVAL                  КОНТРАКТЫ              DOWNSTREAM
    ─────────                  ────────               ──────────
    Context Engineering ←── Open API Specs ───→ Agentic Development
    (Write/Select/             (OpenAPI,             (multi-agent
     Compress/Isolate)          AsyncAPI)              orchestration)
         ↓                                               ↓
    АГЕНТ РАБОТАЕТ ←────────────────────────────── AI-Native Org
    (бот, стратег,                                 (каждый агент =
     экстрактор)                                    org unit)
         ↓
    Digital Twin
    (Pack + данные + агенты)
```

---

## Как это помогает создавать системы

### Без этой архитектуры

1. Пишешь бота → знания хардкодятся в код
2. Меняется домен → переписываешь код
3. Добавляешь второго агента → дублируешь знания
4. Через полгода → 3 агента с разными версиями «правды»
5. LLM галлюцинирует → некому проверить

### С этой архитектурой

1. Обнаружил знание → capture during-work (SOTA.008)
2. Формализовал → AI-Accelerated OE (SOTA.007) → Pack entity с ID
3. Определил границы → DDD Strategic (SOTA.001) → bounded context
4. Оценил связи → Coupling Model (SOTA.011) → минимальный coupling
5. Спроектировал контекст → Context Engineering (SOTA.002) → CLAUDE.md + memory
6. Спроецировал → Multi-Representation (SOTA.012) → бот, MCP, курс
7. Организовал агентов → Agentic Development (SOTA.006) → параллельная работа

**Результат:** одно изменение в Pack → автоматически обновляет все downstream. Знание не дублируется. Агенты работают с проверенным знанием, не с галлюцинациями. Система эволюционирует через обновление Pack, не через переписывание кода.

### Оценка через 4 характеристики

| Характеристика | Как обеспечивается |
|----------------|-------------------|
| **Эволюционируемость** | Coupling Model (3 измерения) + DDD (BC границы) + Open Specs (контракты) |
| **Масштабируемость** | RAPTOR (3-layer loading) + GraphRAG (multi-hop) + Sub-Pack Protocol |
| **Обучаемость** | Context Engineering (Write/Select/Compress) + UL (единый язык) + llms.txt (manifest) |
| **Генеративность** | Multi-Representation (Pack → любой surface) + AI-Native Org (новый агент = новая org unit) + Digital Twins (Pack + данные = двойник) |

---

## Итог

18 методов — не коллекция модных слов. Это **конвейер**, где каждый метод имеет конкретный вход и выход, и связан с другими:

- **FPF** даёт грамматику мышления
- **SPF** даёт шаблон структуры
- **Pack** хранит формализованные знания
- **SOTA-методы** — инструменты на каждом этапе конвейера
- **Downstream** — работающие системы, порождённые из знания

Знание → структура → проекция → система. Не код, из которого потом пытаются извлечь знание. А знание, из которого порождается код.

---

> **Source-of-truth:** [PACK-digital-platform/pack/digital-platform/06-sota/](https://github.com/TserenTserenov/PACK-digital-platform/tree/main/pack/digital-platform/06-sota) — все 12 SOTA-сущностей с evidence и связями.

*Edition: 2026-02 | Pack DP v0.3.0 (39 entities)*
