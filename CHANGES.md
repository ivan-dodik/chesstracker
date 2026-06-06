# История изменений (CHANGES.md)

## 2026-06-06 20:24 — M6: Frontend — базовая структура и навигация
- Созданы: CSS, JS, HTML-шаблоны (base, login, index, players/list, tournaments/list)
- Созданы partials: player_row, tournament_row, pagination
- Созданы веб-роуты (web.py) для 4 страниц
- Проверены HTTP 200 для всех страниц
- 20/20 тестов проходят

## 2026-06-06 20:33 — Memory Bank расширен
- Созданы module-файлы в memory-bank/modules/ (overview, core, models, schemas, services, api, web, alembic, testing, telegram-bot, docker-infra)

## 2026-06-06 20:58 — M7: Frontend — дашборд и детальные страницы
- Добавлены веб-роуты: /players/{id}, /tournaments/{id}
- Chart.js CDN подключён в base.html
- Дашборд: графики рейтинга (line chart) и статистики (doughnut chart) с Chart.js + Alpine.js
- Создан профиль игрока (players/detail.html): рейтинг, статистика wins/losses/draws, график рейтинга, head-to-head, избранное
- Созданы детали турнира (tournaments/detail.html): информация, таблица standings с wins/draws/losses, партии по турам (аккордеон), экспорт CSV, импорт CSV для админа
- Обновлён TournamentStandings: добавлены wins, draws, losses
- Обновлён GameRead: добавлены white_player_name, black_player_name
- Обновлён game_service: обогащение партей именами игроков
- Обновлён tournament_service: подсчёт wins/draws/losses в standings
- Добавлены CSS-стили для страниц игрока, турнира, графиков, h2h
- 20/20 тестов проходят, docker build успешен

## 2026-06-06 21:06 — M8: Frontend — фичи
- Создан SSE-клиент (backend/app/static/js/sse.js): EventSource подключение к /api/events, toast-уведомления о новых партиях, изменении результатов, обновлении рейтинга
- SSE-клиент подключён в base.html
- Добавлен CSS-стиль flash-warning (для уведомлений об изменении результатов)
- Защита роутов через htmx:responseError (401 → редирект на /login) и Alpine.js Auth.isAuthenticated()
- Аутентификация на фронте: форма логина, JWT в localStorage, Authorization header через htmx:configRequest
- Избранное: кнопка ★ на профиле, список на дашборде
- Экспорт CSV: кнопка на странице турнира
- Импорт CSV: форма для админа на странице турнира
