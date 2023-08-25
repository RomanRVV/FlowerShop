from django.shortcuts import render, get_object_or_404
from bot.models import Bouquet


def get_bouquet_description(bouquet: Bouquet):
    message = f'Букет \"{bouquet.name}\"\n'
              f'Цена: {bouquet.price} руб.'
              f'{bouquet.description}'
    # for flower in bouquet.flowers:
    #     message += f'\n- {flower}'


def get_message(bouquet: dict):
    message = f'Букет \"{bouquet["name"]}\"\n' \
              f'Цена: {bouquet["price"]} руб.' \
              f'{bouquet["description"]}'
    for flower in bouquets['flowers']:
        message += f'\n- {flower}'
    return message




