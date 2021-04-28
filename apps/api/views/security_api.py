from django.views.generic import View
from django.http import JsonResponse
from security.models import CollectorTasks, SudoScanResults, VulsScanResult, CveList, VulsScanTasks
import json
from utils.security.vuls_report_scan import config_builder


class SudoScan(View):

    def get(self, request):
        data = []
        task_obj = CollectorTasks.objects.all()
        for task in task_obj:
            result = {
                    'task_id': task.id,
                    'operator': task.operator,
                    'time_created': task.time_created.strftime("%Y-%m-%d %H:%M:%S"),
                    'status': task.status_dict[task.status],
                    'sudo_scan_result': []
                }
            data.append(result)
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data
        })

    def post(self, request):
        host_list = request.POST.get('host_list').lstrip().rstrip().split('\n')
        task_dict = {
            'host_list': json.dumps(host_list),
            'operator': request.user.username
        }
        task_obj = CollectorTasks.objects.create(**task_dict)
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': {'task_id': task_obj.id}
        })


class SudoScanResult(View):

    def get(self, request, *args, **kwargs):
        data = []
        task_id = kwargs['id']
        task_obj = CollectorTasks.objects.filter(id=task_id).first()
        result_obj_list = SudoScanResults.objects.filter(task_id=task_obj)
        for result_obj in result_obj_list:
            result = {
                'hostname': result_obj.hostname,
                'user': result_obj.user,
                'user_type': result_obj.user_type_dict[result_obj.user_type],
                'src_host': result_obj.src_host,
                'run_as': result_obj.run_as,
                'commands': result_obj.commands
            }
            data.append(result)
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data
        })


class VulScan(View):
    def get(self, request):
        data = []
        vuls_scan_result_qs = VulsScanResult.objects.all().order_by('scan_date')
        for result in vuls_scan_result_qs:
            cve_list = []
            for cve in result.cve_list.all():
                cve_list.append({
                    'cve_id': cve.cve_id,
                    'status': cve.status_dict[cve.status],
                    'details': cve.details,
                    'next_check_date': cve.next_check_date
                })

            data.append({
                'id': result.id,
                'server_name': result.server_name,
                'family': result.family,
                'release': result.release,
                'scan_date': result.scan_date,
                'cve_list': cve_list
            })
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data
        })

    def post(self, request):
        host_list = request.POST.get('host_list').lstrip().rstrip().split('\n')
        conf_file_id = config_builder(host_list)
        VulsScanTasks.objects.create(id_code=conf_file_id)

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': "created job with file code %s" % conf_file_id
        })


class VulScanDetail(View):
    def get(self, request, *args, **kwargs):
        data = []
        report_id = kwargs['id']
        cve_qs = VulsScanResult.objects.filter(id=report_id).first().cve_list.all()
        for cve in cve_qs:
            data.append({
                'cve_id': cve.cve_id,
                'affected_packages': json.loads(cve.affected_packages),
                'status': cve.status_dict[cve.status],
                'details': cve.details,
                'next_check_date': cve.next_check_date
            })
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'data': data
        })