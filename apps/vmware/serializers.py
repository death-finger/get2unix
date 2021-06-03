from vmware.models import DeployLists
from rest_framework import serializers
from utils.redis_client import RedisOperator
from get2unix.settings import VC_CACHE_DB
import json

state_to_str = {
        0: 'draft',
        1: 'added',
        2: 'verified',
        3: 'running',
        4: 'success',
        5: 'failed'
}


class InventorySerializer(serializers.Serializer):
    hostname = serializers.CharField()
    vc = serializers.CharField()
    guest = serializers.CharField()
    state = serializers.CharField()
    cpu = serializers.IntegerField()
    memory = serializers.IntegerField()
    ip = serializers.CharField()
    path = serializers.CharField()


class DeploySerializer(serializers.ModelSerializer):
    checked = serializers.BooleanField(default=False)

    class Meta:
        model = DeployLists
        read_only_fields = ['id', 'chain_id', 'user']
        exclude = ['token']

#
# class ChoicesField(serializers.Field):
#     def __init__(self, choices, **kwargs):
#         self._choices = choices
#         super(ChoicesField, self).__init__(**kwargs)
#
#     def to_representation(self, data):
#         return self._choices[data]
#
#     def to_internal_value(self, data):
#         return getattr(self._choices, data)