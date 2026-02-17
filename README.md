# Telegram Bot Setup Guide

Bu loyiha `aiogram` asosidagi Telegram bot. Bot foydalanuvchi xabarlarini admin'ga yuboradi va admin javobini user'ga qaytaradi. 
Project PostgreSQL bilan ishlaydi.

## 1. Talablar

- Python 3.11+
- PostgreSQL 14+
- Telegram bot token (BotFather dan)

## 2. Loyihani ochish va virtual environment

```bash
cd "/home/sss/Рабочий стол/Telegram bot"
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 3. PostgreSQL o'rnatish (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

## 4. Database va user yaratish

`postgres` user bilan `psql` ga kiring:

```bash
sudo -u postgres psql
```

Ichida quyidagilarni bajaring:

```sql
CREATE DATABASE telegram_bot;
CREATE USER bot_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO bot_user;
\c telegram_bot
GRANT USAGE, CREATE ON SCHEMA public TO bot_user;
ALTER SCHEMA public OWNER TO bot_user;
\q
```

## 5. `.env` sozlash

Project root'da `.env` fayl:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_USER_ID
DATABASE_URL=postgresql://bot_user:strong_password@localhost:5432/telegram_bot
```

Izoh:
- `ADMIN_ID` bu birinchi (default) admin.
- Bot start paytida `admins` jadvali bo'sh bo'lsa, shu `ADMIN_ID` primary admin bo'lib yoziladi.

## 6. Botni ishga tushirish

```bash
source env/bin/activate
python main.py
```

Agar hammasi to'g'ri bo'lsa logda PostgreSQL connection haqida yozuv ko'rasiz.

## 7. Admin paneldan foydalanish

Admin akkauntdan:

1. `/start` yoki `/admin` yuboring.
2. `Admin panelni ochish` tugmasini bosing.
3. Kerakli amalni tanlang:
   - `Adminlar ro'yxati`
   - `Admin qo'shish`
   - `Asosiy adminni almashtirish`
   - `Adminni o'chirish`

Kerak bo'lsa bot sizdan `user_id` so'raydi.

## 8. User ID ni qanday olish

Variantlar:
- `@userinfobot` ga kirib ID olish.
- Botga yozgan user xabari admin'ga kelganda `ID: ...` ko'rinadi.

## 9. Foydali tekshiruvlar

### 9.1 PostgreSQL ichida adminlar ro'yxati

```bash
sudo -u postgres psql -d telegram_bot
```

```sql
SELECT user_id, is_primary FROM admins ORDER BY is_primary DESC, user_id;
```

### 9.2 Userlar ro'yxati

```sql
SELECT user_id, username FROM users ORDER BY id DESC;
```

## 10. Ko'p uchraydigan xatolar

### `psycopg2.errors.InsufficientPrivilege: нет доступа к схеме public`
Schema huquqi yo'q. 4-bo'limdagi grant/owner buyruqlarini qayta bajaring.

### `TelegramConflictError: terminated by other getUpdates request`
Bir xil token bilan bir nechta bot instance ishlayapti.

Yechim:
```bash
pkill -f "python main.py"
python main.py
```

Agar webhook ishlatilgan bo'lsa:
```bash
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook?drop_pending_updates=true"
```

### Admin panel javob bermasa
- Botni restart qiling.
- To'g'ri admin akkauntdan kirganingizni tekshiring.
- `.env` dagi `ADMIN_ID` va real Telegram ID ni solishtiring.

## 11. Production tavsiyalar

- `.env` ni hech qachon GitHub'ga push qilmang.
- Kuchli parol ishlating.
- `DATABASE_URL` parolini tez-tez almashtirib turing.
- Systemd yoki Docker bilan bitta instance sifatida ishga tushiring.

## 12. Tez start (qisqa)

```bash
cd "/home/sss/Рабочий стол/Telegram bot"
source env/bin/activate
pip install -r requirements.txt
python main.py
```

