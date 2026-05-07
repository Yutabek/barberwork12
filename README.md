# StyleFlow Python Telegram Bot

Bu project Telegram Mini App uchun alohida Python bot service.

Bot vazifasi:

- `/start` ga javob beradi
- `Open StyleFlow` tugmasini yuboradi
- Tugma orqali Telegram Mini App frontendni ochadi
- Optional: `/api/notify-booking` orqali booking confirmation yuboradi

## 1. Local ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python bot.py
```

`.env` ichida token va frontend URL ni qo'ying:

```env
BOT_TOKEN=your_real_bot_token
MINI_APP_URL=https://username.github.io/styleflow-frontend/client.html
BACKEND_API_URL=https://your-backend.up.railway.app
PORT=5000
```

## 2. Railway deploy

Railway Variables ichida qo'ying:

```env
BOT_TOKEN=your_real_bot_token
MINI_APP_URL=https://username.github.io/styleflow-frontend/client.html
BACKEND_API_URL=https://your-backend.up.railway.app
```

`PORT` ni Railway o'zi beradi, qo'ymasangiz ham bo'ladi.

## 3. Webhook set qilish

Deploy bo'lgandan keyin Railway URL ni oling:

```text
https://your-bot-service.up.railway.app
```

Browserda oching:

```text
https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=https://your-bot-service.up.railway.app/api/telegram/webhook
```

Tekshirish:

```text
https://api.telegram.org/botYOUR_TOKEN/getWebhookInfo
```

## 4. Health check

```text
https://your-bot-service.up.railway.app/health
```

## Muhim

- Bot tokenni frontendga qo'ymang.
- `MINI_APP_URL` frontend link bo'lishi kerak.
- `BACKEND_API_URL` backend API link bo'lishi kerak.
- Agar token screenshot/chatda ko'rinib qolsa, BotFather orqali revoke qiling.
