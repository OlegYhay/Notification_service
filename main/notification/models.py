from django.core.validators import RegexValidator
from django.db import models


# Модель рассылки
class Mailing(models.Model):
    description = models.CharField(max_length=30, verbose_name='Краткое описание рассылки')
    date_dispatch = models.DateTimeField(verbose_name='Дата отправки')
    date_stop = models.DateTimeField(verbose_name='Окончания рассылки', blank=True, null=True)
    text = models.TextField(verbose_name='Текст сообщения')
    tags = models.ManyToManyField('Tags', verbose_name='Теги фильтр', related_name='tags_mail')
    mobile_operator = models.ManyToManyField('MobileOperator', related_name='mop_mail')
    # идентификатор задачи в celery, для отмены или редактирование задачи
    id_task = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.description}-{self.date_dispatch}'


# Модель клиента
class Client(models.Model):
    name = models.CharField(max_length=233, verbose_name='ФИО')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,11}$',
                                 message="Phone number must be entered in the format: '+79603875356'. Up to 11 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=12,
                                    verbose_name='Мобильный телефон')
    mobile_operator = models.ForeignKey('MobileOperator', on_delete=models.SET_NULL, null=True,
                                        verbose_name='Код оператора')
    tags = models.ManyToManyField('Tags', related_name='tags', verbose_name='Теги')

    def __str__(self):
        return f'{self.name}({self.phone_number})'


class Message(models.Model):
    STATUS = (
        ("СОЗДАНО", "Создано"),
        ("ОТПРАВЛЕНО", "Отправлено"),
        ("УСПЕШНО", "Успешно"),
        ("ОШИБКА", "Ошибка"),
    )
    date_created = models.DateTimeField(auto_now=True, verbose_name='Дата отправки')
    status = models.CharField(choices=STATUS, default="СОЗДАНО", verbose_name='Статус', max_length=10)
    mailing_id = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')


# Коды мобильных операторов
class MobileOperator(models.Model):
    code = models.CharField(max_length=5, verbose_name='Код мобильного оператора', primary_key=True)

    def __str__(self):
        return self.code


# Теги клиентов
class Tags(models.Model):
    name = models.CharField(max_length=255, verbose_name='Тег')

    def __str__(self):
        return self.name
