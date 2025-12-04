# KeyRescuer Telegram Bot

## Setup
1. Создать и активировать окружение на Python 3.11:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Заполнить `.env` по примеру `.env.example`:
   ```env
   BOT_TOKEN=your-telegram-bot-token
   APPS_SCRIPT_URL=https://script.google.com/macros/s/your-apps-script-id/exec
   ADMIN_CHAT_ID=123456789  # необязательно
   ```

## Run
```bash
source .venv/bin/activate
python -m app.bot
```

## Notes
- Игнорируются: `.venv/`, `.env`, `__pycache__/`, IDE-файлы (см. `.gitignore`).
- Если требуется другая версия Python, убедитесь, что `aiogram==2.25.1` совместима (Python 3.11).
