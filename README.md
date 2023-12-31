# FlowerShop

Бот, созданный для комфортной продажи и покупки цветов.

Для покупателя:

Позволяет подбирать букет под себя, исходя из стоимости букета и повода.
Также есть возможность связаться с флористом для создания уникального букета.

Для продавца:

Удобная возможность создавать базу данных с букетами, а после редактировать ее в любой момент.
Быстрая связь с курьерами и флористами, так как все необходимые данные о заказе попадают сразу в рабочий Телеграм чат.


### Содержание

- [Как установить](#как-установить)
- [Как запустить](#как-запустить)


### Как установить
Для запуска вам понадобится Python третьей версии.

Скачайте код с GitHub. Установите зависимости:

```sh
pip install -r requirements.txt
```

Создайте файл **.env** вида:
```properties
TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN
PAYMENT_TOKEN=YOUR_PAYMENTS_TOKEN
BOT_LINK=YOUR_BOT_LINK
FLORISTS_CHAT_ID=-912381131
COURIERS_CHAT_ID=-123121231
```
Получить токен для Телеграм бота и подключить к нему оплату вы можете через [BotFather](https://telegram.me/BotFather).
Также необходимо создать чат в телеграмме(информация о заказах для флористов и курьеров будет попадать именно туда)

Создайте базу данных:

```sh
python3 manage.py makemigrations
python3 manage.py migrate
```
Создайте суперпользователя
```sh
python3 manage.py createsuperuser
```


### Как запустить
Для запуска бота используйте команду
```sh
python manage.py runbot
```

Для запуска административной панели используйте команду
```sh
python manage.py runserver
```
