from vmware.models import DeployLists, Snapshots
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


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshots
        read_only_fields = ['id', ]
        fields = ['id', 'vm_name', 'vm_vc', 'vm_path', 'time_created', 'keep_days', 'snap_name',
                  'snap_desc', 'operator', 'state']

    def create(self, validated_data):
        snapshot = Snapshots(**validated_data)
        snapshot.save()
        return snapshot

    def update(self, validated_data):
        results = []
        for item in validated_data:
            snapshot_obj = Snapshots.objects.filter(vm_name=item.vm_name)
            snapshot_obj.update(**item)
            results.append(snapshot_obj)
        return results
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