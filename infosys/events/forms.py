from django import forms
from .models import Event
from django.forms import DateInput, TimeInput


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
            'quantity',
            'contact',
            'parking',
            'responce'
        ]

        widgets = {"data": DateInput(format='%Y-%m-%d', attrs={'type': 'date'}, ),
                   "begin_time": TimeInput(format='%H:%M:%S', attrs={'type': 'time'}, ),
                   "finish_time": TimeInput(format='%H:%M:%S', attrs={'type': 'time'}, ),
                   "title": forms.Textarea(attrs={'rows': 3}),
                   'description': forms.Textarea(attrs={'rows': 2}),
                   'quantity': forms.Textarea(attrs={'rows': 1, 'cols': 5}),
                   'contact': forms.Textarea(attrs={'rows': 3}),
                   'parking': forms.Textarea(attrs={'rows': 2}),
                   'room': forms.CheckboxSelectMultiple(),
                   'room_in_list': forms.CheckboxSelectMultiple()
                   }
