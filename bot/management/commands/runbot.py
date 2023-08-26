from django.core.management.base import BaseCommand, CommandError
from telebot import TeleBot, types, apihelper
from bot.models import *
from pprint import pprint
from telebot.types import InputMediaPhoto
from bot.views import (make_price_list, get_new_bouquet_num, get_description,
                       get_florist_message, get_courier_message)
from more_itertools import chunked
from datetime import datetime, timedelta
#import FlowerShop.settings
from FlowerShop.settings import TELEGRAM_TOKEN, FLORISTS_CHAT_ID, COURIERS_CHAT_ID, STATIC_ROOT
import os


# TELEGRAM_TOKEN = '6078909031:AAGN2OPnKOQfF_rokd3Sjvu5RmCnBEC-4dQ'
# FLORISTS_CHAT_ID = -952806675
# COURIERS_CHAT_ID = -952806675
ORDERS_IN_PROCESS = {}
'''
ORDERS_IN_PROCESS = {
  'id': {
    'cause': str,
    'price': int,
    'bouquets': QuerySet,
    --------------------
    'chosen_bouquet': Bouquet
    'address': str,
    'delivery_date': date,
    'delivery_time': time,
    'order_id': int,
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


bot = TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def main_menu(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    client = Client.objects.get_or_create(client_id=message.from_user.id)[0]  
    client.save()
    # функция, проверяющая, есть ли у клиента с данным id незавершенные заказы, и удаляющая их
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Заказать букет',
                                        callback_data=f'bouquet_params;choose_cause')
    markup.add(button)
    bot.send_message(message.chat.id,
                     f'Добро пожаловать! Выберите действие: ',
                     reply_markup=markup)


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
            {'cause_id': callback_data[2]}
        )])
        choose_price(call.message)
    if callback_data[1] == 'second_menu':
        if not ORDERS_IN_PROCESS[client_chat_id].get('approx_price'):
            ORDERS_IN_PROCESS[client_chat_id]['approx_price'] = int(callback_data[2])
        second_menu(call.message, client_chat_id)
    if callback_data[1] == 'notify_florist':
        notify_florist(call.message)


def choose_cause(message):
    # запрос к бд+
    # фильтр к таблице букетов на уникальные значения поводов+

    causes = Event.objects.filter(bouquets_for_event__in=Bouquet.objects.all()).distinct()
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cause}', 
            callback_data=f'bouquet_params;choose_price;{cause.name}'
        ) 
        for cause in causes
    ]
    for button in buttons:
        markup.add(button)
    bot.send_message(message.chat.id,
                     'К какому событию готовимся? '
                     'Выберите один из вариантов, либо укажите свой',
                     reply_markup=markup)


def choose_price(message):
    # запрос к бд+
    # функция, возвращает лист приблизительных цен с шагом по 1000+
    prices = make_price_list()

    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=f'~{price} руб.', 
            callback_data=f'bouquet_params;second_menu;{price}'
        )
        for price in prices
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


def florist_notified(message):
    # сделать проверку телефона как в задании про риелторов?
    # если делать, то сделать функцию для некорректно введенного номера
    msg = get_florist_message(message, ORDERS_IN_PROCESS[message.chat.id])
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




@bot.callback_query_handler(
    func=lambda call: call.data.startswith('bouquet_presentation_menu')
) 
def bouquet_presentation_menu(call):
    callback_data = call.data.split(';')
    client_chat_id = call.message.chat.id
    bouquet_set = ORDERS_IN_PROCESS.get(client_chat_id)
    is_first_call = (len(callback_data) == 1)
    
    if is_first_call:
        bouquet_set['bouquets'] = Bouquet.objects.filter(
            events__name=bouquet_set['cause_id'],
            price__lte=int(bouquet_set['approx_price']) + 500,
            price__gte=int(bouquet_set['approx_price']) - 500,
            in_stock=True
        ).order_by('id')
        new_num = 0
        # проверить bouquet_set['bouquets'] на пустоту?
        # если пусто, начать сначала, с функции choose_cause?
    else:
        # проверить bouquet_set['bouquets'] на пустоту?
        new_num = get_new_bouquet_num(
            int(callback_data[1]), 
            callback_data[2],
            bouquet_set['bouquets'].count() - 1
        )

    bouquet = bouquet_set['bouquets'][new_num]
    markup = types.InlineKeyboardMarkup()
    main_buttons = [types.InlineKeyboardButton(text='◀ Предыдущий',
                                          callback_data=f'bouquet_presentation_menu;{new_num};prev'),
                    types.InlineKeyboardButton(text='Выбрать букет',
                                          callback_data=f'order;start_order;{new_num}'),
                    types.InlineKeyboardButton(text='Следующий ▶',
                                          callback_data=f'bouquet_presentation_menu;{new_num};next')]
    button = types.InlineKeyboardButton(text='Связаться с флористом',
                                        callback_data=f'bouquet_params;notify_florist')
    markup.add(*main_buttons)
    markup.add(button)

    if is_first_call:
        bot.send_photo(call.message.chat.id,
                       photo=bouquet.image,
                       caption=bouquet.get_message(),
                       reply_markup=markup)
    else:
        image = InputMediaPhoto(media=open(f'{bouquet.image}', 'rb'), caption=bouquet.get_message())
        bot.edit_message_media(media=image,
                               chat_id=call.message.chat.id,
                               message_id=call.message.id,
                               reply_markup=markup)




@bot.callback_query_handler(
    func=lambda call: call.data.startswith('order')
)
def order_menu(call):
    callback_data = call.data.split(';')
    client_chat_id = call.message.chat.id

    if callback_data[1] == 'start_order':
        start_order(call.message, int(callback_data[2]))
    if callback_data[1] == 'ask_name':
        ask_name(call.message)
    if callback_data[1] == 'set_delivery_date':
        set_delivery_date(call.message, callback_data[2])
    if callback_data[1] == 'set_delivery_time':
        set_delivery_time(call.message, callback_data[2])
    if callback_data[1] == 'create_order':
        accept_order(client_chat_id)
        offer_payment_types(call.message)
    if callback_data[1] == 'pay_order':
        pay_order(call.message)
    if callback_data[1] == 'courier_notified':
        is_paid = True if callback_data[2] == 'True' else False
        courier_notified(call.message, is_paid)


def start_order(message, chosen_num):
    client_id = message.chat.id
    bouquet_set = ORDERS_IN_PROCESS.get(client_id)
    chosen_bouquet = bouquet_set['bouquets'][chosen_num]
    ORDERS_IN_PROCESS.update([(
        client_id, 
        {'chosen_bouquet': chosen_bouquet}
    )])
    ask_name(message)


def ask_name(message):
    msg = bot.send_message(message.chat.id, 'На кого будет заказ?\nВведите имя')
    bot.register_next_step_handler(msg, set_name)


def set_name(message):
    # client = Client.objects.get(client_id=message.chat.id)
    # client.client_name = message.text
    client = Client.objects.update_or_create(client_id=message.chat.id,
                                             defaults={'client_name': message.text})[0]  
    client.save()

    msg = bot.send_message(message.chat.id, 'Введите адрес доставки')
    bot.register_next_step_handler(msg, set_address)


def set_address(message):
    ORDERS_IN_PROCESS[message.chat.id]['address'] = message.text

    today = datetime.today()
    date_list = [today + timedelta(days=x) for x in range(1, 6)]

    buttons = [types.InlineKeyboardButton(
                    text=f'{date.strftime("%d.%m")}',
                    callback_data=f'order;set_delivery_date;{date.strftime("%d.%m.%Y")};'
                ) for date in date_list]
    markup = types.InlineKeyboardMarkup()

    buttons = list(chunked(buttons, 3))
    for button_set in buttons:
        markup.add(*button_set)
    bot.send_message(message.chat.id, 'Укажите дату доставки', reply_markup=markup)


def set_delivery_date(message, date_str):
    date = datetime.strptime(date_str, "%d.%m.%Y")
    ORDERS_IN_PROCESS[message.chat.id]['delivery_date'] = date

    time = datetime.strptime('10.00', '%H.%M')
    time_list = [time + timedelta(hours=x) for x in range(9)]

    buttons = [types.InlineKeyboardButton(
                    text=f'{time.strftime("%H:%M")}',
                    callback_data=f'order;set_delivery_time;{time.strftime("%H:%M")};'
                ) for time in time_list]
    markup = types.InlineKeyboardMarkup()

    buttons = list(chunked(buttons, 3))
    for button_set in buttons:
        markup.add(*button_set)
    bot.send_message(message.chat.id, 'Укажите время доставки', reply_markup=markup)


def set_delivery_time(message, date_str):
    client_id = message.chat.id
    time = datetime.strptime(date_str, "%H:%M")
    ORDERS_IN_PROCESS[client_id]['delivery_time'] = time

    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Подтверждаю',
                                          callback_data=f'order;create_order'),
               types.InlineKeyboardButton(text='Изменить',
                                          callback_data=f'order;ask_name'),
               types.InlineKeyboardButton(text='Отмена',
                                          callback_data=f'bouquet_params;main_menu')]
    markup.add(*buttons)

    message = get_description(ORDERS_IN_PROCESS[client_id], client_id)
    bot.send_message(client_id, message, reply_markup=markup)


def accept_order(client_chat_id):
    bouquet = ORDERS_IN_PROCESS[client_chat_id]['chosen_bouquet']
    client = Client.objects.get(client_id=client_chat_id)
    order = Order.objects.create(
        bouquet=bouquet, 
        client=client,
        delivery_address=ORDERS_IN_PROCESS[client_chat_id]['address'],
        delivery_date=ORDERS_IN_PROCESS[client_chat_id]['delivery_date'],
        delivery_time=ORDERS_IN_PROCESS[client_chat_id]['delivery_time']
    )
    ORDERS_IN_PROCESS[client_chat_id]['order_id'] = order.id


def offer_payment_types(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Оплатить онлайн',
                                          callback_data=f'order;pay_order'),
               types.InlineKeyboardButton(text='При получении',
                                          callback_data=f'order;courier_notified;False')]
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     'Ваш заказ принят.\n' 
                     'Желаете оплатить сейчас или при получении?', 
                     reply_markup=markup)


def pay_order(message):

    # сохранить информацию об оплате в БД
    pass


def courier_notified(message, is_paid):
    msg = get_courier_message(message, ORDERS_IN_PROCESS[message.chat.id], is_paid)
    bot.send_message(COURIERS_CHAT_ID, msg)

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Главное меню',
                                        callback_data=f'bouquet_params;main_menu')
    # добавить сюда кнопку "Мои заказы", если будет такой раздел
    markup.add(button)
    filepath = os.path.join(STATIC_ROOT, 'thanks_for_order.jpg')
    with open(filepath, 'rb') as file:
        bot.send_photo(message.chat.id,
                       photo=file,
                       caption='Спасибо, что выбрали нас)',
                       reply_markup=markup)







class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        try:
            bot.polling(none_stop=True)
        except Poll.DoesNotExist:
            raise CommandError()

bot.polling(none_stop=True)

        #bot.infinity_polling()







