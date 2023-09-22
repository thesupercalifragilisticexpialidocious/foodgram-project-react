# FOODGRAM #
![alt text](https://github.com/thesupercalifragilisticexpialidocious/foodgram-project-react/actions/workflows/fg_workflow.yml/badge.svg)
Платформа для обмена кулинарными рецептами. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать файлом сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект реализован на django 2.2.16, используются библиотеки DRF, djoser, reportlab. В данной конфигурации используются докер-образы nginx и PostgreSQL в качестве серверного движка и базы данных соответственно.

### Подготовка переменных среды

В папке infra необходимо создать файл с переменными среды .env формата:
 
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db
DB_PORT=5432
SECRET_KEY=pthnq!x@c5al3k1gve%j_(a111cc0_pj96bz1)=ryvn4^6_4_2
```
(Произвольный ключ нужного формата можно получить через сайт djecrety.ir)


### Как запустить проект в докер-контейнере:

Из директории infra выполни:

```
docker-compose up -d
```

Выполни команды:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

Опционально можно наполнить базу данных ингридиентами из коробочного csv-файла (static/data/ingredients.csv).

```
docker-compose exec web python manage.py import_csv
```

Backend by @thesupercalifragilisticexpialidocious
