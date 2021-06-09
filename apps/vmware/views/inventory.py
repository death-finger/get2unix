from utils.redis_client import RedisOperator
from get2unix.settings import VC_CACHE_DB
import json
from rest_framework import viewsets
from rest_framework.response import Response
from vmware.serializers import InventorySerializer


class InventoryViewSet(viewsets.ViewSet):

    def list(self, request):

        data = []
        for vc, rdb in VC_CACHE_DB.items():
            r = RedisOperator(rdb)
            for res in r.keys('VM_*'):
                vm = json.loads(r.get(res))
                data.append({
                    'hostname': str(res)[5:-1],
                    'vc': vc,
                    'guest': vm['guestFullName'],
                    'state': vm['guestState'],
                    'cpu': vm['numCpu'] if vm['numCpu'] else 0,
                    'memory': round(vm['memorySizeMB'] / 1024, 1) if vm['memorySizeMB'] else 0,
                    'ip': vm['ipAddress'],
                    'path': vm['vmPathName'],
                })
        serializer = InventorySerializer(data, many=True)
        return Response(serializer.data)
