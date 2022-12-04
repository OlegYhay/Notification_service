import datetime
from time import sleep

import pytz
from celery.contrib.abortable import AbortableTask
from django.db.models import Q
from main.celery import app
from .models import Client, Message
import requests

"""
Основная функция рассылки
"""


@app.task(bind=True, base=AbortableTask)
def send_create_message(self, mailing_id):
    print('i started')
    # import there because circular import
    from .views import Mailing
    mailing = Mailing.objects.get(id=mailing_id)
    # get clients
    clients = Client.objects.filter(tags__in=mailing.tags.all(),
                                    mobile_operator__in=mailing.mobile_operator.all())
    # send message and create object Message
    for i in clients:
        # Проверяем что стоп-дата еще не вышла
        now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
        if mailing.date_stop < now:
            return;
        url = 'https://probe.fbrq.cloud/v1/send/' + str(i.id)
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDEzNDMzNzcsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6Im9sZWd5aGF5In0.aR55p1eFYf73I5Tx8XBUVOgyBfALDbf11F67Gc9FzBc'}
        data = {'id': i.id,
                'phone': i.phone_number,
                'text': mailing.text,
                }
        # create message and set status = Отправлено
        new_message = Message(status="ОТПРАВЛЕНО", mailing_id=mailing, client_id=i)
        new_message.save()
        response = requests.post(url, headers=headers, json=data)
        # check status, if status != 200 then try again
        if str(response.status_code) == "200":
            new_message.status = "УСПЕШНО"
            new_message.save()
        else:
            new_message.status = "ОШИБКА"
            new_message.save()
            try_again_send.apply_async((url, data, headers, mailing_id, new_message.id))


"""
Если нам не удалось отправить, мы вызываем функцию отправки для конкретно этого сообщения 
и повторяем ее до тех пор, пока статус не будет равен 200, 
если время отправки истекло, мы отменяем отправку сообщения
"""


@app.task(bind=True, base=AbortableTask)
def try_again_send(self, url, data, headers, mailing_id, message_id):
    from .views import Mailing
    mailing = Mailing.objects.get(id=mailing_id)
    new_message = Message.objects.get(id=message_id)
    now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
    # Проверяем что текущая рассылка не закончилась
    if mailing.date_stop < now:
        return;
    response = requests.post(url, headers=headers, json=data)

    if str(response.status_code) == "200":
        new_message.status = "УСПЕШНО"
        new_message.save()
    else:
        # в случае очередного неуспеха, пытаемся снова.
        try_again_send.apply_async((url, data, headers, mailing_id, new_message.id))
