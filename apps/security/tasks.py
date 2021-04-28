from __future__ import absolute_import, unicode_literals
from celery import shared_task
from security.models import SudoTasks, AWXJobs, TaskJobs, CollectorTasks, VulsScanResult, VulsScanTasks
from utils.awx_client import AwxApi
from django.utils import timezone
from datetime import datetime
import json
from utils.security.sudo_scan import sudo_scan
from django.db.models import Max
from utils.security.vuls_report_scan import vuls_report_scan
from get2unix.settings import VULS_REPORT_PATH


def execute_task(task_list, task_type, awx_client):
    # TASK_TYPE:
    #     0 - sudo_add
    #     1 - sudo_remove
    #     2 - sudo_running
    #     3 - collector
    #     4 - collector_running
    #     5 - vuls_scan
    #     6 - vuls_scan_running
    for item in task_list:
        # sudo_add, sudo_remove, collector
        if task_type in (0, 1, 3):
            job_args = {}
            # sudo_add, sudo_remove
            if task_type in (0, 1):
                job_args = {
                    'host_list': json.loads(item.hosts),
                    'task_type': 0,
                    'sudo_user': json.loads(item.users),
                    'operator': item.operator,
                    'ticket': item.ticket,
                    'tag': 'add' if task_type == 0 else 'remove'
                }
            # collector
            elif task_type == 3:
                job_args = {
                    'host_list': json.loads(item.host_list),
                    'task_type': 1,
                }

            result = awx_client.run_task(**job_args)
            # sudo_add: pending => running
            if task_type == 0:
                item.status = 5
            # sudo_add: added => removing
            elif task_type == 1:
                item.status = 6
            # collector: pending => running
            elif task_type == 3:
                item.id_code = result['id_code']
                item.status = 1
            item.save()
            job_data = {
                'inv_id': result['inv_id'],
                'job_id': result['job_id'],
                'host_id_list': json.dumps(result['host_id_list'])
            }
            job_obj = AWXJobs.objects.create(**job_data)
            task_job = {
                'task_id': item.id,
                'task_type': 1 if task_type == 3 else 0,
                'job_id': job_obj
            }
            TaskJobs.objects.create(**task_job)
        # sudo running, collector running
        elif task_type in (2, 4):
            task_job = TaskJobs.objects.filter(task_id=item.id, task_type=0 if task_type == 2 else 1).first()
            job_obj = task_job.job_id
            result = awx_client.get('/api/v2/jobs/' + str(job_obj.job_id) + "/")
            if result['status'] in ('failed', 'unreachable', 'successful'):
                # collector: running -> awx_done
                if task_type == 4:
                    item.status = 2
                # sudo
                elif task_type == 2:
                    # failed
                    if result['status'] in ('failed', 'unreachable'):
                        item.status = 4
                    elif result['status'] == 'successful':
                        # running => added
                        if item.status == 5:
                            item.status = 1
                        # removing => sudo_scan
                        elif item.status == 6:
                            item.status = 7
                item.save()
                awx_client.run_cleanup_task(job_obj.inv_id, job_obj.host_id_list)
                job_obj.removed = True
                job_obj.save()
        # vuls scan
        elif task_type == 5:
            job_args = {'id_code': item.id_code, 'task_type': 2}
            result = awx_client.run_task(**job_args)
            item.status = 1
            item.save()
            job_data = {
                'inv_id': "N/A",
                'job_id': result['job_id'],
                'host_id_list': "N/A",
                'removed': True
            }
            job_obj = AWXJobs.objects.create(**job_data)
            task_job = {
                'task_id': item.id,
                'task_type': 2,
                'job_id': job_obj
            }
            TaskJobs.objects.create(**task_job)
        # vuls scan running
        elif task_type == 6:
            task_job = TaskJobs.objects.filter(task_id=item.id, task_type=2).first()
            job_obj = task_job.job_id
            result = awx_client.get('/api/v2/jobs/' + str(job_obj.job_id) + "/")
            if result['status'] in ('failed', 'unreachable', 'successful'):
                item.status = 2
            item.save()


@shared_task
def run_sudo_tasks():
    awx_client = AwxApi()
    # task_type == 0 in execute_task
    sudo_add_list = SudoTasks.objects.filter(status=0)
    execute_task(sudo_add_list, 0, awx_client)

    # task_type == 1 in execute_task
    sudo_remove_list = SudoTasks.objects.filter(status=2)
    execute_task(sudo_remove_list, 1, awx_client)

    # task_type == 2 in execute_task
    sudo_running_list = SudoTasks.objects.filter(status__in=(5, 6))
    execute_task(sudo_running_list, 2, awx_client)

    # add sudo_scan task for removed sudo
    sudo_scan_list = SudoTasks.objects.filter(status=7)
    for item in sudo_scan_list:
        sudo_collector_dict = {
            "host_list": item.hosts,
            "operator": item.ticket
        }
        CollectorTasks.objects.create(**sudo_collector_dict)
        item.status = 3
        item.save()


@shared_task
def run_collector_tasks():
    awx_client = AwxApi()

    # task_type == 3 in execute_task
    collector_list = CollectorTasks.objects.filter(status=0)
    execute_task(collector_list, 3, awx_client)

    # task_type == 4 in execute_task
    collector_running_list = CollectorTasks.objects.filter(status=1)
    execute_task(collector_running_list, 4, awx_client)

    collector_parse_list = CollectorTasks.objects.filter(status=2)
    for task_obj in collector_parse_list:
        sudo_scan(task_obj)


@shared_task
def run_sudo_cleanup():
    awx_client = AwxApi()
    cleanup_list = AWXJobs.objects.filter(removed=False)
    for item in cleanup_list:
        result = awx_client.get('/api/v2/jobs/' + str(item.job_id) + "/")
        if result['status'] in ('failed', 'successful'):
            awx_client.run_cleanup_task(item.inv_id, item.host_id_list)
            item.removed = True
            item.save()


@shared_task
def run_sudo_expire_scan():
    check_list = SudoTasks.objects.filter(status=1)
    for item in check_list:
        time_delta = timezone.now() - item.time_created
        if time_delta.days > item.effective_days:
            item.status = 2
            item.save()


@shared_task
def run_vuls_scan():
    awx_client = AwxApi()
    scan_pending_list = VulsScanTasks.objects.filter(status=0)
    scan_running_list = VulsScanTasks.objects.filter(status=1)
    if scan_running_list:
        execute_task(scan_running_list, 6, awx_client)
    elif scan_pending_list:
        execute_task(scan_pending_list, 5, awx_client)


@shared_task
def run_vuls_report_scan():
    start_timedate = VulsScanResult.objects.all().aggregate(Max('scan_date'))['scan_date__max']
    start_timedate = start_timedate if start_timedate else datetime(1000, 1, 1, 0, 0, 1, tzinfo=timezone.get_current_timezone())
    vuls_report_scan(VULS_REPORT_PATH, start_timedate)
