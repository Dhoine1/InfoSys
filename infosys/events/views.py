import datetime
import pyjokes
import configparser
from django.views.decorators.cache import cache_page

from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Event, Halls
from .forms import EventForm
from .filters import EventFilter


def index(request):
    return render(request, 'index.html')


class EventList(ListView):
    model = Event
    ordering = ['-data', 'begin_time']
    template_name = 'index.html'
    context_object_name = 'events'
    paginate_by = 5


class EventSearch(ListView):
    model = Event
    ordering = ['-data', 'begin_time']
    template_name = 'search.html'
    context_object_name = 'events'

    def get_queryset(self):
        if self.request.GET:
            queryset = super().get_queryset()
            self.filterset = EventFilter(self.request.GET, queryset)
            return self.filterset.qs
        else:
            queryset = Event.objects.none()
            self.filterset = EventFilter(self.request.GET, queryset)
            return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class EventCreate(CreateView):
    form_class = EventForm
    model = Event
    template_name = 'event_edit.html'
    success_url = ''


class EventUpdate(UpdateView):
    form_class = EventForm
    model = Event
    template_name = 'event_edit.html'
    raise_exception = True


class EventDelete(DeleteView):
    model = Event
    template_name = 'event_delete.html'
    success_url = reverse_lazy('list')


#экран перед залом
def room_view(request, pk, **kwargs):
    time_show = datetime.datetime.now().strftime('%H:%M')
    hall_now = Halls.objects.filter(pk__exact=pk)

    for i in hall_now:
        hall = i.hall_name
        hall_pk = i.pk
        hall_eng = i.hall_name_eng

    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=datetime.datetime.now().time(),
                                       finish_time__gte=datetime.datetime.now().time())

    event_now = ''
    dis_event_now = ""
    pict_event_now = ""


    for e in event_today:
        for f in e.room.all():
            if f.pk == hall_pk:
                event_now = e.title
                dis_event_now = e.description
                pict_event_now = e.logo

    if event_now != '':
        return render(request, 'room.html', {'time_show': time_show,
                                             'hall': hall,
                                             'hall_eng': hall_eng,
                                             'event_now': event_now,
                                             'dis_event_now': dis_event_now,
                                             'pict_event_now': pict_event_now})
    else:
        return render(request, 'no_event.html')


#экран списка мероприятий
@cache_page(29)
def list_view(request):
    date_show = datetime.datetime.now().strftime('%d.%m.%y')
    time_show = datetime.datetime.now().strftime('%H:%M')
    start_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=start_time.time(),
                                       finish_time__gte=datetime.datetime.now().time()).order_by('begin_time')

    # срезает список мероприятий по 5 штук через файл
    path_to_ini = 'E:/Pyton/infosys/infosys/events/static/pict/Settings.ini'

    config = configparser.ConfigParser()
    config.read(f'{path_to_ini}')
    NUMBER_OF_ROWS = int(config.get('List', 'row_counts'))   #количество строк на экране списка
    count_event = int(len(event_today) // (NUMBER_OF_ROWS + 0.1))
    line = int(config.get('List', 'sheet_number'))

    if line > count_event:
        config.set('List', 'sheet_number', '0')
        with open(f'{path_to_ini}', 'w') as configfile:
            config.write(configfile)
        line = 0

    slice = event_today[line * NUMBER_OF_ROWS:(line * NUMBER_OF_ROWS) + NUMBER_OF_ROWS]

    config.set('List', 'sheet_number', f'{line + 1}')
    with open(f'{path_to_ini}', 'w') as configfile:
        config.write(configfile)

    if event_today:
        return render(request, 'list.html', {'time_show': time_show,
                                             'date_show': date_show,
                                             'event_today': slice,
                                             })
    else:
        return render(request, 'no_event.html')

#анекдот дня )
def anek(request):
    joke = pyjokes.get_joke()

    return render(request, 'anek.html', {'joke': joke})

# тестовая комната для предпросмотра
def room_test(request, pk, **kwargs):
    time_show = datetime.datetime.now().strftime('%H:%M')
    event_test = Event.objects.filter(pk__exact=pk)

    hall = "Тестовый зал"
    hall_eng = "Test room"

    for e in event_test:
            event_now = e.title
            dis_event_now = e.description
            pict_event_now = e.logo

    return render(request, 'room.html', {'time_show': time_show,
                                         'hall': hall,
                                         'hall_eng': hall_eng,
                                         'event_now': event_now,
                                         'dis_event_now': dis_event_now,
                                         'pict_event_now': pict_event_now})
