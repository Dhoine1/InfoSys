from django.db import models
import datetime
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


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название мероприятия')
    description = models.TextField(null=True, verbose_name='Описание мероприятия', blank=True)
    data = models.DateField(default=datetime.date.today, verbose_name='Дата проведения')
    begin_time = models.TimeField(verbose_name='Время начала')
    finish_time = models.TimeField(verbose_name='Время окончания')
    logo = models.FileField(upload_to="images/", verbose_name='Logo', blank=True)
    room = models.ManyToManyField(Halls, through='Location', verbose_name='Зал')

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
