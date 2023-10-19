from django.contrib import admin
from .models import Event, Halls, HallList


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'data', 'begin_time', 'finish_time')


class HallsAdmin(admin.ModelAdmin):
    list_display = ('hall_name', 'hall_name_eng', 'hall_place')


class HallsListAdmin(admin.ModelAdmin):
    list_display = ('name_in_list', 'name_in_list_eng', 'hall_in_list_place')


admin.site.register(Event, EventAdmin)
admin.site.register(Halls, HallsAdmin)
admin.site.register(HallList, HallsListAdmin)
