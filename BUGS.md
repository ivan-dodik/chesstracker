# Bug Report: Редирект после логина (аутентификация)

## Дата обнаружения
2026-06-07 ~01:00

## Версия
- Проект: Chess Tracker (M8 — Frontend фичи, все майлстоуны завершены)
- Коммит: `6a990f02fa24cd1ff4b4cffc425ff150c6021838`
- Ветка: `main`

## Окружение
- Docker Compose (3 сервиса: PostgreSQL 16 + backend + telegram-bot)
- Backend: Python 3.12 / FastAPI / Uvicorn
- Frontend: Jinja2 + HTMX 2.0.4 + Alpine.js 3.14.8 + Chart.js 4.4.7
- Аутентификация: JWT (localStorage) + Bearer Authorization header

## Описание проблемы

### Симптом
После успешного ввода логина и пароля (пользователь admin/admin123 или user/user123) происходит быстрый (менее 1 секунды) редирект обратно на страницу `/login`. Пользователь не может войти в систему — цикл: логин → дашборд → логин.

### Визуальное наблюдение
1. Пользователь вводит credentials на странице `/login`
2. Нажимает «Войти»
3. Появляется спиннер (loading state)
4. На короткое время отображается дашборд (`/`)
5. Происходит мгновенный редирект обратно на `/login`
6. В консоли браузера — сообщения:
   - `[Login] Login successful, token received`
   - `[Login] Token saved to localStorage`
   - `[Login] Redirecting to dashboard...`
   - Затем: очистка токена и редирект на `/login`

## Хронология и попытки исправлений

### Попытка 1 (2026-06-06 21:06, M8)
**Изменения:**
- Создан обработчик `htmx:responseError` в `base.html` (инлайн-скрипт до HTMX)
- Логика: `if (status === 401) → очистить токен → редирект на /login`
- Создан HTMX-запрос `/api/favorites` с `hx-trigger="load"` на дашборде
- Защита роутов через `htmx:responseError` и `Alpine.js Auth.isAuthenticated()`

**Ошибка:** Обработчик не различал ситуации:
- 401 без токена (публичный доступ, не ошибка)
- 401 с токеном (действительно проблема)

Любой 401 ответ от API вызывал очистку токена и редирект на логин.

### Попытка 2 (2026-06-07 01:24)
**Изменения:** (файл `backend/app/static/js/main.js`)
1. Добавлено подробное логирование в `loginForm.submit()`:
   - `[Login] Attempting login for user: ...`
   - `[Login] Login response status: ...`
   - `[Login] Login successful, token received`
   - `[Login] Token saved to localStorage`
   - `[Login] User info loaded: ...`
   - `[Login] Redirecting to dashboard...`

2. Улучшена обработка `/api/auth/me`:
   - Если запрос `me` падает (не 200) — **не блокирует вход**
   - Только `console.warn` с причиной
   - Ранее могло вызывать исключение, которое прерывало редирект

3. Исправлен обработчик `htmx:responseError` в `base.html`:
   ```javascript
   // Было:
   if (e.detail.xhr.status === 401) {
     localStorage.removeItem('jwt_token');
     localStorage.removeItem('user');
     window.location.href = '/login';
   }
   // Стало:
   if (e.detail.xhr.status === 401 && localStorage.getItem('jwt_token')) {
     localStorage.removeItem('jwt_token');
     localStorage.removeItem('user');
     window.location.href = '/login';
   }
   ```
   - Теперь 401 **без токена** игнорируется (публичный доступ — не ошибка)
   - 401 **с токеном** → очистка и редирект (токен невалидный/просроченный)

4. Добавлена задержка 100ms перед `window.location.href = '/'`:
   ```javascript
   setTimeout(() => {
     window.location.href = '/';
   }, 100);
   ```
   - Гарантирует, что localStorage обновлён до редиректа

**Затронутые файлы:** `backend/app/static/js/main.js` (строки 91-141)

**Результат:** Частично исправлено. Условие `&& localStorage.getItem('jwt_token')` предотвращает ложные редиректы при публичном доступе.

**Остаточная проблема:** При определённых условиях (гонка между HTMX `hx-trigger="load"` и Alpine.js `x-show`) запрос `/api/favorites` может уйти с токеном, получить 401 (например, если токен не успел добавиться через `htmx:configRequest`), и вызвать очистку токена + редирект.

## Анализ корневой причины

### 1. Гонка между HTMX `hx-trigger="load"` и Alpine.js `x-show`
В `index.html`:
```html
<div id="favorites-section" x-data="{ isAuth: Auth.isAuthenticated() }" x-show="isAuth">
  <div id="favorites-list" hx-get="/api/favorites" hx-trigger="load">
```

Проблема:
- HTMX обрабатывает `hx-trigger="load"` **сразу после загрузки элемента в DOM**
- Alpine.js обрабатывает `x-show` после инициализации (на этапе `alpine:init`)
- Если HTMX успевает отправить запрос `/api/favorites` до того, как Alpine скрыл секцию, и запрос возвращает 401 (без токена или с невалидным токеном) — срабатывает `htmx:responseError`

### 2. Уязвимость при загрузке страницы без токена
Если пользователь вводит URL дашборда (`/`) напрямую (без токена):
- HTMX запросы с `hx-trigger="load"` отправляются без Authorization header
- API возвращает 401 для защищённых эндпоинтов (например, `/api/favorites`)
- Если в localStorage есть `jwt_token` от предыдущей сессии — обработчик очищает его и редиректит
- Если токена нет — 401 игнорируется (исправлено в попытке 2)

### 3. Потенциальная проблема с `/api/auth/me`
После логина:
1. Сохраняется `access_token`
2. Делается запрос `/api/auth/me`
3. Если запрос падает (например, сетевой таймаут) — ошибка логируется, но не блокирует редирект
4. Если запрос успешен — `Auth.setUser(user)` сохраняет пользователя
5. Если `setUser` не вызван — `Auth.getUser()` возвращает `null`, `Auth.isAdmin()` → `false`

## Приоритет исправлений

### Critical (блокирует вход)
- [ ] Устранить гонку HTMX/Alpine: HTMX `hx-trigger="load"` не должен отправлять запросы к защищённым эндпоинтам, пока Alpine не подтвердил аутентификацию
- [ ] Альтернатива: заменить `hx-trigger="load"` на Alpine-управляемую загрузку для защищённых секций

### Important (улучшение стабильности)
- [ ] Увеличить задержку перед редиректом после логина (100ms → 300ms) или использовать Promise-based подход
- [ ] Добавить верификацию токена перед редиректом (проверить, что HTMX-запросы после редиректа будут содержать токен)

### Minor (диагностика)
- [ ] Добавить в консоль браузера метку времени для всех [Login] сообщений
- [ ] Логировать, какой именно HTMX-запрос вызвал 401

## Текущий статус
- **Статус:** ✅ RESOLVED
- **Блокирует авторизацию:** Нет
- **Рабочая версия:** admin/admin123, user/user123
- **Дата последнего изменения:** 2026-06-07 01:24
- **Дата исправления:** 2026-06-07 (дополнительные E2E-тесты подтверждают работоспособность)

### Разрешение проблемы
Проблема была исправлена в 2026-06-07 11:17:
- Добавлен `Auth.getAuthHeaders()` во все `fetch()` вызовы (Alpine.js компоненты)
- Удалён `hx-trigger="load"` из защищённых секций (favorites, top-rated)
- Установлен cookie `jwt_token` при логине для прямой навигации
- 29 E2E-тестов Playwright покрывают все сценарии аутентификации и подтверждают отсутствие регрессий
