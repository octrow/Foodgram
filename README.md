<h1 align="left"><a href="http://foodgramdjango.ddns.net/">Foodgram</a></h1>
<br/>
![workflow](https://github.com/octrow/foodgram-project-react/actions/workflows/main_prod.yml/badge.svg)
<p align="left">
    <img src="https://img.shields.io/badge/python-3.10.6-blue.svg?style=for-the-badge&logo=python&logoColor=ffdd54" />
    <img src="https://img.shields.io/badge/django-4.2.2-blue.svg?style=for-the-badge&logo=django&logoColor=11F7BB" />
    <img src="https://img.shields.io/badge/django_rest_framework-3.14.0-blue.svg?style=for-the-badge&logo=django&logoColor=ff7171" />
    <img src="https://img.shields.io/badge/nginx-1.19.3-blue.svg?style=for-the-badge&logo=nginx&logoColor=11FF44" />
    <img src="https://img.shields.io/badge/gunicorn-21.2.0-blue.svg?style=for-the-badge&logo=gunicorn&logoColor=11FF44" />
    <img src="https://img.shields.io/badge/docker-24.0.5-blue.svg?style=for-the-badge&logo=docker&logoColor=33AAFF" />
    <img src="https://img.shields.io/badge/postgreSQL-13.0-blue.svg?style=for-the-badge&logo=postgresql&logoColor=66EEFF" />
    <img src="https://img.shields.io/badge/rest_api_version-1.0.0-blue?style=for-the-badge" />
    <img src="https://img.shields.io/badge/CI_CD-github_acions-blue.svg?style=for-the-badge" />
    <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" />
    <img src="https://img.shields.io/github/actions/workflow/status/kluev-evga/foodgram-project-react/main.yml?style=for-the-badge" />
</p>

Это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Стек

- Python 3.10.11
- Django 4.2.5
- Django REST framework 3.14
- Nginx
- Docker
- PostgreSQL

#### Структура репозитория
 * /frontend - файлы, необходимые для сборки фронтенда приложения.
 * /infra — заготовка инфраструктуры проекта: конфигурационный файл nginx и docker-compose.yml.
 * /backend - бэкенд foodgram на Django.
 * /data - список ингредиентов с единицами измерения (json, cvs).
 * /docs - файлы спецификации API.
 * /postman-collection - тесты API

### Сайт и документация API доступена по ссылкам:

```
- http://foodgramdjango.ddns.net/
- http://foodgramdjango.ddns.net/api/docs/
```

### Foodgram - проект позволяет:

#### Для не авторизированных пользователей:
- Создать аккаунт.
- Просматривать рецепты на главной странице.
- Просматривать страницы рецептов.
- Просматривать профили пользователей.
- Фильтровать рецепты по тегам.

#### Для авторизированных пользователей:
- Входить и выходить с сайта (пароль, email)
- Менять свой пароль.
- Создавать, редактировать и удалять свои рецепты
- Всё что могут не авторизированные пользователи
- Работать с личным списком избранного:
- - добавлять рецепты и удалять их 
- - просматривать свою страницу избранных рецептов.
- Работать с личным списком покупок: 
- - добавлять и удалять любые рецепты, 
- - выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку
- Просматривать свою страницу подписок.

#### Для администраторов (в админ-панеле):
- Всё что могут авторизированные пользователи.
- изменять пароль любого пользователя
- создавать, удалять и деактивировать аккаунты пользователей,
- удалять и редактировать любые рецепты 
- добавлять, удалять и редактировать теги
- добавлять, удалять и редактировать ингредиенты

## Инструкции по установке
### Локальная установка
1. Клонируйте репозиторий:
```
git clone git@github.com:octrow/foodgram-project-react.git
cd foodgram-project-react
```

2. В корневом каталоге создайте файл .env, с переменными окружения.

3. Создайте виртуальное окружение:
```
python -m venv venv
```
4. Активируйте виртуальное окружение
* для Linux/Mac:
```source venv/bin/activate```

* для Windows:
```source venv/Scripts/activate```

4. Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
5. В foodgram/setting.py замените PostgreSQL на встроенную SQLite:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

6. Примените миграции:
```
python manage.py makemigrations
python manage.py migrate
```
7. Соберите статику:
```
python manage.py collectstatic --no-input
```
8. Создайте суперпользователя:
```
python manage.py createsuperuser
```
9. Загрузите данные в модель (ингредиенты):
```
python manage.py load
```
10. В папке с файлом manage.py выполните команду для запуска локально:
```
python manage.py runserver
```
Локально документация доступна по адресу:
```
http://127.0.0.1:8000/api/docs/
```

### Запуск проекта в контейнерах:

1. Установить docker и docker-compose.
[Инструкция по установки (Win/Mac/Linux)](https://docs.docker.com/compose/install/)

- Linux:
```
sudo apt install curl                                   
curl -fsSL https://get.docker.com -o get-docker.sh      
sh get-docker.sh                                        
sudo apt-get install docker-compose-plugin              
```


2. Cоздайте и заполните .env файл в корневом каталоге 
```
SECRET_KEY=django-insecure-**************************************
DEBUG=True
ALLOWED_HOSTS=ip-адрес-сервера,127.0.0.1,localhost,адрес-сайте.ру
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
# Django
DB_HOST=db
DB_PORT=5432
DB_NAME=postgram
```

3. Из папки infra/ разверните контейнеры при помощи docker-compose:
```
docker-compose up -d --build
```
4. Выполните миграции:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```
5. Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
6. Соберите статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
7. Наполните базу данных (ингредиентами). 
```
docker-compose exec backend python manage.py load
```
Проект доступен по адресу:

```
http://localhost/
```
Документация доступна по адресу:
```
http://localhost/api/docs/
```
8. Остановка проекта:
```
docker-compose down
```

<details>
<summary>Краткий список эндпоинтов API:</summary>

- /api/users/ - список пользователей (page, limit), регистрация (email, username, first_name, last_name, password), профиль (id), текущий, изменение пароля (new_password, current_password), получение и удаление токена (password, email).
- /api/tags/ - список тегов, получение тега (id).
- /api/recipes/ - список рецептов (page, limit, is_favorited, is_in_shopping_cart, author, tags), создание (ingredients, tags, image, name, text, cooking_time), получение (id), обновление (id, ingredients, tags, image, name, text, cooking_time), удаление (id).
- /api/recipes/download_shopping_cart/ - скачать список покупок.
- /api/recipes/{id}/shopping_cart/ - добавить или удалить рецепт из списка покупок.
- /api/recipes/{id}/favorite/ - добавить или удалить рецепт из избранного.
- /api/users/subscriptions/ - мои подписки (page, limit, recipes_limit).
- /api/users/{id}/subscribe/ - подписаться или отписаться от пользователя (recipes_limit).
- /api/ingredients/ - список ингредиентов (name), получение ингредиента (id).
</details>

<details>
<summary>Подробное описание API</summary>


| Эндпоинт | Запрос | Параметры | Ответ |
| --- | --- | --- | --- |
| Пользователи | Список пользователей | GET /api/users/ | page (номер страницы), limit (количество объектов на странице) | 200 (JSON-объект с полями count, next, previous и results) |
|  | Регистрация пользователя | POST /api/users/ | email, username, first_name, last_name, password (все обязательные) | 201 (JSON-объект с полями email, id, username, first_name и last_name) или 400 (ошибки валидации) |
|  | Профиль пользователя | GET /api/users/{id}/ | id (уникальный id пользователя) | 200 (JSON-объект с полями email, id, username, first_name, last_name и is_subscribed) или 401 (пользователь не авторизован) или 404 (объект не найден) |
|  | Текущий пользователь | GET /api/users/me/ | - | 200 (JSON-объект с полями email, id, username, first_name, last_name и is_subscribed) или 401 (пользователь не авторизован) |
|  | Изменение пароля | POST /api/users/set_password/ | new_password, current_password (все обязательные) | 204 (пароль успешно изменен) или 400 (ошибки валидации) или 401 (пользователь не авторизован) |
| Авторизация | Получить токен авторизации | POST /api/auth/token/login/ | password, email (все обязательные) | 201 (JSON-объект с полем auth_token) |
|  | Удаление токена | POST /api/auth/token/logout/ | - | 204 (токен удален) или 401 (пользователь не авторизован) |
| Теги | Список тегов | GET /api/tags/ | - | 200 (JSON-массив объектов с полями id, name, color и slug) |
|  | Получение тега | GET /api/tags/{id}/ | id (уникальный id тега) | 200 (JSON-объект с полями id, name, color и slug) или 404 (объект не найден) |
| Рецепты | Список рецептов | GET /api/recipes/ | page, limit, is_favorited, is_in_shopping_cart, author, tags (опциональные) | 200 (JSON-объект с полями count, next, previous и results) |
|  | Создание рецепта | POST /api/recipes/ | ingredients, tags, image, name, text, cooking_time (все обязательные) | 201 (JSON-объект с полями id, tags, author, ingredients, is_favorited, is_in_shopping_cart, name, image, text и cooking_time) или 400 (ошибки валидации) или 401 (пользователь не авторизован) |
|  | Получение рецепта | GET /api/recipes/{id}/ | id (уникальный id рецепта) | 200 (JSON-объект с полями id, tags, author, ingredients, is_favorited, is_in_shopping_cart, name, image, text и cooking_time) |
|  | Обновление рецепта | PATCH /api/recipes/{id}/ | id (уникальный id рецепта), ingredients, tags, image, name, text, cooking_time (все обязательные) | 200 (JSON-объект с полями id, tags, author, ingredients, is_favorited, is_in_shopping_cart, name, image,text и cooking_time) или 400(ошибки валидации) или 401(пользователь не авторизован) или403(недостаточно прав) или 404(объект не найден) |
| Подписки | Мои подписки | GET /api/users/subscriptions/ | page, limit, recipes_limit (опциональные) | 200 (JSON-объект с полями count, next, previous и results, где каждый элемент results содержит поля id, email, username, first_name, last_name и recipes (JSON-массив объектов с полями id, name, image и cooking_time)) или 401 (пользователь не авторизован) |
|  | Подписаться на пользователя | POST /api/users/{id}/subscribe/ | id (уникальный id пользователя) | 201 (JSON-объект с полями id, email, username, first_name и last_name) или 400 (ошибка подписки) или 401 (пользователь не авторизован) |
|  | Отписаться от пользователя | DELETE /api/users/{id}/subscribe/ | id (уникальный id пользователя) | 204 (подписка успешно удалена) или 400 (ошибка отписки) или 401 (пользователь не авторизован) |
| Ингредиенты | Список ингредиентов | GET /api/ingredients/ | name (опциональный, поиск по частичному вхождению в начале названия ингредиента) | 200 (JSON-массив объектов с полями id, name и measurement_unit) |
|  | Получение ингредиента | GET /api/ingredients/{id}/ | id (уникальный id ингредиента) | 200 (JSON-объект с полями id, name и measurement_unit) или 404 (объект не найден) |

</details>

### Контакты
Если у вас есть вопросы или пожелания по проекту, вы можете написать мне:
[GitHub](https://github.com/octrow)
