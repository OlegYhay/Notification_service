import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Create your tests here.
from .models import Tags, Client, Mailing, MobileOperator


class TestCRUDClient(APITestCase):
    def setUp(self) -> None:
        Tags(name='мтс').save()
        Tags(name='it рассылка').save()
        self.user = {
            'username': 'admin',
            'password': '1',
        }
        User.objects.create_user(**self.user)
        self.client1 = {
            'name': 'Test user1',
            'phone_number': '+79603875356',
            'tags': [1, 2],
        }

        self.client2 = {
            'name': 'Test user1',
            'phone_number': 'bad phone',
            'tags': ['i  ,don\'t,know'],
        }

    # correct create client
    def test_create_client(self):
        url = reverse('client_create')
        self.client.login(**self.user)
        response = self.client.post(url, self.client1, format='json')
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(self.client1['name'], Client.objects.get(id=1).name)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bad_client(self):
        url = reverse('client_create')
        self.client.login(**self.user)
        response = self.client.post(url, self.client2, format='json')
        self.assertNotEqual(Client.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # test correct update client
    def test_update_client(self):
        new_user = Client(name=self.client1['name'],
                          phone_number=self.client1['phone_number'], )
        new_user.save()
        self.client.login(**self.user)
        data = {
            'name': 'Edit user1',
            'phone_number': '+79603875356',
            'tags': [1, 2],
        }
        url = reverse('client_update', kwargs={'pk': 1})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Client.objects.get(id=1).name, 'Edit user1')

    # test correct destroy client
    def test_destroy_client(self):
        new_user = Client(name=self.client1['name'],
                          phone_number=self.client1['phone_number'], )
        new_user.save()
        self.client.login(**self.user)
        url = reverse('client_destroy', kwargs={'pk': 1})
        response = self.client.delete(url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Client.objects.count(), 0)


class TestCRUDMailing(APITestCase):

    def setUp(self) -> None:
        self.mailing = {
            'description': 'Тестовая рассылка',
            'date_dispatch': "2022-12-01T15:38:00+03:00",
            'date_stop': "2022-12-01T15:38:00+03:00",
            'text': 'Тестовая рассылка',
            'tags': [1],
            'mobile_operator': ["+796"],
        }

        self.user = {
            'username': 'admin',
            'password': '1',
        }
        User.objects.create_user(**self.user)
        Tags(name='mts').save()
        MobileOperator(code="+796").save()

    def test_create_mailing(self):
        url = reverse('mailing-list')
        self.client.login(**self.user)
        response = self.client.post(url, self.mailing, format='json')
        print(response)
        self.assertEqual(Mailing.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


