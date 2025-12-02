## NightBox — учебный сайт доставки

Простой проект на Python/Flask с авторизацией, SQLite и HTML/CSS фронтендом.

### Стек

- Backend/сервер: Flask
- БД: SQLite (`delivery.db`)
- Фронтенд: HTML + CSS (Jinja2-шаблоны)

### Страницы

- Публичные:
  - `/` — главная, описание сервиса + несколько товаров
  - `/catalog` — каталог всех товаров
  - `/login` — вход
  - `/register` — регистрация
- Только авторизованные:
  - `/profile` — профиль пользователя
  - `/cart` — корзина (добавление/удаление товаров)

### Локальный запуск (Windows, PowerShell)

```powershell
cd C:\Cursoriks\delivery_site_simple
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Сайт будет доступен по адресу `http://127.0.0.1:5000/`.

### Развёртывание на Render (бесплатный тариф)

1. Залить код в GitHub:
   - создать пустой репозиторий;
   - скопировать туда содержимое `delivery_site_simple` (чтобы в корне были `app.py`, `requirements.txt`, `templates/`, `static/`).
2. На `render.com`:
   - создать аккаунт и привязать GitHub;
   - **New + Web Service**;
   - выбрать репозиторий с проектом;
   - Environment: Python;
   - Build command: `pip install -r requirements.txt`;
   - Start command: `python app.py`;
   - Plan: Free.

Render сам подставит переменную окружения `PORT`, а приложение уже настроено использовать её.


