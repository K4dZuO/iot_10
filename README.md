# Система мониторинга температуры (FastAPI Backend)

## Общее описание

Данный проект реализует backend-сервис для сбора, хранения и предоставления температурных данных с датчиков **DS18B20**.

Система предназначена для:

* приёма данных от IoT-устройств (например, ESP32)
* хранения временных рядов температур
* предоставления API для визуализации данных
* управления метаданными датчиков (например, именами)

Проект реализован в минималистичном стиле, но с корректной архитектурой (разделение слоёв).

---

## Архитектура системы

### Поток данных

1. Устройство считывает температуру с датчиков
2. Устройство отправляет данные на сервер (HTTP POST)
3. Backend:

   * фильтрует некорректные значения
   * регистрирует новые датчики
   * сохраняет измерения в БД
4. Клиент (UI или curl):

   * получает список датчиков
   * запрашивает измерения
   * обновляет имена датчиков

---

## Структура проекта

```
app/
├── main.py
├── db.py
├── models.py
├── schemas.py
├── services/
│   ├── measurement_service.py
│   └── sensor_service.py
└── api/
    └── routers/
        ├── measurements.py
        └── sensors.py
```

### Описание компонентов

#### `main.py`

Точка входа приложения:

* создаёт FastAPI приложение
* инициализирует БД через lifespan
* подключает роутеры

#### `db.py`

* настройка подключения к базе данных
* создание `engine`
* dependency `get_session`

#### `models.py`

ORM-модели (таблицы БД):

* `Sensor`
* `Measurement`

#### `schemas.py`

Схемы API:

* входные (input)
* выходные (response)

#### `services/`

Слой бизнес-логики:

* обработка измерений
* работа с датчиками

#### `routers/`

HTTP-слой:

* обработка запросов
* маппинг на сервисы

---

## Модель данных

### Sensor

```python
class Sensor:
    id: str              # уникальный ID (ROM DS18B20)
    name: Optional[str]  # пользовательское имя
    device_id: str       # устройство
```

---

### Measurement

```python
class Measurement:
    id: int
    sensor_id: str
    temperature: float
    timestamp: datetime
```

---

## API

Базовый URL:

```
http://localhost:8000/api
```

---

### 1. Отправка измерений

**POST `/measurements`**

Используется IoT-устройством.

#### Пример запроса:

```json
{
  "deviceId": "esp32-test",
  "measurements": [
    {
      "sensorId": "28-000001",
      "temperature": 22.5
    },
    {
      "sensorId": "28-000002",
      "temperature": 24.1
    }
  ]
}
```

#### Поведение:

* если датчик не существует → создаётся
* если timestamp не указан → используется текущее время
* значения `-127` и `85` игнорируются
* дубликаты (sensor_id + timestamp) игнорируются

#### Ответ:

```json
{
  "status": "ok"
}
```

---

### 2. Получение списка датчиков

**GET `/sensors`**

#### Ответ:

```json
[
  {
    "id": "28-000001",
    "name": "Кухня",
    "device_id": "esp32-test"
  }
]
```

---

### 3. Обновление датчика

**PATCH `/sensors/{sensorId}`**

#### Пример:

```json
{
  "name": "Спальня"
}
```

#### Ответ:

```json
{
  "status": "updated"
}
```

---

### 4. Получение измерений

**GET `/measurements`**

#### Параметры:

| Параметр  | Тип      | Описание            |
| --------- | -------- | ------------------- |
| sensorIds | array    | список датчиков     |
| from_     | datetime | начало периода      |
| to        | datetime | конец периода       |
| limit     | int      | ограничение         |
| cursor    | datetime | курсор (pagination) |

---

#### Пример запроса:

```
/measurements?sensorIds=28-000001&limit=10
```

---

#### Ответ:

```json
{
  "data": [
    {
      "sensorId": "28-000001",
      "temperature": 22.5,
      "timestamp": "2026-03-17T15:43:46"
    }
  ],
  "nextCursor": "2026-03-17T15:43:46"
}
```

---

## Логика работы

### 1. Авто-регистрация датчиков

При первом появлении `sensorId`:

* создаётся запись в таблице `Sensor`

---

### 2. Фильтрация ошибок

Игнорируются значения:

* `-127` — ошибка чтения
* `85` — неинициализированный датчик

---

### 3. Идемпотентность

Проверка:

```
(sensor_id, timestamp)
```

Если запись уже существует → не добавляется.

---

### 4. Пагинация

Используется **cursor-based pagination**:

* сортировка по `timestamp DESC`
* следующий курсор = timestamp последней записи

---

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn sqlmodel
```

---

### 2. Запуск сервера

```bash
uvicorn app.main:app --reload
```

---

### 3. Доступ

```
http://localhost:8000
http://localhost:8000/docs
```

---

## Тестирование через curl

### Отправка данных

```bash
curl -X POST http://localhost:8000/api/measurements \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "esp32-test",
    "measurements": [
      {"sensorId": "28-000001", "temperature": 22.5},
      {"sensorId": "28-000002", "temperature": 24.1}
    ]
  }'
```

---

### Получение датчиков

```bash
curl http://localhost:8000/api/sensors
```

---

### Получение измерений

```bash
curl "http://localhost:8000/api/measurements?sensorIds=28-000001&limit=10"
```

---

### Обновление датчика

```bash
curl -X PATCH http://localhost:8000/api/sensors/28-000001 \
  -H "Content-Type: application/json" \
  -d '{"name": "Кухня"}'
```

---

## Ограничения текущей реализации

* отсутствует аутентификация
* используется SQLite (не для production)
* нет миграций
* нет логирования
* нет rate limiting
* нет агрегированных данных (avg, min, max)

---

## Возможные улучшения

1. PostgreSQL + TimescaleDB
2. Alembic (миграции)
3. JWT / API ключи
4. Кэширование (Redis)
5. Агрегации для графиков
6. WebSocket для real-time

---

## Заключение

Проект реализует:

* корректный REST API
* базовую обработку IoT данных
* чистую архитектуру (router → service → model)

