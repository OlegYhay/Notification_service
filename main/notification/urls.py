from django.urls import path, re_path
from rest_framework import permissions
from rest_framework.routers import SimpleRouter, DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'mailings', views.MailingViewSet)


urlpatterns = [
    path(r'client/', views.ClientCreate.as_view(), name='client_create'),
    path(r'client/<int:pk>/', views.ClientRetrieve.as_view(), name='client_create'),
    path(r'client/update/<int:pk>/', views.ClientUpdate.as_view(), name='client_update'),
    path(r'client/destroy/<int:pk>/', views.ClientDestroy.as_view(), name='client_destroy'),
]

urlpatterns += router.urls
