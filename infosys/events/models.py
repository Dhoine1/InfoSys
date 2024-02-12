from django.db import models
from datetime import datetime, timedelta
from django.urls import reverse


class Halls(models.Model):
    hall_name = models.CharField(max_length=32, unique=True)
    hall_place = models.CharField(max_length=32)
    hall_name_eng = models.CharField(max_length=32, null=True)

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'

    def __str__(self):
        return self.hall_name


class HallList(models.Model):
    name_in_list = models.CharField(max_length=32, unique=True)
    name_in_list_eng = models.CharField(max_length=32, null=True)
    hall_in_list_place = models.CharField(max_length=32)

    class Meta:
        verbose_name = 'Зал в списке'
        verbose_name_plural = 'Залы в списке'

    def __str__(self):
        return self.name_in_list


class Manager(models.Model):
    name = models.CharField(max_length=255, verbose_name="Менеджер")

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название мероприятия')
    description = models.TextField(null=True, verbose_name='Компания', blank=True)
    data = models.DateField(default=(datetime.now() + timedelta(days=1)), verbose_name='Дата проведения')
    begin_time = models.TimeField(default="09:00", verbose_name='Время начала')
    finish_time = models.TimeField(default="18:00", verbose_name='Время окончания')
    logo = models.FileField(upload_to="images/", verbose_name='Logo', blank=True)
    room = models.ManyToManyField(Halls, through='Location', verbose_name='Зал')
    room_in_list = models.ManyToManyField(HallList, through='LocList', verbose_name='Отображение в списке')
    quantity = models.CharField(max_length=5, default="n/a", verbose_name="Колличество участников")
    contact = models.TextField(null=True, verbose_name="Контакт организатора", blank=True)
    parking = models.CharField(max_length=255, verbose_name="Парковка", blank=True)
    responce = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name="Ответственный")

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return f'{self.data} ( {self.begin_time} - {self.finish_time} )    Зал: {self.room} - {self.title}'

    def get_absolute_url(self):
        return reverse('list')


class Location(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    hall = models.ForeignKey(Halls, on_delete=models.CASCADE)


class LocList(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    halllist = models.ForeignKey(HallList, on_delete=models.CASCADE)


class Mail(models.Model):
    email = models.EmailField(max_length=254, verbose_name="e-mail", blank=False)

    class Meta:
        verbose_name = 'Список рассылки'
        verbose_name_plural = 'Список рассылки'
