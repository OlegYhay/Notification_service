from rest_framework import serializers
from .models import *


class SerializerClient(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['mobile_operator']


class SerializerMailings(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'
        read_only_fields = ['id_task']


class Serializer_detail_stat(serializers.Serializer):
    status = serializers.CharField(max_length=255)
    count = serializers.IntegerField()


class Serializer_all_stat(serializers.Serializer):
    mailing_id = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=255)
    count = serializers.IntegerField()
