from django.db import models


class Client(models.Model):
    client_id = models.CharField(max_length=100, null=True)
    client_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.client_name


class Event(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='bouquets/')
    price = models.IntegerField()
    events = models.ManyToManyField(Event, related_name='bouquets_for_event')

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(on_delete=models.CASCADE,
                               to='bot.Client',
                               related_name='orders')
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.CharField(max_length=100, null=True)
    user_phone = models.CharField(max_length=20, null=True)
    delivery_date = models.DateField(null=True)
    delivery_time = models.TimeField(null=True)
    delivery_address = models.CharField(max_length=200, null=True)
    bouquet = models.ForeignKey(null=True,
                                on_delete=models.SET_NULL,
                                to='bot.Bouquet')


