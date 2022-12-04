import datetime
import json
import time

import pytz
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
# View для главной страницы
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from admin_ui.forms import MailingForm
from main.celery import app
from .tasks import *
from admin_ui.models import HistoryDataForEmailingStat, Logs
from notification.models import Client, MobileOperator, Mailing
from notification.tasks import *


def main_page(request):
    mailings = Mailing.objects.filter(date_dispatch__gte=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")))[:5]
    return render(request, 'notification/main_page.html', {'mailings': mailings})


# View для редактирования ежедневной рассылки, создает новую повторяющуюся задачу celery и отменяет старую
class SettingsEmailingStat(View):
    def get(self, request):
        data = HistoryDataForEmailingStat.objects.last()
        return render(request, 'admin_ui/another/statictic_email.html', {'data': data})

    def post(self, request):
        data = HistoryDataForEmailingStat.objects.last()
        if data != None:
            app.control.revoke(data.task_id, terminate=True)
        new_task = HistoryDataForEmailingStat(email=request.POST['email'],
                                              date=request.POST['datetime'],
                                              )
        new_task.save()
        time_now = datetime.datetime.now()
        print(new_task.date)
        time_start = new_task.date
        time_start = datetime.datetime.strptime(time_start, "%Y-%m-%dT%H:%M")
        delay = (time_start - time_now).total_seconds()
        m = send_statistic.apply_async((new_task.date, new_task.email),
                                       countdown=delay)
        new_task.task_id = m.id
        new_task.save()
        data = HistoryDataForEmailingStat.objects.last()
        return render(request, 'admin_ui/another/statictic_email.html', {'data': data})


class Mailing_statistic(DetailView):
    model = Mailing
    template_name = "admin_ui/mailing/mailing_statistic.html"
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super(Mailing_statistic,self).get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(mailing_id=self.kwargs['pk']).values('status').annotate(
            count=Count('status'))
        return context

class Logs_list(ListView):
    model = Logs
    template_name = 'admin_ui/logs.html'
    context_object_name = 'logs'
    ordering = ['-date']

class Client_list(ListView):
    model = Client
    template_name = 'admin_ui/client/client_list.html'
    context_object_name = 'clients'


class CreateClient(CreateView):
    model = Client
    template_name = 'admin_ui/client/client_create.html'
    fields = ['name', 'phone_number', 'tags']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        self.object = form.save()
        number = self.object.phone_number
        if '+' in number:
            mobile_operator = number[1:4]
        else:
            mobile_operator = number[0:3]
        self.object.mobile_operator = MobileOperator.objects.get_or_create(code=mobile_operator)[0]
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class UpdateClient(UpdateView):
    model = Client
    template_name = 'admin_ui/client/client_update.html'
    fields = ['name', 'phone_number', 'tags']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        self.object = form.save()
        number = self.object.phone_number
        if '+' in number:
            mobile_operator = number[1:4]
        else:
            mobile_operator = number[0:3]
        self.object.mobile_operator = MobileOperator.objects.get_or_create(code=mobile_operator)[0]
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class DeleteClient(DeleteView):
    model = Client
    template_name = 'admin_ui/client/client_delete.html'
    success_url = reverse_lazy('client_list')


class Mailing_list(ListView):
    model = Mailing
    template_name = 'admin_ui/mailing/mailing_list.html'
    context_object_name = 'mailings'


class CreateMailing(CreateView):
    model = Mailing
    template_name = 'admin_ui/mailing/mailing_create.html'
    success_url = reverse_lazy('mailings_list')
    form_class = MailingForm

    def form_valid(self, form):
        self.object = form.save()
        """
        если время завершения рассылки меньше текущего, рассылка не стартует!
        если время старта в будущем , создается задача с началом на время старта!
        если время старта в прошлом или текущее, а время до завершения еще осталось,
        рассылка стартует немедленно!
        """
        now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
        print(now)
        stop = self.object.date_stop
        start = self.object.date_dispatch
        if stop > now:
            m = send_create_message.apply_async((self.object.id,), countdown=(start - now).total_seconds())
            self.object.id_task = m.id
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())



class UpdateMailing(UpdateView):
    model = Mailing
    template_name = 'admin_ui/mailing/mailing_update.html'
    success_url = reverse_lazy('mailings_list')
    form_class = MailingForm

    def form_valid(self, form):
        self.object = form.save()
        """
            При редактировании старая задача удаляется, новая создается.ю
        """
        now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
        stop = self.object.date_stop
        start = self.object.date_dispatch
        if stop > now:
            app.control.revoke(self.object.id_task, terminate=True)
            m = send_create_message.apply_async((self.object.id,), countdown=(start - now).total_seconds())
            self.object.id_task = m.id
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class DeleteMailing(DeleteView):
    model = Mailing
    template_name = 'admin_ui/mailing/mailing_delete.html'
    success_url = reverse_lazy('mailings_list')

    def form_valid(self, form):
        # удаляем задачу
        app.control.revoke(self.object.id_task, terminate=True)
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


# Авторизация через OAuth
oauth = OAuth()

oauth.register(
    "auth0",
    client_id="CT7sFrzdeKbhskHyVQR4LtX1JrKiN1np",
    client_secret="aab5VbwxQFGCuwXeYmT3_VxLBosWUfp3MmBbJ8dZgPjcENcUIfyR2ajxgpJbMlMB",
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://dev-ybcgufs86ymu7uge.us.auth0.com/.well-known/openid-configuration",
)


def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )


def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://dev-ybcgufs86ymu7uge.us.auth0.com/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": "CT7sFrzdeKbhskHyVQR4LtX1JrKiN1np",
            },
            quote_via=quote_plus,
        ),
    )
