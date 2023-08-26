from django.db import models


class Client(models.Model):
    client_id = models.CharField(max_length=100,
                                 null=True,
                                 verbose_name='ID клиента')
    client_name = models.CharField(max_length=100, null=True,
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
    image = models.ImageField(upload_to='bouquets/', verbose_name='Изображение')
    price = models.PositiveIntegerField(verbose_name='Цена')
    events = models.ManyToManyField(Event, related_name='bouquets_for_event',
                                    verbose_name='События')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    flower = models.ManyToManyField(Flowers,
                                    related_name='bouquets_for_flowers',
                                    verbose_name='Цветок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'


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
