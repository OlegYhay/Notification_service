import datetime
import time

from django.db import transaction
from django.db.models import Count, Avg

# Create your views here.
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from main.celery import app
from .tasks import send_create_message
from .serializers import *

from .models import Client


# Destroy Api for CLIENT
class ClientDestroy(generics.DestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = SerializerClient


# LIST, Create Api for CLIENT
class ClientCreate(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = SerializerClient

    # set mobile operator from MobileOperator model
    def perform_create(self, serializer):
        number = self.request.data['phone_number']
        if '+' in number:
            mobile_operator = number[1:4]
        else:
            mobile_operator = number[0:3]
        operator = MobileOperator.objects.get_or_create(code=mobile_operator)
        serializer.save(mobile_operator=operator[0])


# Detail view client
class ClientRetrieve(RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = SerializerClient


# Edit Api for CLIENT
class ClientUpdate(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = SerializerClient

    def perform_update(self, serializer):
        number = self.request.data['phone_number']
        if '+' in number:
            mobile_operator = number[1:4]
        else:
            mobile_operator = number[0:3]
        operator = MobileOperator.objects.get_or_create(code=mobile_operator)
        serializer.save(mobile_operator=operator[0])


# CRUD for mailing model
class MailingViewSet(ModelViewSet):
    serializer_class = SerializerMailings
    queryset = Mailing.objects.all()

    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(serializer)
        # Удаляем задачу celery
        id = serializer.data['id']
        mails = Mailing.objects.get(id=id)
        app.control.revoke(mails.id_task, terminate=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        id = serializer.data['id']
        now = datetime.datetime.now()
        stop = datetime.datetime.strptime(serializer.data['date_stop'], "%Y-%m-%dT%H:%M:%S+03:00")
        start = datetime.datetime.strptime(serializer.data['date_dispatch'], "%Y-%m-%dT%H:%M:%S+03:00")
        """"
            При обновление удаляем старую задачу celery по id и создаем новую с новыми данными
        """
        if stop > now:
            mails = Mailing.objects.get(id=id)
            app.control.revoke(mails.id_task, terminate=True)
            m = send_create_message.apply_async((id,), countdown=(start - now).total_seconds())
            mails.id_task = m.id
            mails.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        id = serializer.data['id']
        """
        если время завершения рассылки меньше текущего, рассылка не стартует!
        если время старта в будущем , создается задача с началом на время старта!
        если время старта в прошлом или текущее, а время до завершения еще осталось,
        рассылка стартует немедленно!
        """
        now = datetime.datetime.now()
        stop = datetime.datetime.strptime(serializer.data['date_stop'], "%Y-%m-%dT%H:%M:%S+03:00")
        start = datetime.datetime.strptime(serializer.data['date_dispatch'], "%Y-%m-%dT%H:%M:%S+03:00")
        if stop > now:
            mails = Mailing.objects.get(id=id)
            m = send_create_message.apply_async((mails.id,), countdown=(start - now).total_seconds())
            # Сохраняем id задачи чтоб в будущем отменить либо отредактировать
            mails.id_task = m.id
            mails.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Получаем детальную статистику(конкретной рассылки) с группировкой по статусу
    # Возвращает данный в формате
    """{
        'status':'Статус сообщения',
        'count':'Количество сообщения с данным статусом'
        }
    """

    @action(detail=True, methods=['get'])
    def main_statistic_detail(self, request, pk=None):
        mailing = Mailing.objects.get(pk=pk)
        messages = Message.objects.filter(mailing_id=mailing).values('status').annotate(count=Count('status'))
        serializers = Serializer_detail_stat(messages, many=True)
        return Response(serializers.data)

    # Получение общей статистики по всем рассылкам с группировкой по статусу
    # представлен в формате
    """
        {
        'mailing_id':'номер рассылки'
        'status':'Статус сообщения'
        'count': 'количество сообщений с данным стаусом'
        }
    """

    @action(detail=False, methods=['get'])
    def main_statistic_all(self, request):
        messages = Message.objects.values('mailing_id', 'status').annotate(count=Count('status'))
        serializers = Serializer_all_stat(messages, many=True)
        return Response(serializers.data)
