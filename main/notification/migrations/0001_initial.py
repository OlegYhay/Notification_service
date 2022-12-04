# Generated by Django 4.1.3 on 2022-12-01 05:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('phone_number', models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+79603875356'. Up to 11 digits allowed.", regex='^\\+?1?\\d{10,11}$')], verbose_name='Мобильный телефон')),
            ],
        ),
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=30, verbose_name='Краткое описание рассылки')),
                ('date_dispatch', models.DateTimeField(auto_now=True, verbose_name='Дата отправки')),
                ('date_stop', models.DateTimeField(blank=True, null=True, verbose_name='Окончания рассылки')),
                ('text', models.TextField(verbose_name='Текст сообщения')),
            ],
        ),
        migrations.CreateModel(
            name='MobileOperator',
            fields=[
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False, verbose_name='Код мобильного оператора')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Тег')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now=True, verbose_name='Дата отправки')),
                ('status', models.CharField(choices=[('СОЗДАНО', 'Создано'), ('ОТПРАВЛЕНО', 'Отправлено'), ('УСПЕШНО', 'Успешно'), ('ОШИБКА', 'Ошибка')], default='СОЗДАНО', max_length=10, verbose_name='Статус')),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notification.client', verbose_name='Клиент')),
                ('mailing_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notification.mailing', verbose_name='Рассылка')),
            ],
        ),
        migrations.AddField(
            model_name='mailing',
            name='mobile_operator',
            field=models.ManyToManyField(related_name='mop_mail', to='notification.mobileoperator'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='tags',
            field=models.ManyToManyField(related_name='tags_mail', to='notification.tags', verbose_name='Теги фильтр'),
        ),
        migrations.AddField(
            model_name='client',
            name='mobile_operator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='notification.mobileoperator', verbose_name='Код оператора'),
        ),
        migrations.AddField(
            model_name='client',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='notification.tags', verbose_name='Теги'),
        ),
    ]