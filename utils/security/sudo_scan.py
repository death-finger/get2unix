from pysudoers import Sudoers
import os
from security.models import SudoScanResults
import tarfile
from get2unix.settings import SUDO_EXCLUDE_USERS, SUDO_EXCLUDE_GROUPS

def sudo_scan(task_obj):
    tar_file = tarfile.open('tmp/sudo_collector.tgz.' + task_obj.id_code)
    tar_file.extractall('tmp/' + task_obj.id_code)
    folder = 'tmp/' + task_obj.id_code + '/sudo_collector'

    host_list = []
    result = []

    # scan folder to collect all host names
    for root, dirs, files in os.walk(folder):
        for name in dirs:
            if name != 'sudoers.d':
                host_list.append(name)

    # sudo analyze
    for host in host_list:
        for root, dirs, files in os.walk(folder + '/' + host):
            for name in files:
                if name.split('.')[-1] != 'swp':
                    full_path = os.path.join(root, name)
                    sobj = Sudoers(path=full_path)
                    for rule in sobj.rules:
                        try:
                            user_tmp = {}
                            if len(rule['users']) == 1:
                                if (rule['users'][0] in SUDO_EXCLUDE_USERS) or (rule['users'][0][1:] in SUDO_EXCLUDE_GROUPS):
                                    continue
                                user_tmp['user'] = rule['users'][0]
                                # user_type = 2: NET_GROUP
                                if user_tmp['user'].startswith('+'):
                                    user_tmp['user_type'] = 2
                                # user_type = 1: LOCAL_GROUP
                                elif user_tmp['user'].startswith('%'):
                                    user_tmp['user_type'] = 1
                                # user_type = 0: USER
                                else:
                                    # check if this is a user group alias
                                    try:
                                        user_tmp['user'] = sobj.user_aliases[user_tmp['user']]
                                    except:
                                        pass
                                    if (len(user_tmp['user']) == 1) and user_tmp['user'][0] in SUDO_EXCLUDE_USERS:
                                        continue
                                    user_tmp['user_type'] = 0
                            try:
                                cmd_tmp = sobj.cmnd_aliases[rule['commands'][0]['command']]
                            except:
                                cmd_tmp = rule['commands'][0]['command']

                            sudo_dict = {
                                'hostname': host,
                                'user': user_tmp['user'],
                                'user_type': user_tmp['user_type'],
                                'src_host': rule['hosts'][0],
                                'run_as': rule['commands'][0]['run_as'][0],
                                'commands': cmd_tmp,
                                'task_id': task_obj
                            }
                            result.append(SudoScanResults(**sudo_dict))

                        except Exception as e:
                            print('Error: %s' % e)

    SudoScanResults.objects.bulk_create(result)
    # change the status from AWX_DONE to DONE
    task_obj.status = 3
    task_obj.save()
