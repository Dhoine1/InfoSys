import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils.timezone import now
from events.models import Mail, Event
import datetime

logger = logging.getLogger(__name__)


def my_job():
    tomorrow = now() + datetime.timedelta(days=1)
    events = Event.objects.filter(data__exact=tomorrow)
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
        list_to_send += f'<tr><td>{tomorrow.strftime("%d-%m-%Y")}</td>' \
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



@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(hour="14", minute="00"),
            # trigger=CronTrigger(second="*/30"),
            id="my_job",
            max_instances=1,
            misfire_grace_time=3600,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")