from django.core.management.base import BaseCommand, CommandError
from telebot import TeleBot, types
from telebot.types import InputMediaPhoto
from bot.models import *
from bot import views
# from bot.views import get_message
#import FlowerShop.settings
#from FlowerShop.settings import TELEGRAM_TOKEN, FLORISTS_CHAT_ID, COURIERS_CHAT_ID


TELEGRAM_TOKEN = '6078909031:AAGN2OPnKOQfF_rokd3Sjvu5RmCnBEC-4dQ'
FLORISTS_CHAT_ID = -952806675
COURIERS_CHAT_ID = -952806675
ORDERS_IN_PROCESS = {}
'''
ORDERS_IN_PROCESS = {
  'id': {
    'cause_id': int,
    'price': int,
    'bouquets': QuerySet
  }
}

'''


CAUSES = [
    'День Рождения',
    'Свадьба',
    'В школу',
    'Другой повод'
]
PRICES = [
    1000,
    2000,
    3000,
    4000,
    5000
]
BOUQUETS = [
    {
        'id': 1,
        'name': 'букет 1',
        'price': 2600,
        'image': 'media\\bouquets\\bouquet_1',
        'description': 'описание 1',
        'flowers': [
            'Роза',
            'Гвоздика',
            'Рускус'
            ]
    },
    {
        'id': 4,
        'name': 'букет 2',
        'price': 3100,
        'image': 'media\\bouquets\\bouquet_2',
        'description': 'описание 4',
        'flowers': [
            'Аспидистра',
            'Краспендия',
            'Хризантема',
            'Гвоздика'
        ]
    },
    {
        'id': 8,
        'name': 'букет 3',
        'price': 2900,
        'image': 'media\\bouquets\\bouquet_3',
        'description': 'описание 8',
        'flowers': [
            'Роза кустовая',
            'Роза',
            'Краспендия'
        ]
    },
    {
        'id': 11,
        'name': 'букет 4',
        'price': 3400,
        'image': 'media\\bouquets\\bouquet_4',
        'description': 'описание 11',
        'flowers': [
            'Гербера',
            'Питоспорум',
            'Статица'
        ]
    },
    {
        'id': 12,
        'name': 'букет 5',
        'price': 3300,
        'image': 'media\\bouquets\\bouquet_5',
        'description': 'описание 12',
        'flowers': [
            'Питоспорум',
            'Аспидистра',
            'Тюльпан'
        ]
    }
]


def get_message(bouquet: dict):
    message = f'Букет \"{bouquet["name"]}\"\n' \
              f'Цена: {bouquet["price"]} руб.' \
              f'{bouquet["description"]}' 
    for flower in bouquet['flowers']:
        message += f'\n- {flower}'
    return message


bot = TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def main_menu(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    client = Client.objects.get_or_create(
        client_id=message.chat.id,
        defaults={
            'client_name': message.from_user.username
        }
        )
    # client.save()
    # функция, проверяющая, есть ли у клиента с данным id незавершенные заказы, и удаляющая их
    id_tg=message.from_user.id
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Заказать букет',
                                        callback_data=f'bouquet_params;choose_cause')
    markup.add(button)
    bot.send_message(message.chat.id,
                     f'Добро пожаловать! {client[0]} Выберите действие: ',
                     reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: True) #call.data.startswith('bouquet')
@bot.callback_query_handler(
    func=lambda call: call.data.startswith('bouquet_params')
)
def bouquet_params_menu(call):
    callback_data = call.data.split(';')
    # client_id = call.message.from_user.id - выдаеь id бота
    client_chat_id = call.message.chat.id

    if callback_data[1] == 'main_menu':
        main_menu(call.message)
    if callback_data[1] == 'choose_cause':
        choose_cause(call.message)
    if callback_data[1] == 'choose_price':
        ORDERS_IN_PROCESS.update([(
            client_chat_id,
            {
                'cause_id': callback_data[2]
            }
        )])
        choose_price(call.message)
    if callback_data[1] == 'second_menu':
        if not ORDERS_IN_PROCESS[client_chat_id].get('approx_price'):
            ORDERS_IN_PROCESS[client_chat_id]['approx_price'] = callback_data[2]
        second_menu(call.message, client_chat_id)
    if callback_data[1] == 'notify_florist':
        notify_florist(call.message)
    if callback_data[1] == 'bouquet_presentation_menu':
        cause_id = callback_data[1]
        price = callback_data[2]
        bouquet_presentation_menu(call.message, cause_id, price)



def choose_cause(message):
    # запрос к бд
    # фильтр к таблице букетов на уникальные значения поводов

    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cause}', 
            callback_data=f'bouquet_params;choose_price;{cause}'
        ) 
        for cause in CAUSES
    ]
    for button in buttons:
        markup.add(button)
    bot.send_message(message.chat.id,
                     'К какому событию готовимся? '
                     'Выберите один из вариантов, либо укажите свой',
                     reply_markup=markup)


def choose_price(message):
    # запрос к бд
    # функция, возвращает лист приблизительных цен с шагом по 1000

    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=f'~{price} руб.', 
            callback_data=f'bouquet_params;second_menu;{price}'
        )
        for price in PRICES
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     'На какую сумму рассчитываете?',
                     reply_markup=markup)


def second_menu(message, client_chat_id):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Посмотреть букеты',
                                          callback_data=f'bouquet_presentation_menu'),
               types.InlineKeyboardButton(text='Связаться с флористом',
                                          callback_data=f'bouquet_params;notify_florist')]
    markup.add(*buttons)

    cause_id = ORDERS_IN_PROCESS[client_chat_id]['cause_id']
    approx_price = ORDERS_IN_PROCESS[client_chat_id]['approx_price']
    bot.send_message(message.chat.id,
                     f'Вы выбрали:\n повод: {cause_id}\n цена: {approx_price}\n'
                     'Предпочитаете посмотреть готовые букеты или обратиться к флористу?',
                     reply_markup=markup)


def notify_florist(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Отмена',
                                        callback_data=f'bouquet_params;second_menu;')
    markup.add(button)
    msg = bot.send_message(message.chat.id,
                           'Укажите номер телефона, и наш флорист перезвонит вам в течение 20 минут',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, florist_notified)


def get_florist_message(message):
    client_chat_id = message.chat.id
    cause_id = ORDERS_IN_PROCESS[client_chat_id]['cause_id']
    approx_price = ORDERS_IN_PROCESS[client_chat_id]['approx_price']
    msg = 'Сообщение для флориста: \n\n' \
          f'Клиент № client.id\n' \
          f'ТГ ссылка: tg://user?id={message.chat.id}\n' \
          f'Телефон: {message.text}\n' \
          f'Предпочтения:\n  повод: {cause_id}\n  цена: ~ {approx_price} руб.'
    return msg


def florist_notified(message):
    # client.id заменить на id клиента из БД
    # сделать проверку телефона как в задании про риелторов?
    # если делать, то сделать функцию для некорректно введенного номера
    msg = get_florist_message(message)
    bot.send_message(FLORISTS_CHAT_ID, msg)

    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Посмотреть букеты',
                                          callback_data=f'bouquet_presentation_menu'),
               types.InlineKeyboardButton(text='Главное меню',
                                          callback_data=f'bouquet_params;main_menu')]
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     'Флорист скоро свяжется с вами. '
                     'А пока можете присмотреть что-нибудь из готовой коллекции',
                     reply_markup=markup)




def get_new_bouquet_num(last_num: int, direction, max_set_num: int):
    if(direction == 'next'):
        return last_num + 1 if max_set_num != last_num else 0
    else:
        return last_num - 1 if last_num != 0 else max_set_num


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('bouquet_presentation_menu')
) 
def bouquet_presentation_menu(call):
    callback_data = call.data.split(';')
    client_chat_id = call.message.chat.id
    bouquet_set = ORDERS_IN_PROCESS.get(client_chat_id)

    if len(callback_data) == 1:
        # фильтр к таблице букетов по наличию, cause_id и approx_price(ap-500 < price < ap+500)
        # отсортировать по Bouquet.id
        bouquet_set['bouquets'] = BOUQUETS
        new_num = 0
        # проверить bouquet_set['bouquets'] на пустоту?
        # если пусто, начать сначала, с функции choose_cause?
    else:
        # проверить bouquet_set['bouquets'] на пустоту?
        # при QuerySet вместо len(х) использовать х.count()
        new_num = get_new_bouquet_num(
            int(callback_data[1]), 
            callback_data[2],
            len(bouquet_set['bouquets']) - 1
        )
        
    bouquet = bouquet_set['bouquets'][new_num]
    # bouquet = bouquet_set['bouquets'][new_num].values()

    markup = types.InlineKeyboardMarkup()
    main_buttons = [types.InlineKeyboardButton(text='◀ Предыдущий',
                                          callback_data=f'bouquet_presentation_menu;{new_num};prev'),
                    types.InlineKeyboardButton(text='Выбрать букет',
                                          callback_data=f'order;name'),
                    types.InlineKeyboardButton(text='Следующий ▶',
                                          callback_data=f'bouquet_presentation_menu;{new_num};next')]
    button = types.InlineKeyboardButton(text='Связаться с флористом',
                                        callback_data=f'bouquet_params;notify_florist')
    markup.add(*main_buttons)
    markup.add(button)

    # image = InputMediaPhoto(bouquet.image) if bouquet.image else None
    # if image:
    #     bot.send_photo(call.message.chat.id, photo=image)
    bot.send_message(call.message.chat.id,
                     get_message(bouquet),
                     reply_markup=markup)




@bot.callback_query_handler(
    func=lambda call: call.data.startswith('order')
)
def order_menu(call):
    callback_data = call.data.split(';')

    if callback_data[1] == 'name':
        set_name(call.message)


def set_name(message):
    print(message)








class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        try:
            bot.polling(none_stop=True)
        except Poll.DoesNotExist:
            raise CommandError()

bot.polling(none_stop=True)

        #bot.infinity_polling()







