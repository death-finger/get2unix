let deployListObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#tb_deploy_list",
    data: {
        selectedIdList: "",
        tableData: "",
        columns: [
            { data: 'id' },
            { data: 'template' },
            { data: 'servername' },
            { data: 'vcenter' },
            { data: 'datacenter' },
            { data: 'cluster' },
            { data: 'datastore' },
            { data: 'custspec' },
            { data: 'vlan' },
            { data: 'ipaddress' },
            { data: 'netmask' },
            { data: 'gateway' },
            { data: 'cpu' },
            { data: 'memory' },
            { data: 'state' },
        ],
        buttons: [
            {
                text: "Create VM",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_vm_deploy',
                }
            },
            {
                text: "Copy Selected",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_vm_deploy',
                },
                action: async function (){
                    dt = $("#tb_deploy_list").DataTable();
                    rowSelected = dt.row({selected: true}).data();
                    deployFormObj.vcSelected = rowSelected.vcenter;
                    await deployFormObj.getList(deployFormObj.vcSelected, "template", deployFormObj.deployId);
                    deployFormObj.tpSelected = rowSelected.template;
                    await deployFormObj.getList(deployFormObj.tpSelected, "datacenter", deployFormObj.deployId);
                    deployFormObj.dcSelected = rowSelected.datacenter;
                    await deployFormObj.getList(deployFormObj.dcSelected, 'cluster', deployFormObj.deployId);
                    deployFormObj.clSelected = rowSelected.cluster;
                    await deployFormObj.getList(deployFormObj.clSelected, 'datastore', deployFormObj.deployId);
                    deployFormObj.dsSelected = rowSelected.datastore;
                    await deployFormObj.getList(deployFormObj.dsSelected, 'custspec', deployFormObj.deployId);
                    deployFormObj.csSelected = rowSelected.custspec;
                    await deployFormObj.getList(deployFormObj.csSelected, 'vlan', deployFormObj.deployId);
                    deployFormObj.vlSelected = rowSelected.vlan;
                }
            },
            {
                text: "Run Tasks",
                action: function (){
                    deployListObj.runTasks()
                }
            },
            {
                text: "Delete Logs",
                action: function (){
                    deployListObj.deleteTasks()
                }
            },
            'selectAll',
            'selectNone',
            'excelHtml5'
        ]
    },
    methods: {
        drawTable: function (){
            $("#tb_deploy_list").DataTable({
                dom: 'Bfrtip',
                data: this.tableData,
                columns: this.columns,
                autoWidth: true,
                processing: true,
                lengthMenu: [50],
                order: [[0, 'desc']],
                buttons: this.buttons,
                select: true,
            })
        },
        submitTasks: function (submitType){
            this.selectedIdList = [];
            let dt = $("#tb_deploy_list").DataTable();
            let rowSelected = dt.rows({selected: true}).data();
            for ( let i = 0; i < rowSelected.length; i++ ){
                this.selectedIdList.push(rowSelected[i].id)
            }
            let params = new URLSearchParams();
            params.append("deploy_id", this.selectedIdList);
            if (submitType === 'delete'){
                params.append("delete", "true");
            } else {
                params.append("run", "true");
            }
            PNotify.info({
                title: "Submitting...",
                text: "Submitting Deploy Tasks...",
                delay: 2000
            })
            axios({
                method: 'post',
                url: '/api/vmware/deploy/action/',
                headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                data: params
            }).then(function (response) {
                console.log(response);
                if (response['data']['code'] === 200) {
                    PNotify.info({
                        title: 'Success',
                        text: "Submitted Successfully!"
                    })
                } else {
                    PNotify.error({
                        title: 'Failed!',
                        text: response['data']["msg"]
                    })
                }
            })
        },
        deleteTasks: function () {
            this.submitTasks('delete')
        },
        runTasks: function () {
            this.submitTasks('run')
        },
    }
})

let deployFormObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#modal_vm_deploy",
    data: {
        deployId: "",
        servername: "",
        vcList: [],
        vcSelected: "",
        tpList: [],
        tpSelected: "",
        dcList: [],
        dcSelected: "",
        clList: [],
        clSelected: "",
        dsList: [],
        dsSelected: "",
        csList: [],
        csSelected: "",
        vlList: [],
        vlSelected: "",
        ip: "",
        mask: "",
        gateway: "",
        cpu: "",
        memory: "",
        currentSelectedId: "",
    },
    methods: {
        getList: async function (current_name, query_type, deploy_id) {
            let params = new URLSearchParams();
            params.append('current_name', current_name);
            params.append('query_type', query_type);
            params.append('deploy_id', deploy_id);
            await axios({
                method: 'post',
                url: '/api/vmware/getopts/',
                headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                data: params
            }).then(function (response) {
                if (response['data']['code'] === 200) {
                    ret = response['data']['data']['result'];
                    this.deployId = response['data']['data']['deploy_id'];
                    switch (query_type) {
                        case "template":
                            Vue.set(deployFormObj, 'tpList', ret);
                            Vue.set(deployFormObj, 'deployId', response['data']['data']['deploy_id'])
                            break;
                        case "datacenter":
                            Vue.set(deployFormObj, 'dcList', ret);
                            break;
                        case "cluster":
                            Vue.set(deployFormObj, 'clList', ret);
                            break;
                        case "datastore":
                            Vue.set(deployFormObj, 'dsList', ret);
                            break;
                        case "custspec":
                            Vue.set(deployFormObj, 'csList', ret);
                            break;
                        case "vlan":
                            Vue.set(deployFormObj, 'vlList', ret);
                            break;
                    }
                }
            })
        },
        submitTask: function () {
            let params = new URLSearchParams();
            params.append('template', this.tpSelected);
            params.append('servername', this.servername);
            params.append('vcenter', this.vcSelected);
            params.append('datacenter', this.dcSelected);
            params.append('cluster', this.clSelected);
            params.append('datastore', this.dsSelected);
            params.append('custspec', this.csSelected);
            params.append('ipaddress', this.ip);
            params.append('netmask', this.mask);
            params.append('gateway', this.gateway);
            params.append('cpu', this.cpu);
            params.append('memory', this.memory);
            params.append('state', "0");
            params.append('deploy_id', this.deployId);
            params.append('vlan', this.vlSelected);
            if (params.get('template').length === 0 ||
                params.get('servername').length === 0 ||
                params.get('vcenter').length === 0 ||
                params.get('datacenter').length === 0 ||
                params.get("cluster").length === 0 ||
                params.get("datastore").length === 0 ||
                params.get('custspec').length === 0) {
                PNotify.alert({
                    title: "Task Submit Error!",
                    text: "Please check the items you filled in!"
                });
            } else {
                this.submitDisabled = false;
                axios({
                    method: 'post',
                    url: '/api/vmware/deploy/',
                    headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                    data: params
                }).then(function (response) {
                    if (response['data']['code'] === 200) {
                        PNotify.info({
                            title: "Success!",
                            text: "Deploy Task Submitted!"
                        });
                        deployFormObj.resetForm();
                    }
                })
            }
        },
        resetForm: function (){
            this.deployId = '';
            this.servername = '';
            this.vcList = [];
            this.vcSelected = "";
            this.tpList = "";
            this.tpSelected = "";
            this.dcList = [];
            this.dcSelected = "";
            this.clList = [];
            this.clSelected = "";
            this.dsList = [];
            this.dsSelected = "";
            this.csList = [];
            this.csSelected = "";
            this.vlList = [];
            this.vlSelected = "";
            this.ip = "";
            this.mask = "";
            this.gateway = "";
            this.cpu = "";
            this.memory = "";
            $("#deploy_form_reset").trigger('click');
        }
    },
    watch: {
        vcSelected: function () {
            this.getList(this.vcSelected, "template", this.deployId)
        },
        tpSelected: function () {
            this.getList(this.tpSelected, "datacenter", this.deployId)
        },
        dcSelected: function () {
            this.getList(this.dcSelected, "cluster", this.deployId)
        },
        clSelected: function () {
            this.getList(this.clSelected, 'datastore', this.deployId)
        },
        dsSelected: function () {
            this.getList(this.dsSelected, 'custspec', this.deployId)
        },
        csSelected: function () {
            this.getList(this.csSelected, 'vlan', this.deployId)
        }
    }
})

$(document).ready(function () {
    getDeployListObjTableData();
    // setInterval(getDeployListObjTableData, 10000);
})

function getDeployListObjTableData() {
    $("#loaderIcon").removeAttr("hidden");
    axios.get('/api/vmware/deploy/').then(function (response) {
        deployListObj.tableData = response['data']['data'];
        deployListObj.drawTable();
        $("#loaderIcon").attr("hidden", 'true');
    })
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}