# Notification_service
Тестовое задание для Фабрики решений
Работа с API рассылкой на номера тлф
отложенные задачи Celery
Авторизация через OAuth

Для развертывания выполните следующие шаги: 

1)Клонируйте репозиторий командой

 git clone 'https://gitlab.com/OlegYhay/Notification_service.git'
 
 2)Установите все зависимости : 

2.1) Перейдите в папку Notification_service командой

 cd Notification_service
 
 2.2) Установите все необходимые пакеты командой 
 
pip install -r requirements.txt

 2.3) Запустите на своей машине redis-server
 
 3)Запустите сервер django
 
 4)Запустите worker командой(находясь в папке main):
 
 celery -A main worker -l info -P gevent
