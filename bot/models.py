from django.db import models
from django.db.models import Max
from FlowerShop.settings import BOT_LINK
from bot.bitlink import is_bitlink, shorten_link, count_clicks


class Client(models.Model):
    client_id = models.CharField(max_length=100,
                                 null=True,
                                 verbose_name='ID клиента')
    client_name = models.CharField(max_length=100, 
                                   null=True, blank=True,
                                   verbose_name='Имя клиента')
    client_phone = models.CharField(max_length=20, null=True,
                                    verbose_name='Телефон')

    def __str__(self):
        return self.client_name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name='Событие')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class Flowers(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название цветка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'


class Bouquet(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название букета')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='bouquets/', 
                              verbose_name='Изображение')
    price = models.PositiveIntegerField(verbose_name='Цена')
    events = models.ManyToManyField(Event, related_name='bouquets_for_event',
                                    verbose_name='События')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    flowers = models.ManyToManyField(Flowers,
                                    related_name='bouquets_for_flowers',
                                    verbose_name='Цветок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    def get_message(self):
        message = f'Букет \"{self.name}\"\n' \
                  f'Цена: {self.price} руб.\n' \
                  f'Описание: {self.description}'
        for flower in self.flowers.all():
            message += f'\n- {flower.name}'
        return message


class Order(models.Model):
    client = models.ForeignKey(on_delete=models.CASCADE,
                               to='bot.Client',
                               related_name='orders',
                               verbose_name='Клиент')
    delivery_date = models.DateField(null=True, verbose_name='Дата доставки')
    delivery_time = models.TimeField(null=True, verbose_name='Время доставки')
    delivery_address = models.CharField(max_length=200, null=True,
                                        verbose_name='Адрес доставки')
    bouquet = models.ForeignKey(null=True,
                                on_delete=models.SET_NULL,
                                to='bot.Bouquet', verbose_name='Букет')
    payment = models.BooleanField(default=False, verbose_name='Оплата')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


def create_new_bitlink():
    max_id = Link.objects.aggregate(Max('id'))['id__max']
    if not max_id:
        max_id = 0
    next_bitlink_id = max_id + 1
    while True:
        if not is_bitlink(BOT_LINK, next_bitlink_id):
            return shorten_link(BOT_LINK, next_bitlink_id)
        next_bitlink_id += 1


class Link(models.Model):
    shorten_link = models.CharField(
        'Сокращенная ссылка',
        max_length=20,
        null=True, blank=True,
        default=create_new_bitlink)
    place_of_use = models.CharField(
        'Место использования ссылки',
        max_length=50,
        null=True, blank=True)

    @property
    def clicks(self):
        return count_clicks(self.shorten_link)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
