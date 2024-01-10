# Статуworkflow
[![Main Foodgram workflow](https://github.com/N0len-sasha/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/N0len-sasha/foodgram-project-react/actions/workflows/main.yml)

# Описание 
Проект Foodgram представляет собой портал для публикации и обмена различными рецептами. 
Вы можете подписаться на любимого автора, добавить его рецепт в избранное или список покупок,
который позже можно импортировать файлом с ингредиентами, необходимыми для приготовления
требуемых блюд.

# Технологический стек проекта 
`Python` `DJANGO` `Nginx` `Docker-compose` `JavaScript` `React` 
 
# Установка 
## Как развернуть проект на локальной машине 
### Клонировать репозиторий и перейти в него в командной строке 
``` 
  git clone https://github.com/N0len-sasha/kittygram_finae.git 
``` 
``` 
  cd foodgram-project-react 
``` 
### Создать и активировать виртуальное окружение 
``` 
  python -m venv venv 
``` 
``` 
  source venv/Scripts\activate 
``` 
### Установить зависимости 
``` 
cd backend 
``` 
``` 
  pip install -r requirements.txt 
``` 
### Выполнить миграции и загрузить данные
``` 
  python manage.py migrate 
```
``` 
  python manage.py load_data_csv 
```
``` 
  python manage.py create_tags
``` 
### Запустить проект 
``` 
  python manage.py runserver 
``` 
## Создать файл .env 
### Создать файл с названием .env в корне проекта 
### Заполнить его следующим содержимым:
``` 
POSTGRES_USER=n0len
POSTGRES_PASSWORD=2000c08o09Cyny
POSTGRES_DB=foodgram_db

DB_HOST=db
DB_PORT=5432

SECRET_KEY=my_sercet_key
DEBUG=False
ALLOWED_HOSTS=51.250.27.0,127.0.0.1,localhost,foodgramsite.hopto.org
RUN_SQL=True
``` 
# Просмотр документации API

### Переейти в папку infra

```
cd infra
```
### Собрать образы и запустить контейнеры
```
docker compose up
```
### Перейти по ссылке 
```
http://localhost/api/docs/redoc.html
```
 
## Автор 
Платошин Александр Игоревич 
