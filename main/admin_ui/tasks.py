import datetime

from celery.contrib.abortable import AbortableTask
from django.core.mail import send_mail
from django.db.models import Count
from main.celery import app

from admin_ui.models import HistoryDataForEmailingStat
from notification.models import Message
from notification.serializers import Serializer_all_stat


@app.task(bind=True, base=AbortableTask)
def send_statistic(self, time, email):
    # данные отправляем за предыдуший день
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.combine(yesterday.date(), yesterday.min.time())
    today = datetime.datetime.today()
    today = today.combine(today.date(), today.min.time())
    messages = Message.objects.filter(date_created__gte=yesterday, date_created__lte=today).values('mailing_id',
                                                                                                   'status').annotate(
        count=Count('status'))
    if messages.count() != 0:
        data = Serializer_all_stat(messages, many=True).data
    else:
        data = "Вчера не было рассылок!"
    send_mail(
        'Ежедневная статистика',
        str(data),
        'testmaildjango@mail.ru',
        [email],
        fail_silently=False,
    )
    task = HistoryDataForEmailingStat.objects.last()
    m = send_statistic.apply_async((task.date, task.email),
                                   countdown=86400)
    task.task_id = m.id
    task.save()
