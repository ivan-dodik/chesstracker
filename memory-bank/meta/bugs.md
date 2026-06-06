# Known Bugs (`BUGS.md`)

## Critical

### Циклический редирект после логина
- **Симптом**: После успешного логина происходит циклический редирект между `/login` и `/`
- **Корневая причина**: Гонка между HTMX `hx-trigger="load"` и Alpine.js `x-show` на дашборде
- **Статус**: Частично исправлено. Создан BUGS.md с полным анализом.
- **Подробнее**: см. `BUGS.md` в корне проекта

## Minor

### Контрастность CSS
- **Проблема**: Цвет ссылок `#3498db` и placeholder-текст `#7f8c8d` имеют недостаточный контраст на белом фоне
- **Аудит**: Accessibility Score 80/100
- **Статус**: Исправлено (результат аудита)

### Гонка HTMX + Alpine.js на дашборде
- **Проблема**: HTMX `hx-trigger="load"` и Alpine.js `x-show` одновременно управляют видимостью элементов
- **Статус**: Исправлено

## Links
- → `frontend/js-main.md` — HTMX + Alpine integration
- → `frontend/templates.md` — dashboard template