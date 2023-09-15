import datetime

from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Event, Halls
from .forms import EventForm
from .filters import EventFilter

def index(request):
    return render(request, 'index.html')


class EventDetail(DetailView):
    model = Event
    template_name = 'event.html'
    context_object_name = 'event'


class EventList(ListView):
    model = Event
    ordering = '-data'
    template_name = 'index.html'
    context_object_name = 'events'


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
    return render(request, 'room.html', {'time_show': time_show,
                                         'hall': hall,
                                         'hall_eng': hall_eng,
                                         'event_now': event_now,
                                         'dis_event_now': dis_event_now,
                                         'pict_event_now': pict_event_now})

#
# class RoomView(DetailView):
#     model = Halls
#     time_show = datetime.datetime.now().strftime('%H:%M')
#     event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
#                                        begin_time__lte=datetime.datetime.now().time(),
#                                        finish_time__gte=datetime.datetime.now().time())
#
#     template_name = 'room.html'
#
#     context_object_name = 'hall'
#     extra_context = {'time_show': time_show, 'event_today': event_today}
