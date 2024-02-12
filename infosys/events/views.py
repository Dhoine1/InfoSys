import datetime
import pyjokes
import configparser
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings
from .models import Event, Halls, HallList, Mail
from .forms import EventForm
from .filters import EventFilter
from django.core.mail import EmailMultiAlternatives
from copy import deepcopy

# def index(request):
#     return render(request, 'index.html')


# Экран списка всех мероприятий. Стартовый.
class EventList(ListView):
    model = Event
    ordering = ['-data', 'begin_time']
    template_name = 'index.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super(EventList, self).get_context_data(*args, **kwargs)
        config = configparser.ConfigParser()
        config.read(f'{settings.INI_URL}settings.ini')
        context['rows'] = int(config.get('List', 'row_counts'))
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


# Создание мероприятия через формы
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
        return render(request, 'no_event_room.html', {'hall': hall,
                                                      'hall_eng': hall_eng,
                                                      'time_show': time_show, })


# экран списка мероприятий
def list_view(request):
    date_show = datetime.datetime.now().strftime('%d.%m.%y')
    time_show = datetime.datetime.now().strftime('%H:%M')
    start_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=start_time.time(),
                                       finish_time__gte=datetime.datetime.now().time()).order_by('begin_time')

    # срезает список мероприятий по N штук через файл
    path_to_ini = f'{settings.INI_URL}Settings.ini'

    config = configparser.ConfigParser()
    try:
        config.read(f'{path_to_ini}')
        NUMBER_OF_ROWS = int(config.get('List', 'row_counts'))  # количество строк на экране списка
        count_event = int(len(event_today) // (NUMBER_OF_ROWS + 0.1))
        line = int(config.get('List', 'sheet_number'))

        if line > count_event:
            config.set('List', 'sheet_number', '0')
            with open(f'{path_to_ini}', 'w') as configfile:
                config.write(configfile)
            line = 0
    except:
        NUMBER_OF_ROWS = 3
        line = 0

    slice = event_today[line * NUMBER_OF_ROWS:(line * NUMBER_OF_ROWS) + NUMBER_OF_ROWS]

    try:
        config.set('List', 'sheet_number', f'{line + 1}')
        with open(f'{path_to_ini}', 'w') as configfile:
            config.write(configfile)
    except:
        pass

    if event_today:
        return render(request, 'list.html', {'time_show': time_show,
                                             'date_show': date_show,
                                             'event_today': slice,
                                             })
    else:
        return render(request, 'no_event.html')


# Экран списка без смены среза мероприятий. Временно.
def list_view_const(request):
    date_show = datetime.datetime.now().strftime('%d.%m.%y')
    time_show = datetime.datetime.now().strftime('%H:%M')
    start_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=start_time.time(),
                                       finish_time__gte=datetime.datetime.now().time()).order_by('begin_time')
    path_to_ini = f'{settings.INI_URL}Settings.ini'

    try:
        config = configparser.ConfigParser()
        config.read(f'{path_to_ini}')
        NUMBER_OF_ROWS = int(config.get('List', 'row_counts'))  # количество строк на экране списка
        count_event = int(len(event_today) // (NUMBER_OF_ROWS + 0.1))
        line = int(config.get('List', 'sheet_number'))
        if line > count_event:
            line = 0

    except:
        NUMBER_OF_ROWS = 3
        line = 0

    slice = event_today[line * NUMBER_OF_ROWS:(line * NUMBER_OF_ROWS) + NUMBER_OF_ROWS]

    if event_today:
        return render(request, 'list.html', {'time_show': time_show,
                                             'date_show': date_show,
                                             'event_today': slice,
                                             })
    else:
        return render(request, 'no_event.html')


# анекдот дня )
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
            events = Event.objects.filter(data__exact=day)
            emails = Mail.objects.all().values_list('email', flat=True)
            list_to_send_text = ''
            list_to_send = '''<style type="text/css">
                                table {background: #5ce532;border: 3px solid #000;} 
                                td {background:  #fdff70; padding: 5px; border: 1px solid;}</style>
                                <table><th>Дата</th><th>Время<br>проведения</th><th>Зал</th>
                                <th>Название мероприятия</th><th>Кол-во<br>уч-ов</th><th>Компания</th>
                                <th>Контакт организатора</th><th>Ответственный<br>менеджер</th><th>Парковка</th>'''

            for item_list in events:
                rooms = ""
                for i in item_list.room.all():
                    rooms += f' <b>{i.hall_name}</b> - {i.hall_place}<br>'
                list_to_send_text += f'-- {item_list.title} --'
                list_to_send += f'<tr><td>{day}</td>' \
                                f'<td>{item_list.begin_time.strftime("%H:%M")} - {item_list.finish_time.strftime("%H:%M")}</td>' \
                                f'<td>{rooms}</td><td><strong>{item_list.title}</strong></td><td>{item_list.quantity}</td>' \
                                f'<td>{item_list.description}</td><td>{item_list.contact}</td><td>{item_list.responce}</td>' \
                                f'<td>{item_list.parking}</td></tr>'
            list_to_send += '</table>'
            if list_to_send_text == '':
                list_to_send_text = 'Завтра мероприятий нет'
                list_to_send = 'Завтра мероприятий нет'

            for email in emails:
                title = f'Мероприятия на завтра {tomorrow.strftime("%d-%m-%Y")}'
                msg = EmailMultiAlternatives(title, list_to_send_text, None, [email])
                msg.attach_alternative(list_to_send, "text/html")
                msg.send()
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


def copy(request, pk):
    model_instance = Event.objects.get(pk__exact=pk)
    cloned_instance = deepcopy(model_instance)
    cloned_instance.pk = None
    cloned_instance.save()

    # for related_obj in model_instance.room.all():
    #     related_obj.pk = None
    #     related_obj.foreign_key_to_instance = cloned_instance
    #     related_obj.save()
    #
    # for related_obj in model_instance.room_in_list.all():
    #     related_obj.pk = None
    #     related_obj.foreign_key_to_instance = cloned_instance
    #     related_obj.save()

    return redirect('../../events')
