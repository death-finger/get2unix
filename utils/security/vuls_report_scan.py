import json
import os
from security.models import CveList, VulsScanResult
from django.utils import timezone
from datetime import datetime
from get2unix.settings import VULS_CONF_PATH
import hashlib
import time
from utils.awx_client import AwxApi


TEMPLATE_HEADER = """[default]
port = "22"
user = "itans"
keyPath = "/root/.ssh/id_rsa"
scanMode = ["fast-root", "offline"]
[servers]
"""
TEMPLATE = """[servers.%s]
host = "%s"
"""


def vuls_report_scan(report_path, start_timedate):

    # print('REPORT PATH: %s\nSTART TIMESTAMP: %s' % (report_path, start_timedate))

    scan_date_list = []
    for root, dirs, files in os.walk(report_path):
        for scan_date in dirs:
            scan_date_list.append(scan_date)

    # print("SCAN_DATE_LIST: %s" % scan_date_list)

    for item in sorted(scan_date_list):

        # print("START SCAN ==> %s" % item)

        item_timedate = datetime.strptime(item, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.get_current_timezone())

        if item_timedate < start_timedate:

            # print("SKIPPED FOLDER ==> %s" % item)

            continue
        for root, dirs, files in os.walk(os.path.join(report_path, item)):
            for file in files:
                if file.split('.')[-1] == 'json':

                    # print('FILE: %s' % file)

                    full_path = os.path.join(root, file)
                    with open(full_path, 'r') as report:
                        report_data = json.load(report)

                        # print("REPORT_DATA: %s" % report_data)

                        report_cve_list = []
                        # CVE List Update
                        for cve_id in report_data['scannedCves'].keys():
                            report_cve_list.append(cve_id)
                            cve_list_obj = CveList.objects.filter(cve_id=cve_id).first()
                            if cve_list_obj:
                                defer_date_delta = cve_list_obj.next_check_date - timezone.now() if cve_list_obj.next_check_date else 0
                                if (cve_list_obj.status == 3 and defer_date_delta > 0) or cve_list_obj.status == 2:
                                    continue
                            cve_dict = {
                                'cve_id': cve_id,
                                'affected_packages': json.dumps(report_data['scannedCves'][cve_id]['affectedPackages']),
                            }
                            for pkg in report_data['scannedCves'][cve_id]['affectedPackages']:
                                if pkg.get('fixedIn'):
                                    cve_dict['status'] = 1
                                    cve_dict['details'] = pkg['fixedIn']
                                    break
                                else:
                                    cve_dict['status'] = 0
                                    cve_dict['details'] = pkg['fixState']
                            if not cve_list_obj:
                                CveList.objects.create(**cve_dict)
                            else:
                                cve_list_obj.affected_packages = cve_dict['affected_packages']
                                cve_list_obj.status = cve_dict['status']
                                cve_list_obj.details = cve_dict['details']
                                cve_list_obj.save()

                        # VulsScanResult Update
                        server_name = report_data['serverName']
                        cve_queryset = []
                        for cve in report_cve_list:
                            cve_obj = CveList.objects.filter(cve_id=cve).first()
                            cve_queryset.append(cve_obj)
                        report_dict = {
                            'server_name': server_name,
                            'family': report_data['family'],
                            'release': report_data['release'],
                            'scan_date': item_timedate,
                        }
                        vuls_scan_result_obj = VulsScanResult.objects.filter(server_name=server_name).first()
                        if vuls_scan_result_obj:
                            vuls_scan_result_obj.scan_date = report_dict['scan_date']
                            vuls_scan_result_obj.cve_list.set(cve_queryset)
                            vuls_scan_result_obj.save()
                        else:
                            res = VulsScanResult.objects.create(**report_dict)
                            res.cve_list.set(cve_queryset)
                            res.save()


def config_builder(hosts):
    conf_file_content = TEMPLATE_HEADER
    for host in hosts:
        conf_file_content += TEMPLATE % (host, host)
    id_code = hashlib.md5(str(time.time()).encode()).hexdigest()
    with open(VULS_CONF_PATH + '/config.toml.%s' % id_code, 'w', encoding='utf8') as vuls_conf_file:
        vuls_conf_file.write(conf_file_content)
    return id_code
