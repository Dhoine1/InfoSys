from events.models import Event, Mail
from django.core.mail import EmailMultiAlternatives


def sendmail(day):
    events = Event.objects.filter(data__exact=day).distinct()
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
        list_to_send += f'<tr><td>{item_list.data.strftime("%d-%m-%Y")}</td>' \
                        f'<td>{item_list.begin_time.strftime("%H:%M")} - {item_list.finish_time.strftime("%H:%M")}</td>' \
                        f'<td>{rooms}</td><td><strong>{item_list.title}</strong></td><td>{item_list.quantity}</td>' \
                        f'<td>{item_list.description}</td><td>{item_list.contact}</td><td>{item_list.responce}</td>' \
                        f'<td>{item_list.parking}</td></tr>'
    list_to_send += '</table>'
    if list_to_send_text == '':
        list_to_send_text = 'Завтра мероприятий нет'
        list_to_send = 'Завтра мероприятий нет'

    send_date = f"{day[8:10]}-{day[5:7]}-{day[0:4]}"
    for email in emails:
        title = f'Мероприятия на: {send_date}'
        msg = EmailMultiAlternatives(title, list_to_send_text, None, [email])
        msg.attach_alternative(list_to_send, "text/html")
        msg.send()
