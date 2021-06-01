import requests
import json
import time
import hashlib
from urllib import parse
from get2unix.settings import AWX_URL, G2U_HOST, AWX_USERNAME, AWX_PASSWORD, AWX_CLIENT_ID, AWX_CLIENT_SECERT, AWX_ORG_NAME
from get2unix.settings import AWX_INV_PREFIX, AWX_INV_DESC, AWX_SUDO_TEMPLATE, AWX_COLLECTOR_TEMPLATE
from get2unix.settings import VULS_HOST, VULS_PATH, VULS_CONF_PATH, VULS_REPORT_PATH, AWX_VULSSCAN_TEMPLATE


class AwxApi():
    HEADERS = {"Content-Type": "application/json"}
    AUTH = (AWX_CLIENT_ID, AWX_CLIENT_SECERT)
    ACCESS_TOKEN = ""
    REFRESH_TOKEN = ""

    def __init__(self):
        self.get_token()

    def get_token(self):
        data = {"grant_type": "password", "username": AWX_USERNAME, "password": AWX_PASSWORD}
        rsp = json.loads(
            requests.post(AWX_URL + "/api/o/token/", auth=self.AUTH, data=data, verify=False,
                          headers={"Content-Type": "application/x-www-form-urlencoded"}).content)
        self.ACCESS_TOKEN = rsp['access_token']
        self.REFRESH_TOKEN = rsp['refresh_token']

    def post(self, uri, data):
        rsp = requests.post(AWX_URL + uri, data=json.dumps(data),
                           headers={"Authorization": "Bearer %s" % self.ACCESS_TOKEN,
                                    "Content-Type": "application/json"}, verify=False)
        return json.loads(rsp.content)

    def put(self, uri, uid, data):
        rsp = requests.put(AWX_URL + uri + str(uid) + '/', data=json.dumps(data),
                           headers={"Authorization": "Bearer %s" % self.ACCESS_TOKEN,
                                    "Content-Type": "application/json"}, verify=False)
        return json.loads(rsp.content)

    def delete(self, uri, uid):
        rsp = requests.delete(AWX_URL + uri + str(uid) + '/',
                              headers={"Authorization": "Bearer %s" % self.ACCESS_TOKEN}, verify=False)
        return rsp

    def get(self, uri):
        rsp = requests.get(AWX_URL + uri, headers={"Authorization": "Bearer %s" % self.ACCESS_TOKEN,
                                                   "Content-Type": "application/json"}, verify=False)
        return json.loads(rsp.content)

    def get_stdout(self, uri):
        rsp = requests.get(AWX_URL + uri, headers={"Authorization": "Bearer %s" % self.ACCESS_TOKEN,
                                                   "Content-Type": "application/json"}, verify=False)
        return rsp.content

    def search(self, uri, key, value):
        data = parse.quote(value)
        return self.get(uri + '?%s=%s' % (key, data))

    def run_task(self, **job_args):
        job_args = job_args
        if not job_args['task_type'] == 2:
            id_code, inv_id, host_id_list = self.create_inventory(job_args['host_list'])
        else:
            id_code, inv_id, host_id_list = 'N/A'
        template_name = ""
        job_tags = ""
        job_vars = ""
        # task_type == 0: sudo_add or sudo_remove
        if job_args['task_type'] == 0:
            users_remove = []
            for user in job_args['sudo_user']:
                users_remove.append(user[1:] if user.startswith('+') else user)
            template_name = AWX_SUDO_TEMPLATE
            job_vars = {'USERS': job_args['sudo_user'], 'USERS_REMOVE': users_remove, 'DATE': time.ctime(),
                        'OPERATOR': job_args['operator'], 'TICKET': job_args['ticket'],
                        'NOPASSWD': "NOPASSWD:" if job_args['nopasswd'] else ""}
            job_tags = job_args['tag']
        # task_type == 1: sudo collector
        elif job_args['task_type'] == 1:
            template_name = AWX_COLLECTOR_TEMPLATE
            job_vars = {'FILENAME': id_code, 'G2U_HOST': G2U_HOST}
            job_tags = 'all'
        # task_type == 2: vuls scan
        elif job_args['task_type'] == 2:
            template_name = AWX_VULSSCAN_TEMPLATE
            job_vars = {'VULS_CONF_FILE': "config.toml.%s" % job_args['id_code'], 'G2U_HOST': G2U_HOST,
                        'VULS_HOST': VULS_HOST}
        template_id = self.search("/api/v2/job_templates/", 'name', template_name)['results'][0]['id']
        if not job_args['task_type'] == 2:
            job_data = {'inventory': inv_id, "job_tags": job_tags, 'extra_vars': job_vars}
        else:
            job_data = {'extra_vars': job_vars}
        job_id = self.post('/api/v2/job_templates/' + str(template_id) + "/launch/", job_data)['job']
        return {'inv_id': inv_id, 'host_id_list': host_id_list, 'job_id': job_id, 'id_code': id_code}

    def create_inventory(self, host_list):
        org_id = self.search('/api/v2/organizations/', 'name', AWX_ORG_NAME)['results'][0]['id']
        id_code = hashlib.md5(str(time.time()).encode()).hexdigest()
        inv_data = {"name": AWX_INV_PREFIX + "-%s" % id_code,
                    "description": AWX_INV_DESC,
                    'organization': org_id}
        inv_id = self.post('/api/v2/inventories/', inv_data)['id']
        host_id_list = []
        for host in host_list:
            host_data = {"name": host, "inventory": inv_id, 'enabled': True}
            host_id = self.post('/api/v2/hosts/', host_data)['id']
            host_id_list.append(host_id)
        return id_code, inv_id, host_id_list

    def run_cleanup_task(self, inv_id, host_id_list):
        for host_id in json.loads(host_id_list):
            self.delete('/api/v2/hosts/', host_id)
        self.delete('/api/v2/inventories/', inv_id)
