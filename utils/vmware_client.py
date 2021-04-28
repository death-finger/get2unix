import uuid
from contextlib import contextmanager
from pyVim import connect
from pyVmomi import vim, vmodl
import json
import redis
import threading
from vmware.models import Tasks, DeployLists
from get2unix.settings import RUNNING_ENV


REDIS_LIVETIME = 9999999


class VMWare(object):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    ########################
    #    Base Functions    #
    ########################
    def connect(self):
        return connect.SmartConnectNoSSL(
            host=self.host,
            user=self.username,
            pwd=self.password,
            port=self.port
        )

    def is_task_done(self, task):
        state = task.info.state
        if state == vim.TaskInfo.State.success:
            return True, None

        if state == vim.TaskInfo.State.error:
            return True, str(task.info.error.msg)

        return False, None

    def wait_for_tasks(self, vmware_client, tasks):
        """Given the service instance si and tasks, it returns after all the
       tasks are complete
       """
        property_collector = vmware_client.RetrieveContent().propertyCollector
        task_list = [str(task) for task in tasks]
        # Create filter
        obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                     for task in tasks]
        property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                                   pathSet=[],
                                                                   all=True)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        filter_spec.propSet = [property_spec]
        pcfilter = property_collector.CreateFilter(filter_spec, True)
        try:
            version, state = None, None
            # Loop looking for updates till the state moves to a completed state.
            while len(task_list):
                update = property_collector.WaitForUpdates(version)
                for filter_set in update.filterSet:
                    for obj_set in filter_set.objectSet:
                        task = obj_set.obj
                        task_model = Tasks.objects.filter(chain_id=task.info.eventChainId)
                        for change in obj_set.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                                msg = task.info.description.message if task.info.description else ""
                                task_model.update(progress=change.val.progress, state=state,
                                                  msg=msg)
                            elif change.name == 'info.state':
                                state = change.val
                                msg = task.info.description.message if task.info.description else ""
                                task_model.update(state=state, msg=msg)
                            else:
                                continue

                            if not str(task) in task_list:
                                continue

                            if state == vim.TaskInfo.State.success:
                                # Remove task from taskList
                                task_list.remove(str(task))
                                msg = task.info.description.message if task.info.description else ""
                                task_model.update(progress=100, msg=msg)
                                DeployLists.objects.filter(chain_id=task.info.eventChainId).update(state=4)
                            elif state == vim.TaskInfo.State.error:
                                task_model.update(progress=100, msg=task.info.error.msg + task.info.error.faultMessage[0].message)
                                DeployLists.objects.filter(chain_id=task.info.eventChainId).update(state=5)
                                raise task.info.error
                # Move to next version
                version = update.version
        finally:
            if pcfilter:
                pcfilter.Destroy()

    def wait_for_tasks_async(self, vmware_client, tasks):
        threading.Thread(target=self.wait_for_tasks, args=(vmware_client, tasks)).start()

    def get_obj(self, vmware_client, vimtype, name, folder=None):
        """
        Return an object by name, if name is None the
        first found object is returned
        """
        obj = None
        content = vmware_client.RetrieveContent()

        if folder is None:
            folder = content.rootFolder

        container = content.viewManager.CreateContainerView(folder, [vimtype], True)
        for c in container.view:
            if c.name == name:
                obj = c
                break

        container.Destroy()
        return obj

    @contextmanager
    def client_session(self):
        vmware_client = self.connect()
        try:
            yield vmware_client
        finally:
            connect.Disconnect(vmware_client)

    ########################
    #  VC Object Actions   #
    ########################

    def get_datacenter(self, vmware_client, datacenter_name):
        return self.get_obj(vmware_client, vim.Datacenter, datacenter_name)

    def get_folder(self, vmware_client, folder_name, datacenter):
        # TODO: find folder in DC
        return self.get_obj(vmware_client, vim.Folder, folder_name)

    def get_image(self, vmware_client, image_name, datacenter):
        return self.get_obj(vmware_client, vim.VirtualMachine, image_name, folder=datacenter.vmFolder)

    def get_network(self, vmware_client, network_name):
        return self.get_obj(vmware_client, vim.Network, network_name)

    def get_cluster(self, vmware_client, cluster_name, datacenter):
        return self.get_obj(vmware_client, vim.ClusterComputeResource, cluster_name, folder=datacenter.hostFolder)

    def get_host(self, vmware_client, host_name):
        return self.get_obj(vmware_client, vim.HostSystem, host_name)

    def get_datastore(self, vmware_client, datastore_name, datacenter):
        return self.get_obj(vmware_client, vim.Datastore, datastore_name, folder=datacenter.datastoreFolder)

    def get_port_group(self, vmware_client, port_group_name, datacenter):
        return self.get_obj(vmware_client, vim.dvs.DistributedVirtualPortgroup, port_group_name,
                            folder=datacenter.networkFolder)

    def get_task(self, vmware_client, task_key):
        task = vim.Task(task_key)
        task._stub = vmware_client._stub
        return task

    def get_event(self, vmware_client, chain_id):
        em = vmware_client.content.eventManager
        efs = vim.event.EventFilterSpec()
        efs.eventChainId = chain_id
        return em.QueryEvent(efs)

    def get_vm_cust_spec(self, vmware_client, name):
        return vmware_client.content.customizationSpecManager.Get(name)

    ########################
    #    Disk Actions      #
    ########################

    def get_disk(self, vmware_client, disk_id, datastore):
        vStorageManager = vmware_client.RetrieveContent().vStorageObjectManager
        return vStorageManager.RetrieveVStorageObject(id=disk_id, datastore=datastore)

    def get_disk_size(self, vm):
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == "Hard disk 1":
                return dev.capacityInBytes

        return 0

    def create_disk(self, vmware_client, disk_name, size, datastore):
        vStorageManager = vmware_client.RetrieveContent().vStorageObjectManager

        spec = vim.vslm.CreateSpec()
        spec.name = disk_name
        spec.capacityInMB = size * 1024
        spec.backingSpec = vim.vslm.CreateSpec.DiskFileBackingSpec()
        spec.backingSpec.provisioningType = "thin"
        #spec.backingSpec.provisioningType = "eagerZeroedThick"
        spec.backingSpec.datastore = datastore

        task = vStorageManager.CreateDisk_Task(spec)
        self.wait_for_tasks(vmware_client, [task])
        vStorageObject = task.info.result

        return vStorageObject.config.name.name

    def clone_disk(self, vmware_client, disk_name, disk_id, datastore):
        vStorageManager = vmware_client.RetrieveContent().vStorageObjectManager

        spec = vim.vslm.CloneSpec()
        spec.name = disk_name
        spec.backingSpec = vim.vslm.CreateSpec.DiskFileBackingSpec()
        spec.backingSpec.datastore = datastore
        spec.backingSpec.provisioningType = "thin"
        task = vStorageManager.CloneVStorageObject_Task(id=vim.vslm.ID(id=disk_id), datastore=datastore, spec=spec)
        return task

    def delete_disk(self, vmware_client, disk_id, datastore):
        vStorageManager = vmware_client.RetrieveContent().vStorageObjectManager
        task = vStorageManager.DeleteVStorageObject_Task(id=vim.vslm.ID(id=disk_id), datastore=datastore)
        self.wait_for_tasks(vmware_client, [task])

    def grow_disk(self, vmware_client, disk_id, size, datastore):
        vStorageManager = vmware_client.RetrieveContent().vStorageObjectManager
        task = vStorageManager.ExtendDisk_Task(id=vim.vslm.ID(id=disk_id), datastore=datastore,
                                               newCapacityInMB=size * 1024)
        self.wait_for_tasks(vmware_client, [task])

    def resize_root_disk(self, vmware_client, new_size, vm):
        virtual_disk_device = None

        # Find the disk device
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == "Hard disk 1":
                virtual_disk_device = dev
                break

        virtual_disk_spec = vim.vm.device.VirtualDeviceSpec()
        virtual_disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        virtual_disk_spec.device = virtual_disk_device
        virtual_disk_spec.device.capacityInBytes = new_size * (1024 ** 3)
        virtual_disk_spec.device.backing.thinProvisioned = True

        spec = vim.vm.ConfigSpec()
        spec.deviceChange = [virtual_disk_spec]
        task = vm.ReconfigVM_Task(spec=spec)
        self.wait_for_tasks(vmware_client, [task])

    def attach_disk(self, vmware_client, disk_id, datastore, vm):
        task = vm.AttachDisk_Task(diskId=vim.vslm.ID(id=disk_id), datastore=datastore)
        self.wait_for_tasks(vmware_client, [task])

    def detach_disk(self, vmware_client, disk_id, vm):
        task = vm.DetachDisk_Task(diskId=vim.vslm.ID(id=disk_id))
        try:
            self.wait_for_tasks(vmware_client, [task])
        except vim.fault.NotFound:
            # Ignore error if the disk is already detached
            pass

    ########################
    #      VM Actions      #
    ########################
    def get_vm_by_uuid(self, vmware_client, vm_uuid):
        return vmware_client.content.searchIndex.FindByUuid(uuid=vm_uuid, vmSearch=True, instanceUuid=True)

    # VM Inventory 缓存的实际执行程序
    # 当 self.scan_folder_recursively 发现当前对象是 vim.VirtualMachine 时调用
    def get_vm_info(self, vm, redis_client, **kwargs):
        # print(kwargs)
        try:
            vm_dict = {
                'annotation': vm.summary.config.annotation,
                'guestFullName': vm.summary.config.guestFullName,
                'memorySizeMB': vm.summary.config.memorySizeMB,
                'numCpu': vm.summary.config.numCpu,
                'vmPathName': vm.summary.config.vmPathName,
                'instanceUuid': vm.summary.config.instanceUuid,
                'template': vm.config.template,
                'guestState': vm.guest.guestState,
                'ipAddress': vm.guest.ipAddress,
                'datacenter': kwargs['current_dc']
            }
            if vm.config.template:
                kwargs['template_list'].append(
                    {'name': vm.summary.config.name, 'instanceUuid': vm.summary.config.instanceUuid})
            redis_client.set('VM_%s' % vm.summary.config.name, json.dumps(vm_dict))
        # 当 clone 一台新的 VM, 并且还没 clone 完成时, 会导致这个报错
        # AttributeError: 'NoneType' object has no attribute 'template'
        except AttributeError as e:
            print(e)


    def create_vm_from_image(self, vm_name, image, datacenter, cluster, datastore, folder, port_group, vcpus, ram):

        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.pool = cluster.resourcePool

        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = False

        dvs_port_connection = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey = port_group.key
        dvs_port_connection.switchUuid = (
            port_group.config.distributedVirtualSwitch.uuid
        )

        nic = vim.vm.device.VirtualDeviceSpec()
        nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        nic.device = vim.vm.device.VirtualVmxnet3()
        nic.device.addressType = 'assigned'
        nic.device.key = 4000
        nic.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic.device.backing.port = dvs_port_connection
        nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic.device.connectable.startConnected = True
        nic.device.connectable.allowGuestControl = True

        vmconf = vim.vm.ConfigSpec()
        vmconf.numCPUs = vcpus
        vmconf.memoryMB = ram
        vmconf.deviceChange = [nic]

        enable_uuid_opt = vim.option.OptionValue()
        enable_uuid_opt.key = 'disk.enableUUID'  # Allow the guest to easily mount extra disks
        enable_uuid_opt.value = '1'
        vmconf.extraConfig = [enable_uuid_opt]

        clonespec.config = vmconf

        if folder is not None:
            task = image.Clone(folder=folder, name=vm_name, spec=clonespec)
        else:
            task = image.Clone(folder=datacenter.vmFolder, name=vm_name, spec=clonespec)

        return task

    def create_vm_from_template(self, vmware_client, redis_client, deploy_args):
        try:
            # Retrieve template object
            tp = deploy_args['template']
            tp_list = json.loads(redis_client.get('TEMPLATE'))
            for i in tp_list:
                if i['name'] == tp:
                    tp = i['instanceUuid']
            tp = self.get_vm_by_uuid(vmware_client, tp)
            # Retrieve Datacenter object
            dc = self.get_datacenter(vmware_client, deploy_args['datacenter'])
            # 针对开发环境的多环境支持
            if RUNNING_ENV == 'dev':
                ho = self.get_host(vmware_client, deploy_args['cluster'])
                cl_name = "Cluster01"
                cl = self.get_cluster(vmware_client, cl_name, dc)
            else:
                cl = self.get_cluster(vmware_client, deploy_args['cluster'], dc)
            ds = self.get_datastore(vmware_client, deploy_args['datastore'], dc)
            fo = dc.vmFolder
            vl = self.get_network(vmware_client, deploy_args['vlan'])
            reloSpec = vim.vm.RelocateSpec()
            reloSpec.datastore = ds
            reloSpec.folder = fo
            reloSpec.pool = cl.resourcePool
            confSpec = vim.vm.ConfigSpec()
            confSpec.cpuHotAddEnabled = True
            confSpec.memoryHotAddEnabled = True
            confSpec.numCPUs = deploy_args['cpu']
            confSpec.memoryMB = deploy_args['memory'] * 1024
            confSpec.name = deploy_args['servername']
            custSpec = vim.vm.customization.Specification()
            custSpec = vmware_client.content.customizationSpecManager.Get(deploy_args['custspec'])

            # IP 设置
            custSpec.spec.nicSettingMap[0].adapter.ip = vim.vm.customization.FixedIp()
            custSpec.spec.nicSettingMap[0].adapter.ip.ipAddress = deploy_args['ipaddress']
            custSpec.spec.nicSettingMap[0].adapter.subnetMask = deploy_args['netmask']
            custSpec.spec.nicSettingMap[0].adapter.gateway = deploy_args['gateway']
            # VLAN 设置
            specs = []
            for dev in tp.config.hardware.device:
                if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                    dev.backing.network = vl
                    dev.backing.deviceName = vl.name
                    dev.backing.useAutoDetect = True
                    dev.connectable.connected = True
                    dev.connectable.startConnected = True
                    spec = vim.vm.device.VirtualDeviceSpec()
                    spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                    spec.device = dev
                    specs.append(spec)
            confSpec.deviceChange = specs

            clonSpec = vim.vm.CloneSpec()
            clonSpec.location = reloSpec
            clonSpec.config = confSpec
            clonSpec.powerOn = True
            clonSpec.customization = custSpec.spec
        except Exception as e:
            return {'error': e}
        else:
            if deploy_args['mode'] == 'check':
                DeployLists.objects.filter(id=deploy_args['id']).update(state=2)
                return {'error': False}
            elif deploy_args['mode'] == 'run':
                task = tp.Clone(folder=fo, name=deploy_args['servername'], spec=clonSpec)
                msg = task.info.description.message if task.info.description else ""
                Tasks.objects.create(chain_id=task.info.eventChainId, key=task.info.key, user=task.info.reason.userName,
                                     queue_time=task.info.queueTime, state=task.info.state,
                                     progress=task.info.progress or 0, entity_name=task.info.entityName, type=1,
                                     msg=msg)
                DeployLists.objects.filter(id=deploy_args['id']).update(chain_id=task.info.eventChainId, state=3)
                self.wait_for_tasks_async(vmware_client, [task])
                return task

    def clone_and_template_vm(self, vm, datastore, folder):
        reloSpec = vim.vm.RelocateSpec()
        reloSpec.datastore = datastore
        # the vm template stays on the host
        # if the host is down any clone will fail

        if folder is not None:
            reloSpec.folder = folder

        # Configure the new vm to be super small because why not
        # We may want to remove it from the vswitch as well
        vmconf = vim.vm.ConfigSpec()
        vmconf.numCPUs = 1
        vmconf.memoryMB = 128
        vmconf.deviceChange = []

        # We don't want additional disks to be cloned with the VM so remove them
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label.startswith("Hard disk") \
                    and dev.deviceInfo.label.endswith("1") is False:
                virtual_disk_spec = vim.vm.device.VirtualDeviceSpec()
                virtual_disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                virtual_disk_spec.device = dev
                vmconf.deviceChange.append(virtual_disk_spec)

        # If the vm starts with a large disk there is no way to shrink it.
        # Hopefully it is thin provisioned...
        # We should be smart when we create instances that will be converted to images
        # they should have as small a disk as possible
        # storage is cheap but cloning is expensive

        clonespec = vim.vm.CloneSpec()
        clonespec.location = reloSpec
        clonespec.config = vmconf
        clonespec.powerOn = False
        clonespec.template = True

        file_name = "sandwich-" + str(uuid.uuid4())

        task = vm.Clone(folder=folder, name=file_name, spec=clonespec)
        return task, file_name

    def setup_serial_connection(self, vmware_client, vspc_address, vm):
        serial_device = None
        # Find the serial device
        for dev in vm.config.hardware.device:
            # Label may change if we add another port (i.e for logging)
            if isinstance(dev, vim.vm.device.VirtualSerialPort) and dev.deviceInfo.label == "Serial port 1":
                serial_device = dev
                break

        serial_device_spec = vim.vm.device.VirtualDeviceSpec()
        serial_device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit

        if serial_device is None:
            serial_device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            serial_device_spec.device = vim.vm.device.VirtualSerialPort()
        else:
            serial_device_spec.device = serial_device

        serial_device_spec.device.backing = vim.vm.device.VirtualSerialPort.URIBackingInfo()
        serial_device_spec.device.backing.serviceURI = 'sandwich'
        serial_device_spec.device.backing.direction = 'client'
        serial_device_spec.device.backing.proxyURI = vspc_address
        serial_device_spec.device.yieldOnPoll = True

        spec = vim.vm.ConfigSpec()
        spec.deviceChange = [serial_device_spec]
        task = vm.ReconfigVM_Task(spec=spec)
        self.wait_for_tasks(vmware_client, [task])

    def power_on_vm(self, vmware_client, vm):
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
            task = vm.PowerOn()
            self.wait_for_tasks(vmware_client, [task])

    def power_off_vm(self, vmware_client, vm, hard=False):
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            if hard is False:
                try:
                    vm.ShutdownGuest()
                except vim.fault.ToolsUnavailable:
                    # Guest tools was not running so hard power off instead
                    return self.power_off_vm(vmware_client, vm, hard=True)
                return
            task = vm.PowerOff()
            self.wait_for_tasks(vmware_client, [task])

    def delete_vm(self, vmware_client, vm):
        task = vm.Destroy()
        self.wait_for_tasks(vmware_client, [task])

    def delete_image(self, vmware_client, image):
        task = image.Destroy_Task()
        self.wait_for_tasks(vmware_client, [task])

    ########################
    #   Snapshot Actions   #
    ########################

    def get_snapshot(self, vmware_client, vm_uuid, snapshot_name):
        vm_obj = self.get_vm_by_uuid(vmware_client, vm_uuid)
        snapshot_obj = vm_obj.snapshot.rootSnapshotList
        snap_obj = self.__get_snapshot_loop(snapshot_obj, snapshot_name)
        return snap_obj

    def __get_snapshot_loop(self, snapshots, snapname):
        snap_obj = []
        for snapshot in snapshots:
            if snapshot.name == snapname:
                snap_obj.append(snapshot)
            else:
                snap_obj = snap_obj + self.__get_snapshot_loop(snapshot.childSnapshotList, snapname)
        return snap_obj

    def get_snapshot_list(self, vmware_client, vm_uuid):
        vm_obj = self.get_vm_by_uuid(vmware_client, vm_uuid)
        snapshot_obj = vm_obj.snapshot.rootSnapshotList
        snapshot_data = self.__get_snapshot_list_loop(snapshot_obj)
        return snapshot_data

    def __get_snapshot_list_loop(self, snapshots):
        snapshot_data = []
        snap_text = ""
        for snapshot in snapshots:
            snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (snapshot.name, snapshot.description,
                                                                                  snapshot.createTime, snapshot.state)
            snapshot_data.append(snap_text)
            snapshot_data = snapshot_data + self.__get_snapshot_list_loop(snapshot.childSnapshotList)
        return snapshot_data

    def create_snapshot(self, vmware_client, vm_obj, snap_dict):
        task = vm_obj.CreateSnapshot(snap_dict['snapshot_name'], snap_dict['description'], snap_dict['snapshot_mem'],
                                         snap_dict['snapshot_qui'])
        msg = task.info.description.message if task.info.description else ""
        Tasks.objects.create(chain_id=task.info.eventChainId, key=task.info.key, user=task.info.reason.userName,
                                   queue_time=task.info.queueTime, state=task.info.state, progress=task.info.progress,
                                   entity_name=task.info.entityName, type=0, msg=msg)
        self.wait_for_tasks_async(vmware_client, [task])
        return task

    def delete_snapshot(self, snapshot_obj):
        return snapshot_obj.RemoveSnapshot_Task(True)

    ########################
    #     Regular Task     #
    ########################

    def __scan_dc(self, vim_obj, folder_dict, cluster_dict, datastore_dict, network_dict, template_list, redis_client,
                  full_scan, current_dc):
        print("Current DC: %s" % current_dc)
        if hasattr(vim_obj, 'childEntity'):
            for child in vim_obj.childEntity:
                if isinstance(child, vim.Datacenter):
                    folder_dict[child.name] = {}
                    cluster_dict[child.name] = {}
                    datastore_dict[child.name] = {}
                    network_dict[child.name] = {}
                    self.__scan_dc(child, folder_dict[child.name], cluster_dict[child.name], datastore_dict[child.name],
                                   network_dict[child.name], template_list, redis_client, full_scan,
                                   current_dc + child.name + "/vm/")
                elif isinstance(child, vim.Folder):
                    folder_dict[child.name] = {}
                    self.__scan_dc(child, folder_dict[child.name], cluster_dict, datastore_dict, network_dict,
                                   template_list, redis_client, full_scan, current_dc + child.name + "/")
                elif isinstance(child, vim.VirtualMachine):
                    folder_dict[child.name] = 'vm'
                    if full_scan:
                        self.get_vm_info(child, redis_client, template_list=template_list, current_dc=current_dc)
                elif isinstance(child, vim.ClusterComputeResource):
                    cluster_dict[child.name] = {}
                    self.__scan_dc(child, folder_dict, cluster_dict[child.name],
                                   datastore_dict, network_dict, template_list, redis_client, full_scan, current_dc)
        if hasattr(vim_obj, 'vmFolder'):
            self.__scan_dc(vim_obj.vmFolder, folder_dict, cluster_dict, datastore_dict, network_dict, template_list,
                           redis_client, full_scan, current_dc)
        if hasattr(vim_obj, 'hostFolder'):
            self.__scan_dc(vim_obj.hostFolder, folder_dict, cluster_dict, datastore_dict, network_dict, template_list,
                           redis_client, full_scan, current_dc)
        if hasattr(vim_obj, 'host'):
            for child in vim_obj.host:
                if isinstance(child, vim.HostSystem):
                    cluster_dict[child.name] = 'host'
        if hasattr(vim_obj, 'datastore'):
            for child in vim_obj.datastore:
                if isinstance(child, vim.Datastore):
                    datastore_dict[child.name] = [child.summary.freeSpace, child.summary.capacity]
        if hasattr(vim_obj, 'network'):
            for child in vim_obj.network:
                if isinstance(child, vim.Network):
                    network_dict[child.name] = 'nw'

    def __scan_custspec(self, vmware_client, result):
        for item in vmware_client.content.customizationSpecManager.info:
            if isinstance(item, vim.CustomizationSpecInfo):
                result.append(item.name)

    def task_scan_dc(self, vmware_client, redis_client, full_scan=False):
        folder = {}
        cluster = {}
        datastore = {}
        network = {}
        template = []
        self.__scan_dc(vmware_client.content.rootFolder, folder, cluster, datastore, network, template, redis_client,
                       full_scan, "/")
        redis_client.set('FOLDER_ARCH', json.dumps(folder))
        redis_client.set('CLUSTER_ARCH', json.dumps(cluster))
        redis_client.set('DATASTORE_ARCH', json.dumps(datastore))
        redis_client.set('VLAN_ARCH', json.dumps(network))
        if full_scan:
            redis_client.set('TEMPLATE', json.dumps(template))
        custspec = []
        self.__scan_custspec(vmware_client, custspec)
        redis_client.set('CUSTSPEC_ARCH', json.dumps(custspec))
