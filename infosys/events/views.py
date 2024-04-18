import datetime
import configparser
from copy import deepcopy

from .code.sendmail import sendmail

from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings
from django.core.paginator import Paginator

from .models import Event, Halls, Mail, Location, LocList
from .forms import EventForm
from .filters import EventFilter, FastFilter


# Экран списка всех мероприятий. Стартовый.
class EventList(ListView):
    model = Event
    ordering = ['-data', 'begin_time']
    template_name = 'index.html'
    context_object_name = 'events'
    paginate_by = 10
    filter_class = FastFilter

    def get_queryset(self):
        if self.request.GET:
            queryset = super().get_queryset()
            self.filterset = FastFilter(self.request.GET, queryset)
            return self.filterset.qs
        else:
            queryset = Event.objects.all().order_by('-data', 'begin_time')
            self.filterset = FastFilter(self.request.GET, queryset)
            return self.filterset.qs

    def get_context_data(self, *args, **kwargs):
        context = super(EventList, self).get_context_data(*args, **kwargs)
        config = configparser.ConfigParser()
        config.read(f'{settings.INI_URL}settings.ini')
        context['rows'] = int(config.get('List', 'row_counts'))
        context['today'] = datetime.datetime.now()
        context['filterset'] = self.filterset
        return context

    @staticmethod
    def post(request):
        number = request.POST.get("numbers_of_row")

        if not number or int(number) <= 0:
            number = 4

        config2 = configparser.ConfigParser()
        config2.read(f'{settings.INI_URL}settings.ini')
        config2.set('List', 'row_counts', f'{number}')
        with open(f'{settings.INI_URL}settings.ini', 'w') as configfile:
            config2.write(configfile)
        return redirect('./')


# Экран поиска мероприятий
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


# Создание мероприятия
class EventCreate(CreateView):
    form_class = EventForm
    model = Event
    template_name = 'event_edit.html'
    success_url = ''


# Редактирование мероприятия
class EventUpdate(UpdateView):
    form_class = EventForm
    model = Event
    template_name = 'event_edit.html'
    raise_exception = True


# Удаление мероприятия
class EventDelete(DeleteView):
    model = Event
    template_name = 'event_delete.html'
    success_url = reverse_lazy('list')


# экран перед залом
def room_view(request, pk, **kwargs):
    time_show = datetime.datetime.now().strftime('%H:%M')
    hall_now = Halls.objects.filter(pk__exact=pk)

    for i in hall_now:
        hall = i.hall_name
        hall_pk = i.pk
        hall_eng = i.hall_name_eng

    start_time = datetime.datetime.now() + datetime.timedelta(hours=2)

    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=start_time.time(),
                                       finish_time__gte=datetime.datetime.now().time()).order_by('-begin_time')

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
        return render(request, 'no_event_room.html', {'hall': hall,
                                                      'hall_eng': hall_eng,
                                                      'time_show': time_show, })


# экран списка мероприятий
# def list_view(request):
#     event_slice, event_today = list_slice(True)
#
#     if event_today:
#         return render(request, 'list.html', event_slice)
#     else:
#         return render(request, 'no_event.html')


def list_view(request):
    date_show = datetime.datetime.now().strftime('%d.%m.%y')
    time_show = datetime.datetime.now().strftime('%H:%M')
    start_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=start_time.time(),
                                       finish_time__gte=datetime.datetime.now().time(),
                                       room_in_list__isnull=False).order_by('begin_time').distinct()

    path_to_ini = f'{settings.INI_URL}Settings.ini'
    config = configparser.ConfigParser()
    try:
        config.read(f'{path_to_ini}')
        NUMBER_OF_ROWS = int(config.get('List', 'row_counts'))
    except:
        NUMBER_OF_ROWS = 3

    paginator = Paginator(event_today, NUMBER_OF_ROWS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if event_today:
        return render(request, 'list.html', {'event_today': page_obj,
                                             'time_show': time_show,
                                             'date_show': date_show, })
    else:
        return render(request, 'no_event.html')


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


# экран списка адресов для автомат. рассылки
def send_list(request):
    mail = Mail.objects.order_by('email')
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)

    if request.method == "POST":
        email = Mail()
        email.email = request.POST.get("newmail")
        email.save()
        return render(request, 'send.html', {'mail': mail,
                                             'tomorrow': tomorrow})

    if request.method == "GET":
        if request.GET.get('date'):
            send_message = "ОТПРАВЛЕНО"
            day = request.GET.get("date")
            sendmail(day)
        else:
            send_message =""

        return render(request, 'send.html', {'mail': mail,
                                             'tomorrow': tomorrow,
                                             'send_message': send_message})

    return render(request, 'send.html', {'mail': mail,
                                         'tomorrow': tomorrow})


# удаление адреса из списка рассылки
class MailDelete(DeleteView):
    model = Mail
    template_name = 'mail_delete.html'
    success_url = reverse_lazy('email')


# создание копии мероприятия
def copy(request, pk):
    model_instance = Event.objects.get(pk__exact=pk)
    cloned_instance = deepcopy(model_instance)
    cloned_instance.pk = None
    new_data = datetime.datetime.now() + datetime.timedelta(weeks=10)
    cloned_instance.data = new_data
    cloned_instance.save()

    for rooms in model_instance.room.all():
        location = Location()
        location.event_id = cloned_instance.pk
        location.hall_id = rooms.pk
        location.save()

    for rooms_in_list in model_instance.room_in_list.all():
        loclist = LocList()
        loclist.event_id = cloned_instance.pk
        loclist.halllist_id = rooms_in_list.pk
        loclist.save()

    return redirect('../../events')


# help
def help(request):
    return render(request, 'help.html')
