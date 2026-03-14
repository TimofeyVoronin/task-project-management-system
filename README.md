# Task / Project Management System — Architecture

## 1. Project overview

Проект представляет собой backend-систему управления рабочими пространствами, проектами и задачами с event-driven взаимодействием между сервисами.

Система ориентирована на следующие сценарии:

* регистрация и аутентификация пользователей
* создание рабочих пространств и управление участниками
* создание проектов внутри workspace
* управление задачами, комментариями и историей изменений
* генерация внутренних уведомлений на основе доменных событий

Проект строится как **микросервисная система** с разделением ответственности между сервисами и обменом событиями через RabbitMQ.

---

## 2. Goals

Основные цели проекта:

* показать архитектуру production-style backend-системы
* продемонстрировать работу с Django / DRF в многосервисной среде
* реализовать role-based access control
* показать event-driven взаимодействие через RabbitMQ
* реализовать идемпотентную обработку событий
* покрыть систему тестами и CI

---

## 3. Tech stack

### Core technologies

* Python
* Django
* Django REST Framework
* PostgreSQL
* Redis
* RabbitMQ
* Celery
* Docker / Docker Compose
* Pytest
* drf-spectacular
* GitHub Actions

---

## 4. Services

Система состоит из трёх сервисов.

### 4.1 `auth_service`

Отвечает за аутентификацию и пользовательские данные.

**Responsibilities:**

* регистрация пользователя
* login/logout
* JWT authentication
* refresh token flow
* смена пароля
* профиль пользователя
* login history

**Data owned by service:**

* users
* token / blacklist data
* login history

---

### 4.2 `core_service`

Центральный бизнес-сервис системы.

**Responsibilities:**

* workspaces
* memberships
* projects
* private project access
* tasks
* labels
* watchers
* comments
* activity log

**Data owned by service:**

* workspace
* workspace_membership
* project
* project_access
* task
* label
* task_label
* task_watcher
* comment
* activity_log

---

### 4.3 `notification_service`

Сервис обработки доменных событий и генерации уведомлений.

**Responsibilities:**

* чтение событий из RabbitMQ
* создание Notification
* идемпотентная обработка событий
* фоновая обработка уведомлений
* Notification API

**Data owned by service:**

* notification

---

## 5. Service interaction model

### HTTP

HTTP используется для клиентского взаимодействия с API.

Клиент обращается к:

* `auth_service` для регистрации и аутентификации
* `core_service` для работы с workspace / project / task / comment
* `notification_service` для чтения уведомлений

### RabbitMQ

RabbitMQ используется для межсервисного обмена доменными событиями.

* `core_service` публикует события
* `notification_service` потребляет события

---

## 6. User identity strategy

Ключевое архитектурное решение проекта:

**только `auth_service` владеет пользователями как сущностями.**

Во всех остальных сервисах пользователь хранится только как внешний `user_id`.

### Rules

* `core_service` не имеет FK на таблицу пользователей
* `notification_service` не имеет FK на таблицу пользователей
* между сервисами нет межсервисных foreign key
* `user_id` используется как внешний идентификатор пользователя из `auth_service`

### Why

Это упрощает границы сервисов и сохраняет независимость схем данных.

---

## 7. Domain model

## 7.1 Workspace

Рабочее пространство — верхний контейнер бизнес-объектов.

**Main fields:**

* id
* name
* slug
* owner_id
* is_archived
* created_at
* updated_at

---

## 7.2 WorkspaceMembership

Связь пользователя с workspace.

**Main fields:**

* workspace_id
* user_id
* role
* created_at

**Roles:**

* owner
* manager
* member
* viewer

---

## 7.3 Project

Проект внутри workspace.

**Main fields:**

* id
* workspace_id
* name
* slug
* description
* created_by
* visibility
* is_archived
* is_completed
* completed_at
* created_at
* updated_at

**Visibility:**

* public
* private

---

## 7.4 ProjectAccess

Явный доступ пользователя к private project.

**Main fields:**

* project_id
* user_id
* granted_by
* created_at

Используется только для private projects.

---

## 7.5 Task

Основная рабочая сущность системы.

**Main fields:**

* id
* project_id
* title
* description
* status
* priority
* due_date
* assignee_id
* reporter_id
* is_archived
* deleted_at
* created_at
* updated_at

**Statuses:**

* todo
* in_progress
* in_review
* done

**Priorities:**

* low
* medium
* high
* critical

---

## 7.6 Label

Метка задачи внутри workspace.

**Main fields:**

* id
* workspace_id
* name
* color

---

## 7.7 TaskWatcher

Подписка пользователя на задачу.

**Main fields:**

* task_id
* user_id
* created_at

Watcher не даёт дополнительных прав доступа и используется только как подписка на изменения задачи.

---

## 7.8 Comment

Комментарий к задаче.

**Main fields:**

* id
* task_id
* author_id
* body
* edited_at
* deleted_at
* created_at
* updated_at

---

## 7.9 ActivityLog

Бизнес-аудит изменений.

**Main fields:**

* entity_type
* entity_id
* actor_id
* action
* old_value_jsonb
* new_value_jsonb
* metadata_jsonb
* created_at

Используется как центральный источник истории действий по проектам, задачам, membership и комментариям.

---

## 7.10 Notification

Уведомление пользователя.

**Main fields:**

* id
* recipient_id
* event_id
* event_type
* title
* message
* status
* is_read
* read_at
* payload_json
* created_at
* updated_at

**Statuses:**

* pending
* processing
* sent
* failed

---

## 8. Access control model

Система использует role-based access control с несколькими уровнями.

### Workspace level

Роль пользователя в workspace определяет базовые права.

### Project level

Для private project используется дополнительная проверка через `ProjectAccess`.

### Task level

Доступ к задаче наследуется от доступа к проекту и дополняется object-level permission checks.

### Comment level

Доступ к комментариям определяется доступом к задаче и дополнительными правилами редактирования/удаления.

---

## 9. Permission rules

### Owner

* полный доступ к workspace
* управление участниками
* управление private access
* управление проектами и задачами

### Manager

* расширенный доступ внутри workspace
* может управлять проектами, задачами и участниками
* не выполняет owner-only операции

### Member

* работает с доступными проектами и задачами
* может создавать и изменять сущности в рамках правил

### Viewer

* может читать доступные сущности
* не может создавать или изменять проекты, задачи и комментарии

### Comment rule for viewer

* viewer может читать комментарии
* viewer не может создавать комментарии
* viewer не может редактировать комментарии
* viewer не может удалять комментарии

---

## 10. Project visibility model

### Public project

Доступен участникам workspace по правилам membership/permissions.

### Private project

Доступен:

* owner workspace
* manager workspace
* пользователям с явной записью в `ProjectAccess`

---

## 11. Task workflow

### Allowed status transitions

* todo -> in_progress
* in_progress -> in_review
* in_review -> done
* done -> in_progress

### Task lifecycle actions

* create
* update
* assign
* unassign
* archive
* unarchive
* soft delete

---

## 12. Project lifecycle

### Main actions

* create
* update
* archive
* unarchive
* complete

### Rules after completion

После `project.completed`:

* нельзя создавать новые задачи в проекте
* нельзя изменять ключевые поля проекта через обычный update endpoint
* completed project остаётся доступным для чтения

---

## 13. Soft delete strategy

### Tasks

Для задач используется `deleted_at`.

### Comments

Для комментариев используется `deleted_at`.

### Rules

* soft deleted записи скрываются из обычных запросов
* физическое удаление не используется в основных сценариях
* history сохраняется для audit trail

---

## 14. Labels strategy

### Rules

* label принадлежит workspace
* одна задача может иметь несколько labels
* удаление label выполняется как hard delete
* при удалении label удаляются связи task-label

---

## 15. Activity model

Activity не вычисляется динамически по живым таблицам.

Все значимые действия записываются в `ActivityLog`.

### Examples of logged actions

* workspace created
* member added
* member role changed
* ownership transferred
* project created
* project archived
* task created
* task updated
* task assigned
* task status changed
* comment created
* comment updated
* comment deleted

### Activity endpoints

* `GET /tasks/{id}/activity`
* `GET /projects/{id}/activity`
* `GET /workspaces/{id}/activity`

Эти endpoints читают данные из `ActivityLog`.

---

## 16. Event-driven architecture

## 16.1 Purpose

RabbitMQ используется для публикации доменных событий после успешных бизнес-операций.

## 16.2 Main principle

Событие публикуется **только после успешного commit транзакции**.

Для этого используется подход вида:

* `transaction.on_commit(...)`

---

## 17. Domain event schema

Все события имеют единый envelope.

```json
{
  "event_id": "uuid",
  "event_type": "task.status_changed",
  "event_version": 1,
  "occurred_at": "2026-03-14T10:00:00Z",
  "producer_service": "core_service",
  "payload": {},
  "metadata": {}
}
```

### Envelope fields

* `event_id`
* `event_type`
* `event_version`
* `occurred_at`
* `producer_service`
* `payload`
* `metadata`

---

## 18. Published events

### Project events

* `project.created`
* `project.updated`
* `project.archived`
* `project.completed`

### Task events

* `task.created`
* `task.updated`
* `task.assigned`
* `task.unassigned`
* `task.status_changed`
* `task.archived`

### Comment events

* `comment.created`
* `comment.updated`
* `comment.deleted`

---

## 19. RabbitMQ routing

Основной exchange:

* `domain_events`

Примеры routing keys:

* `project.created`
* `project.updated`
* `task.created`
* `task.assigned`
* `task.status_changed`
* `comment.created`

`notification_service` подписывается на нужные очереди и обрабатывает только интересующие события.

---

## 20. Event reliability rules

### Idempotency

Каждое событие имеет уникальный `event_id`.

`notification_service` обязан обрабатывать повторную доставку безопасно.

### Versioning

Каждое событие содержит `event_version`, чтобы поддерживать эволюцию схемы.

### Duplicate safety

Обработка дублей не должна приводить к повторному созданию уведомлений.

---

## 21. Notification flow

`notification_service` обрабатывает события и создаёт внутренние уведомления.

### Supported events for notification generation

* `task.assigned`
* `task.status_changed`
* `comment.created`

### Recipient rules

#### `task.assigned`

Получатель:

* `assignee`

#### `task.status_changed`

Получатели:

* `reporter`
* `assignee`
* `watchers`

#### `comment.created`

Получатели:

* `reporter`
* `assignee`
* `watchers`

### General notification rules

* actor не получает уведомление о собственном действии
* дубли получателей исключаются
* отсутствие assignee/watchers должно обрабатываться корректно

---

## 22. Notification processing lifecycle

### Notification statuses

* `pending`
* `processing`
* `sent`
* `failed`

### Read state

* `is_read`
* `read_at`

Состояние доставки уведомления и состояние прочтения пользователем разделены.

---

## 23. Background processing

Celery используется в `notification_service` для фоновой обработки уведомлений.

### Responsibilities

* обработка pending notifications
* retry logic
* перевод статусов processing -> sent / failed
* логирование ошибок обработки

---

## 24. Testing strategy

Система покрывается несколькими уровнями тестов.

### Unit tests

* модели
* managers
* permission logic
* business services

### API tests

* auth endpoints
* workspace endpoints
* project endpoints
* task endpoints
* comment endpoints
* notification endpoints

### Integration tests

* RabbitMQ publishing
* event consumption
* transactional publication
* Celery tasks

### Special test areas

* permissions
* idempotency
* filters and search
* database constraints
* API response schemas

---

## 25. Documentation plan

Проект должен включать следующую документацию:

* README
* ARCHITECTURE.md
* domain model description
* ER diagram
* event catalog
* RabbitMQ configuration notes
* environment configuration
* local development setup
* testing guide

---

## 26. CI strategy

CI pipeline должен выполнять:

* установку зависимостей
* линтинг
* запуск тестов
* отчёт по coverage

Инструменты:

* GitHub Actions
* ruff / flake8
* black
* isort
* pytest
* pytest-cov

---

## 27. Implementation order

Рекомендуемый порядок реализации:

1. Infrastructure
2. `auth_service`
3. `core_service` workspace + membership
4. `core_service` projects + project access
5. `core_service` tasks
6. labels + watchers
7. comments + activity
8. RabbitMQ event layer
9. `notification_service`
10. tests
11. documentation and CI

---

## 28. Non-goals for MVP

Следующие вещи не входят в первую версию и могут быть добавлены позже:

* attachments
* task checklist
* websocket notifications
* realtime updates
* dedicated search service
* metrics and monitoring
* API gateway
* outbox pattern
* distributed tracing

---

## 29. Portfolio value

Проект демонстрирует:

* backend architecture design
* Django / DRF in multi-service setup
* PostgreSQL schema design
* role-based access control
* RabbitMQ event-driven integration
* Celery background processing
* idempotent consumer design
* testing strategy
* production-oriented engineering practices

---