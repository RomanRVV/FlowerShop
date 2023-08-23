from django.core.management.base import BaseCommand, CommandError
from telebot import TeleBot, types
#import FlowerShop.settings
#from FlowerShop.settings import TELEGRAM_TOKEN
TELEGRAM_TOKEN = '6078909031:AAGN2OPnKOQfF_rokd3Sjvu5RmCnBEC-4dQ'
FLORISTS_CHAT_ID = -952806675
COURIERS_CHAT_ID = -952806675


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
        'image': 'путь к файлу',


    }
]



bot = TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def main_menu(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    # client = Client.objects.get_or_create(id_tg=message.from_user.id)[0]
    # client.save()
    id_tg=message.from_user.id
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Заказать букет',
                                        callback_data=f'choose_cause')
    markup.add(button)
    bot.send_message(message.chat.id,
                     f'Добро пожаловать! Выберите действие: ',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True) #call.data.startswith('bouquet')
def get_bouquet_params(call):
    callback_data = call.data.split(';')

    if call.data.startswith('main_menu'):
        main_menu(call.message)
    if call.data.startswith('choose_cause'):
        choose_cause(call.message)
    if call.data.startswith('choose_price'):
        cause_id = callback_data[1]
        choose_price(call.message, cause_id)
    if call.data.startswith('second_menu'):
        cause_id = callback_data[1]
        price = callback_data[2]
        second_menu(call.message, cause_id, price)
    if call.data.startswith('notify_florist'):
        cause_id = callback_data[1]
        price = callback_data[2]
        notify_florist(call.message, cause_id, price)



def choose_cause(message):
    # запрос к бд
    # фильтр к таблице букетов на уникальные значения поводов

    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cause}', 
            callback_data=f'choose_price;{cause}'
        ) 
        for cause in CAUSES
    ]
    #markup.add(*buttons)
    for button in buttons:
        markup.add(button)
    bot.send_message(message.chat.id,
                     'К какому событию готовимся? '
                     'Выберите один из вариантов, либо укажите свой',
                     reply_markup=markup)


def choose_price(message, cause_id):
    # запрос к бд
    # функция, возвращает лист приблизительных цен с шагом по 1000

    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(
            text=f'~{price} руб.', 
            callback_data=f'second_menu;{cause_id};{price}'
        )
        for price in PRICES
    ]
    # for button in buttons:
    #     markup.add(button)
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     'На какую сумму рассчитываете?',
                     reply_markup=markup)


def second_menu(message, cause_id, price):
    # функция, фильтрующая букеты по cause_id и price, 
    # возвращает список подходящих букетов
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Посмотреть букеты',
                                          callback_data=f'bouquet_presentation;{cause_id};{price}'),
               types.InlineKeyboardButton(text='Связаться с флористом',
                                          callback_data=f'notify_florist;{cause_id};{price}')]
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     f'Вы выбрали:\n повод: {cause_id}\n цена: {price}\n'
                     'Предпочитаете посмотреть готовые букеты или обратиться к флористу?',
                     reply_markup=markup)


def notify_florist(message, cause_id, price):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Отмена',
                                        callback_data=f'second_menu;')
    markup.add(button)
    msg = bot.send_message(message.chat.id,
                           'Укажите номер телефона, и наш флорист перезвонит вам в течение 20 минут',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, florist_notified, cause_id, price)


#message.from_user.id
def florist_notified(message, cause_id, price):
    msg = f'Клиент № client.id\n' \
          f'ТГ ссылка: tg://user?id={message.chat.id}\n' \
          f'Телефон: {message.text}\n' \
          f'Предпочтения:\n  повод: {cause_id}\n  цена: {price}'
    bot.send_message(FLORISTS_CHAT_ID, msg)

    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text='Посмотреть букеты',
                                          callback_data=f'bouquet_presentation;{cause_id};{price}'),
               types.InlineKeyboardButton(text='Главное меню',
                                          callback_data=f'main_menu')]
    markup.add(*buttons)
    bot.send_message(message.chat.id,
                     'Флорист скоро свяжется с вами. '
                     'А пока можете присмотреть что-нибудь из готовой коллекции',
                     reply_markup=markup)



    



# @bot.callback_query_handler(func=lambda call: call.data.startswith('bouquet_presentation')) 
# def bouquet_presentation(call):








class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        try:
            bot.polling(none_stop=True)
        except Poll.DoesNotExist:
            raise CommandError()

bot.polling(none_stop=True)

        #bot.infinity_polling()







