from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='bouquet/')
    price = models.IntegerField()
    events = models.ManyToManyField(Event)

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.CharField(max_length=100, null=True)
    user_phone = models.CharField(max_length=20, null=True)
    delivery_date = models.DateField(null=True)
    delivery_time = models.TimeField(null=True)
    delivery_address = models.CharField(max_length=200, null=True)
    bouquet = models.ForeignKey(null=True, on_delete=models.SET_NULL, to='bot.Bouquet')

