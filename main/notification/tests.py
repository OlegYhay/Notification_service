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

    def test_create_client_without_login(self):
        url = reverse('client_create')
        response = self.client.post(url, self.client1, format='json')
        self.assertNotEqual(Client.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_update_client_without_login(self):
        new_user = Client(name=self.client1['name'],
                          phone_number=self.client1['phone_number'], )
        new_user.save()
        data = {
            'name': 'Edit user1',
            'phone_number': '+79603875356',
            'tags': [1, 2],
        }
        url = reverse('client_update', kwargs={'pk': 1})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_destroy_client_without_login(self):
        new_user = Client(name=self.client1['name'],
                          phone_number=self.client1['phone_number'], )
        new_user.save()
        url = reverse('client_destroy', kwargs={'pk': 1})
        response = self.client.delete(url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Client.objects.count(), 1)


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

    def test_create_mailing_without_login(self):
        url = reverse('mailing-list')
        response = self.client.post(url, self.mailing, format='json')
        self.assertEqual(Mailing.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_mailing(self):
        url = reverse('mailing-detail', kwargs={'pk': 1})
        self.client.login(**self.user)
        Mailing(description=self.mailing['description'],
                date_dispatch="2022-12-01T15:38:00+03:00",
                date_stop="2022-12-01T15:38:00+03:00",
                text='Тестовая рассылка', ).save()

        date = {
            'description': 'Edit рассылка',
            'date_dispatch': "2022-12-01T15:38:00+03:00",
            'date_stop': "2022-12-01T15:38:00+03:00",
            'text': 'Тестовая рассылка2',
            'tags': [1],
            'mobile_operator': ["+796"],
        }
        response = self.client.put(url, date, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Mailing.objects.first().description, 'Edit рассылка')
        self.assertEqual(Mailing.objects.first().text, 'Тестовая рассылка2')

    def test_delete_mailing(self):
        url = reverse('mailing-detail', kwargs={'pk': 1})
        self.client.login(**self.user)
        Mailing(description=self.mailing['description'],
                date_dispatch="2022-12-01T15:38:00+03:00",
                date_stop="2022-12-01T15:38:00+03:00",
                text='Тестовая рассылка', ).save()
        response = self.client.delete(url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
