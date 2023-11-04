<h1 align="left"><a href="http://foodgramdjango.ddns.net/">Foodgram</a></h1>
<br/>
<p align="left">
    <img src="https://img.shields.io/badge/python-3.10.11-blue.svg?style=for-the-badge&logo=python&logoColor=ffdd54" />
    <img src="https://img.shields.io/badge/django-4.2.5-blue.svg?style=for-the-badge&logo=django&logoColor=11F7BB" />
    <img src="https://img.shields.io/badge/django_rest_framework-3.14.0-blue.svg?style=for-the-badge&logo=django&logoColor=ff7171" />
    <img src="https://img.shields.io/badge/nginx-1.19.3-blue.svg?style=for-the-badge&logo=nginx&logoColor=11FF44" />
    <img src="https://img.shields.io/badge/gunicorn-21.2.0-blue.svg?style=for-the-badge&logo=gunicorn&logoColor=11FF44" />
    <img src="https://img.shields.io/badge/docker-24.0.5-blue.svg?style=for-the-badge&logo=docker&logoColor=33AAFF" />
    <img src="https://img.shields.io/badge/postgreSQL-13.0-blue.svg?style=for-the-badge&logo=postgresql&logoColor=66EEFF" />
    <img src="https://img.shields.io/badge/rest_api_version-1.0.0-blue?style=for-the-badge" />
    <img src="https://img.shields.io/badge/CI_CD-github_acions-blue.svg?style=for-the-badge" />
    <img src="https://img.shields.io/github/actions/workflow/status/octrow/Foodgram/main_prod.yml?style=for-the-badge" />
</p>

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/octrow/Foodgram/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yellow.svg)](https://github.com/octrow/Foodgram/blob/master/README.RU.md)

This is an online service and an API for it. On this service, users can publish recipes, subscribe to the publications of other users, add liked recipes to the "Favorites" list, and before going to the store, download a summary list of products needed to prepare one or several selected dishes.

### Stack

- Python 3.10.11
- Django 4.2.5
- Django REST framework 3.14
- Nginx
- Docker
- PostgreSQL

#### Repository structure
 * /frontend - files needed to build the frontend of the application.
 * /infra - infrastructure template of the project: nginx configuration file and docker-compose.yml.
 * /backend - foodgram backend on Django.
 * /data - list of ingredients with units of measurement (json, cvs).
 * /docs - API specification files.
 * /postman-collection - API tests

### Site and API documentation are available at the links:

```
- http://foodgramdjango.ddns.net/
- http://foodgramdjango.ddns.net/api/docs/
```

### Foodgram - project allows:

#### For unauthenticated users:
- Create an account.
- View recipes on the main page.
- View recipe pages.
- View user profiles.
- Filter recipes by tags.

#### For authenticated users:
- Log in and out of the site (password, email)
- Change your password.
- Create, edit and delete your recipes
- Everything that unauthenticated users can do
- Work with your personal list of favorites:
- - add and delete recipes 
- - view your page of favorite recipes.
- Work with your personal shopping list: 
- - add and delete any recipes, 
- - download a file with the number of necessary ingredients for recipes from the shopping list.
- Subscribe to the publications of recipe authors and cancel the subscription
- View your subscription page.

#### For administrators (in the admin panel):
- Everything that authenticated users can do.
- change the password of any user
- create, delete and deactivate user accounts,
- delete and edit any recipes 
- add, delete and edit tags
- add, delete and edit ingredients

## Installation instructions
### Local installation
1. Clone the repository:
```
git clone git@github.com:octrow/foodgram-project-react.git
cd foodgram-project-react
```

2. In the root directory, create a .env file with environment variables.

3. Create a virtual environment:
```
python -m venv venv
```
4. Activate the virtual environment
* for Linux/Mac:
```source venv/bin/activate```

* for Windows:
```source venv/Scripts/activate```

4. Install dependencies from the requirements.txt file:

```
pip install -r requirements.txt
```
5. In foodgram/setting.py replace PostgreSQL with the built-in SQLite:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

6. Apply migrations:
```
python manage.py makemigrations
python manage.py migrate
```
7. Collect static:
```
python manage.py collectstatic --no-input
```
8. Create a superuser:
```
python manage.py createsuperuser
```
9. Load data into the model (ingredients):
```
python manage.py load
```
10. In the folder with the manage.py file, run the command to run locally:
```
python manage.py runserver
```
Locally, the documentation is available at:
```
http://127.0.0.1:8000/api/docs/
```

### Running the project in containers:

1. Install docker and docker-compose.
[Installation instructions (Win/Mac/Linux)](https://docs.docker.com/compose/install/)

- Linux:
```
sudo apt install curl                                   
curl -fsSL https://get.docker.com -o get-docker.sh      
sh get-docker.sh                                        
sudo apt-get install docker-compose-plugin              
```


2. Create and fill in the .env file in the root directory
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

3. From the infra/ folder, deploy the containers using docker-compose:
```
docker-compose up -d --build
```
4. Perform migrations:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```
5. Create a superuser:
```
docker-compose exec backend python manage.py createsuperuser
```
6. Collect static:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
7. Populate the database (with ingredients).
```
docker-compose exec backend python manage.py load
```
The project is available at:

```
http://localhost/
```
The documentation is available at:
```
http://localhost/api/docs/
```
8. Stop the project:
```
docker-compose down
```

<details>
<summary>A brief list of API endpoints:</summary>

- /api/users/ - list of users (page, limit), registration (email, username, first_name, last_name, password), profile (id), current, change password (new_password, current_password), get and delete token (password, email).
- /api/tags/ - list of tags, get tag (id).
- /api/recipes/ - list of recipes (page, limit, is_favorited, is_in_shopping_cart, author, tags), create (ingredients, tags, image, name, text, cooking_time), get (id), update (id, ingredients, tags, image, name, text, cooking_time), delete (id).
- /api/recipes/download_shopping_cart/ - download shopping list.
- /api/recipes/{id}/shopping_cart/ - add or remove recipe from shopping list.
- /api/recipes/{id}/favorite/ - add or remove recipe from favorites.
- /api/users/subscriptions/ - my subscriptions (page, limit, recipes_limit).
- /api/users/{id}/subscribe/ - subscribe or unsubscribe from user (recipes_limit).
- /api/ingredients/ - list of ingredients (name), get ingredient (id). </details>
</details>

<details>
<summary>Detailed description of API</summary>


| Endpoint    | Request | Parameters | Response                                                                                        |
|-------------| --- | --- |-------------------------------------------------------------------------------------------------|
| Users       | List of users | GET /api/users/ | page (page number), limit (number of objects per page)                                          | 200 (JSON-object с полями count, next, previous и results) |
|             | User registration | POST /api/users/ | email, username, first_name, last_name, password (all required)                                 | 201 (JSON-объект с полями email, id, username, first_name и last_name) или 400 (ошибки валидации) |
|             | User profile | GET /api/users/{id}/ | id (unique id of the user)                                                                      | 200 (JSON-object с полями email, id, username, first_name, last_name и is_subscribed) или 401 (пользователь не авторизован) или 404 (объект не найден) |
|             | Current user | GET /api/users/me/ | -                                                                                               | 200 (JSON-object с полями email, id, username, first_name, last_name и is_subscribed) или 401 (пользователь не авторизован) |
|             | 	Change password | POST /api/users/set_password/ | new_password, current_password (all required)                                                   | 204 (пароль успешно изменен) или 400 (ошибки валидации) или 401 (пользователь не авторизован) |
| Authorization | Get authorization token | POST /api/auth/token/login/ | password, email (all required)                                                                  | 201 (JSON-объект с полем auth_token) |
|             | Delete token | POST /api/auth/token/logout/ | -                                                                                               | 204 (токен удален) или 401 (пользователь не авторизован) |
| Tags        | 	List of tags | GET /api/tags/ | -                                                                                               | 200 (JSON-массив объектов с полями id, name, color и slug) |
|             | 	Get tag | GET /api/tags/{id}/ | 	id (unique id of the tag)                                                                      | 200 (JSON-объект с полями id, name, color и slug) или 404 (объект не найден) |
| Recipes     | List of recipes | GET /api/recipes/ | page, limit, is_favorited, is_in_shopping_cart, author, tags (опциональные)                     | 200 (JSON-объект с полями count, next, previous и results) |
|             | Create recipe | POST /api/recipes/ | ingredients, tags, image, name, text, cooking_time (all required)                               | 201 (JSON-объект с полями id, tags, author, ingredients, is_favorited, is_in_shopping_cart, name, image, text и cooking_time) или 400 (ошибки валидации) или 401 (пользователь не авторизован) |
|             | Get recipe | GET /api/recipes/{id}/ | id (unique id of the recipe)                                                                    | 200 (JSON-объект с полями id, tags, author, ingredients, is_favorited, is_in_shopping_cart, name, image, text и cooking_time) |
|             | Update recipe | PATCH /api/recipes/{id}/ | id (unique id of the recipe), ingredients, tags, image, name, text, cooking_time (all required) | 200 (JSON-объект с полями id, tags, author, ingredients, is_favorited, is_in_shopping_cart, name, image,text и cooking_time) или 400(ошибки валидации) или 401(пользователь не авторизован) или403(недостаточно прав) или 404(объект не найден) |
| Subscriptions    | My subscriptions | GET /api/users/subscriptions/ | page, limit, recipes_limit (опциональные)                                                       | 200 (JSON-объект с полями count, next, previous и results, где каждый элемент results содержит поля id, email, username, first_name, last_name и recipes (JSON-массив объектов с полями id, name, image и cooking_time)) или 401 (пользователь не авторизован) |
|             | 	Subscribe to user | POST /api/users/{id}/subscribe/ | id (unique id of the user)                                                                      | 201 (JSON-объект с полями id, email, username, first_name и last_name) или 400 (ошибка подписки) или 401 (пользователь не авторизован) |
|             | 	Unsubscribe from user | DELETE /api/users/{id}/subscribe/ | id (unique id of the user)                                                                      | 204 (подписка успешно удалена) или 400 (ошибка отписки) или 401 (пользователь не авторизован) |
| Ingredients | List of ingredients	 | GET /api/ingredients/ | name (optional, search by partial match at the beginning of the ingredient name)                | 200 (JSON-массив объектов с полями id, name и measurement_unit) |
|             | Get ingredient | GET /api/ingredients/{id}/ | id (unique id of the ingredient)                                                                | 200 (JSON-объект с полями id, name и measurement_unit) или 404 (объект не найден) |

</details>

### Contacts
If you have any questions or queries about the project, you can write to me:
[GitHub](https://github.com/octrow)
