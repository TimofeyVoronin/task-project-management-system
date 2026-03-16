````md
# Development Guide

## Tools

Проект использует:

- `black` — форматирование Python-кода
- `isort` — сортировка импортов
- `ruff` — линтер и автоисправления
- `pre-commit` — проверки перед коммитом

## Setup

### Создать виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
````

### Установить dev-зависимости:

```bash
pip install -r requirements-dev.txt
```

### Установить git hooks:

```bash
pre-commit install
```

## Run checks

### Запуск всех проверок:

```bash
pre-commit run --all-files
```

### При необходимости можно запускать инструменты отдельно:

```bash
black .
isort .
ruff check .
ruff format .
```

## Workflow

### Перед работой:

```bash
source .venv/bin/activate
```

### Перед коммитом:

```bash
pre-commit run --all-files
```

### Если hooks изменили файлы, нужно повторно запустить проверки.

## Config files

В проекте используются:

* `requirements-dev.txt`
* `pyproject.toml`
* `.pre-commit-config.yaml`

```
```
