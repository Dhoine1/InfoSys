from django_filters import FilterSet, DateTimeFilter
from django.forms import DateInput


class EventFilter(FilterSet):
   data = DateTimeFilter(
       field_name='data',
       lookup_expr='exact',
       widget=DateInput(
           format='%Y-%m-%d',
           attrs={'type': 'date'},
       ),
       label='Дата:',
   )
