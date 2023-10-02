import django_filters
from django_filters import FilterSet, DateTimeFilter
from django.forms import DateInput


class EventFilter(FilterSet):
    event_title = django_filters.CharFilter(
        field_name='title',
        label="Содержит в названии",
        lookup_expr='icontains',
    )

    data = DateTimeFilter(
       field_name='data',
       lookup_expr='exact',
       widget=DateInput(
           format='%Y-%m-%d',
           attrs={'type': 'date'},
       ),
       label='Дата:',
   )
