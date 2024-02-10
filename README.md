# QRkot_spreadseets

Приложение для Благотворительного фонда поддержки котиков QRKot.
Фонд собирает пожертвования на различные целевые проекты: на медицинское обслуживание нуждающихся хвостатых, на обустройство кошачьей колонии в подвале, на корм оставшимся без попечения кошкам — на любые цели, связанные с поддержкой кошачьей популяции.
Доступно формирование отчёта по закрытым проектам с сортировкой по скорости сбора средств в Google Sheets.

# Технологии

Python
FastAPI
SQL Alchemy
Google Sheets
aiogoogle

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Sergey-K2/cat_charity_fund.git
```

```
cd cat_charity_fund
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

- Если у вас Linux/macOS

  ```
  source venv/bin/activate
  ```

- Если у вас windows

  ```
  source venv/scripts/activate
  ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
alembic upgrade head
```

Запуск проекта:

```
uvicorn app.main:app --reload
```

Документация API досупна по адресам:

[`http://localhost/api/docs/`](http://localhost/api/docs/)
или
[`http://localhost/api/redoc/`](http://localhost/api/redoc/)

## Автор:

Сергей Козлов
GitHub: [Sergey-K2](https://github.com/Sergey-K2)
