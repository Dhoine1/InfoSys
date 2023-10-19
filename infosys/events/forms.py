from django import forms
from .models import Event


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'data',
            'begin_time',
            'finish_time',
            'logo',
            'room',
            'room_in_list',
        ]
