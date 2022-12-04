from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page, name='main_page'),
    path('admin_ui/clients/', Client_list.as_view(), name='client_list'),
    path('admin_ui/clients/create/', CreateClient.as_view(), name='client_create_admin'),
    path('admin_ui/clients/<int:pk>/update/', UpdateClient.as_view(), name='client_update_admin'),
    path('admin_ui/clients/<int:pk>/delete/', DeleteClient.as_view(), name='client_delete_admin'),
    path('admin_ui/mailings/', Mailing_list.as_view(), name='mailings_list'),
    path('admin_ui/mailings/create/', CreateMailing.as_view(), name='mailings_create_admin'),
    path('admin_ui/mailings/<int:pk>/update/', UpdateMailing.as_view(), name='mailings_update_admin'),
    path('admin_ui/mailings/<int:pk>/delete/', DeleteMailing.as_view(), name='mailings_delete_admin'),
    path('admin_ui/mailings/settings_email/', SettingsEmailingStat.as_view(), name='settings_email'),
    path('admin_ui/mailings/<int:pk>/statistic/', Mailing_statistic.as_view(), name='mailings_statistic'),
    path('admin_ui/logs', Logs_list.as_view(), name='logs'),
    path("", index, name="index"),
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
    path("callback", callback, name="callback"),
]
