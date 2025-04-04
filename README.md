# Название проекта: Продуктовый помощник Foodgram

## Автор проект
* [Alexander Batogov](https://github.com/Predatorevil666)

## Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)

## Описание проекта Foodgram
«Продуктовый помощник»:  сайт, на котором пользователи будут публиковать свои рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Роли пользователей:
- **Неавторизованные пользователи:** могут просматривать рецепты и страницы пользователей.
- **Авторизованные пользователи:** имеют доступ ко всем возможностям, включая создание рецептов, добавление в избранное и покупки, подписки на публикации авторов рецептов. 
- **Администраторы:** полный контроль над системой, включая редактирование и удаление любого контента.



### Развертывание проекта на локальном компьютере в Docker-контейнерах
1. Клонируете репозиторий:
   ```bash
   git clone https://github.com/Predatorevil666/foodgram.git
   mkdir foodgram
   cd foodgram
   ```

Создать `.env` файл с переменными окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432
```

Собрать и запустить контейнеры:
```bash
sudo docker-compose up
```

Выполнить миграции внутри контейнера `backend`:
```bash
sudo docker-compose exec backend python manage.py migrate
```

Собрать статику проекта внутри контейнера `backend`:
```bash
sudo docker-compose exec backend python manage.py collectstatic --noinput
```

Создать суперпользователя для админ-панели внутри контейнера `backend`:
```bash
sudo docker-compose exec backend python manage.py createsuperuser
```

Заполнить БД ингредиентами и тегами внутри контейнера `backend`:
```bash
sudo docker-compose exec backend python manage.py loaddb
```

### Развертывание проекта на удаленном сервере c CI/CD GitHub Actions

### Для работы с Workflow GitHub Actions необходимо добавить в GitHub Secrets переменные окружения:
```
DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
SSH_PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
SSH_PORT=<порт сервера, если был изменен>

TELEGRAM_TOKEN: Токен бота, полученный у @BotFather.
TELEGRAM_TO: ID телеграм-аккаунта для отправки уведомлений. Можно узнать у @userinfobot, отправив команду `/start`.
```

### Подготовить удаленный сервер
1. Подключитесь к удаленному серверу

    ```bash
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ```

2. Установка docker compose на сервер:

    ```bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
    ```



3. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env:

    ```bash
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
    scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/foodgram/.env

    * path_to_SSH — путь к файлу с SSH-ключом;
    * SSH_name — имя файла с SSH-ключом (без расширения);
    * username — ваше имя пользователя на сервере;
    * server_ip — IP вашего сервера.
    ```
4. Запустите docker compose в режиме демона:

    ```bash
    sudo docker compose -f docker-compose.production.yml up -d
    ```

