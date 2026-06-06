# Настройка Telegram Bot

Для работы Telegram-бота Chess Tracker необходим токен, который выдаёт [@BotFather](https://t.me/BotFather) — официальный бот Telegram для управления ботами.

## Инструкция по созданию токена

1. **Откройте Telegram** и найдите [@BotFather](https://t.me/BotFather) (официальный бот Telegram).

2. **Отправьте команду** `/newbot`.

3. **Укажите имя бота** — это отображаемое имя, например `Chess Tracker`.

4. **Укажите username бота** — должен заканчиваться на `bot`, например:
   - `chess_tracker_bot`
   - `my_chess_bot`
   - `chess_notifier_bot`

5. **Скопируйте полученный токен**. BotFather пришлёт сообщение вида:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/chess_tracker_bot.
   You can now add a description, about section and profile picture for your bot, see /help for a list of commands.
   
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklmNOPqrSTUvwxYZ
   
   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

6. **Запишите токен в `.env` файл** в корне проекта:
   ```bash
   # Откройте .env и замените строку с TG_BOT_TOKEN:
   TG_BOT_TOKEN=1234567890:ABCdefGHIjklmNOPqrSTUvwxYZ
   ```

7. **Перезапустите проект**:
   ```bash
   docker compose up --build
   ```

## Проверка работы

После запуска бот должен написать в логах:
```
Chess Tracker Bot started (long-polling mode)
```

Найдите своего бота в Telegram по username (например `@chess_tracker_bot`) и отправьте команду `/start`.

## Если токен не указан

Если в `.env` нет токена или указан токен-заглушка (`your-telegram-bot-token`), бот **не запустится**, а в логах появится предупреждение:
```
TG_BOT_TOKEN is not set or is a placeholder. Bot will not start.
```

При этом backend и база данных продолжат работать нормально.

## Безопасность

- **Никому не передавайте токен** — он даёт полный контроль над ботом.
- **Не коммитьте токен в Git** — `.env` добавлен в `.gitignore`.
- Если токен скомпрометирован, отзовите его у @BotFather командой `/revoke` и создайте новый.