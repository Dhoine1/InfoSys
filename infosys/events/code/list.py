import datetime
import configparser
from events.models import Event
from django.conf import settings


def list_slice(mainlist):
    date_show = datetime.datetime.now().strftime('%d.%m.%y')
    time_show = datetime.datetime.now().strftime('%H:%M')
    start_time = datetime.datetime.now() + datetime.timedelta(hours=3)
    event_today = Event.objects.filter(data__exact=datetime.datetime.now().date(),
                                       begin_time__lte=start_time.time(),
                                       finish_time__gte=datetime.datetime.now().time(),
                                       room_in_list__isnull=False).order_by('begin_time').distinct()

    # срезает список мероприятий по N штук через файл
    path_to_ini = f'{settings.INI_URL}Settings.ini'

    config = configparser.ConfigParser()
    try:
        config.read(f'{path_to_ini}')
        NUMBER_OF_ROWS = int(config.get('List', 'row_counts'))  # количество строк на экране списка
        count_event = int(len(event_today) // (NUMBER_OF_ROWS + 0.1))
        line = int(config.get('List', 'sheet_number'))

        if line > count_event:
            if mainlist:
                config.set('List', 'sheet_number', '0')
                with open(f'{path_to_ini}', 'w') as configfile:
                    config.write(configfile)
            line = 0
    except:
        NUMBER_OF_ROWS = 3
        line = 0
        count_event = 0

    slice = event_today[line * NUMBER_OF_ROWS:(line * NUMBER_OF_ROWS) + NUMBER_OF_ROWS]

    if mainlist:
        try:
            config.set('List', 'sheet_number', f'{line + 1}')
            with open(f'{path_to_ini}', 'w') as configfile:
                config.write(configfile)
        except:
            pass

    event_slice = {'time_show': time_show,
                   'date_show': date_show,
                   'event_today': slice,
                   'screen_number': line + 1,
                   'screens_count': count_event + 1}

    return event_slice, event_today
