from django.shortcuts import render, get_object_or_404
from bot.models import Bouquet, Order, Client
from django.db.models import Max, Min


def get_bouquet_description(bouquet: Bouquet):
    message = f'Букет \"{bouquet.name}\"\n' \
              f'Цена: {bouquet.price} руб.' \
              f'{bouquet.description}'
    for flower in bouquet.flowers:
        message += f'\n- {flower}'
    return message


def get_message(bouquet: dict):
    message = f'Букет \"{bouquet["name"]}\"\n' \
              f'Цена: {bouquet["price"]} руб.' \
              f'{bouquet["description"]}'
    for flower in bouquet['flowers']:
        message += f'\n- {flower}'
    return message


def get_description(order: dict, client_id):
    сlient = Client.objects.get(client_id=client_id)
    message = f'Имя: {сlient}\n' \
              f'Адрес: {order["address"]}\n' \
              f'Дата доставки: {order["delivery_date"].strftime("%d.%m.%y")}\n' \
              f'Время доставки: {order["delivery_time"].strftime("%H:%M")}'
    return message


def make_price_list():
    max_price = Bouquet.objects.aggregate(Max("price"))['price__max']
    min_price = Bouquet.objects.aggregate(Min("price"))['price__min']
    approximate_prices = [
        price for price in range(roundup(min_price), max_price, 1000)
    ]
    return approximate_prices


def roundup(x):
    return int(round(x / 1000) * 1000)


def get_new_bouquet_num(last_num: int, direction, max_set_num: int):
    if(direction == 'next'):
        return last_num + 1 if max_set_num != last_num else 0
    else:
        return last_num - 1 if last_num != 0 else max_set_num





