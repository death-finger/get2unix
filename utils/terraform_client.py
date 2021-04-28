import subprocess
from get2unix.settings import TF_BIN, TF_BASE

TEMPLATE = """
data "vsphere_virtual_machine" "%s" {
  name = "%s"
}
resource "vsphere_virtual_machine_snapshot" "%s" {
  virtual_machine_uuid = data.vsphere_virtual_machine.%s.id
  snapshot_name = "%s"
  description = "%s"
  memory = "%s"
  quiesce = "%s"
  remove_children = "%s"
  consolidate = "%s"
}
"""


def tf_file_builder(vcenter, tasks):
    with open(TF_BASE + "/%s/main.tf" % vcenter, 'w', encoding='utf-8') as tf_file:
        if not tasks:
            tf_file.write('#NO SNAPSHOT EXISTS')
        else:
            for task in tasks:
                print(TEMPLATE % (task.vm_name, task.vm_path + task.vm_name, task.vm_name, task.vm_name,
                                      task.snap_name, task.snap_desc, str(task.snap_mem).lower(), str(task.snap_qui).lower(),
                                      str(task.snap_remove_child).lower(), str(task.snap_sol).lower()))
                tf_file.write(TEMPLATE % (task.vm_name, task.vm_path + task.vm_name, task.vm_name, task.vm_name,
                                      task.snap_name, task.snap_desc, str(task.snap_mem).lower(), str(task.snap_qui).lower(),
                                      str(task.snap_remove_child).lower(), str(task.snap_sol).lower()))
        tf_file.write('#EOF')
        tf_file.flush()
    return {'tf_file': TF_BASE + "/%s/main.tf" % vcenter}


def terraform_runner(folder, action, username, password, vcenter_address):
    cmd = [TF_BIN, '-chdir=%s' % folder, action, '-var', 'vsphere_user=%s' % username, '-var',
           'vsphere_password=%s' % password, '-var', 'vsphere_server=%s.corp.ebay.com' % vcenter_address, '-no-color',
           '-input=false']
    if action == 'apply':
        cmd.append('-auto-approve')
    proc_running = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        if proc_running.poll() is None:
            proc_running.wait(180)
        elif proc_running.poll() == 0:
            return {'code': proc_running.poll(), 'msg': proc_running.communicate()[0]}
        else:
            return {'code': proc_running.poll(), 'msg': proc_running.communicate()[1]}
