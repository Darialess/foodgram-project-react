[![foodgram workflow](https://github.com/Darialess/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)](https://github.com/Darialess/foodgram-project-react/actions/workflows/foodgram-workflow.yml)

### Опиcание проекта.
Сайт Foodgram, «Продуктовый помощник». Это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Инструкции по установке
***- Клонируйте репозиторий:***
```
git@github.com:Darialess/foodgram-project-react.git
```

## Как запустить приложение в контейнере:

В директории создайте файл .env с переменными окружения для работы с базой данных:

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=#имя базы данных
POSTGRES_USER=#логин для подключения к базе данных
POSTGRES_PASSWORD=# пароль для подключения к БД
DB_HOST=название сервиса (контейнера)
DB_PORT=порт для подключения к БД
```

Выполнить команду:
```
docker-compose up
```
Произвести миграции:
```
docker-compose exec backend python manage.py migrate
```
Создать суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
Собрать статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```

Проект доступен по адресу: http://51.250.77.179/
Администратор:
```
логин - blondolly@yandex.ru
пароль - admin
```
Пользователь:
```
логин - anna@mail.ru
пароль - annaanna1985
```