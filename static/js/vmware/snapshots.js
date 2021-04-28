let snapshotListObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#tb_snapshot_list",
    data: {
        tableData: "",
        selectedIdList: "",
        columns: [
            { data: 'id' },
            { data: 'vm_name' },
            { data: 'vm_vc' },
            { data: 'vm_path' },
            { data: 'time_created' },
            { data: 'keep_days' },
            { data: 'snap_name' },
            { data: 'snap_desc' },
            { data: 'operator' },
            { data: 'state' },
        ],
        buttons: [
            {
                text: "Create Snapshot",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_create_snapshots',
                }
            },
            // {
            //     text: "Delete Logs",
            //     action: function (){
            //         deployListObj.deleteTasks()
            //     }
            // },
            'selectAll',
            'selectNone',
            'excelHtml5'
        ]
    },
    methods: {
        drawTable: function (){
            $('#tb_snapshot_list').DataTable({
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
        deleteRecord: function (){
            this.selectedIdList = [];
            let dt = $('#tb_snapshot_list').DataTable();
            let rowSelected = dt.rows({selected: true}).data();
            for ( let i = 0; i < rowSelected.length; i++ ){
                this.selectedIdList.push(rowSelected[i].id)
            }
            let params = new URLSearchParams();
            params.append("task_id", this.selectedIdList);
            axios({
                method: 'post',
                url: '/api/vmware/tasks/',
                headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                data: params
            }).then(function (response) {
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
        }
    },
})

let createSnapshotObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#modal_create_snapshots",
    data: {
        vcList: [],
        vcSelected: "",
        hostname: "",
        snapshotName: "",
        description: "",
        snapMemory: false,
        quiesceFS: false,
        removeChild: false,
        consolidate: false,
        keepDays: 5
    },
    methods: {
        submitTask: function () {
            let params = new URLSearchParams();
            params.append("vm_vc", this.vcSelected);
            params.append("vm_name_list", this.hostname);
            params.append("snap_name", this.snapshotName);
            params.append("snap_desc", this.description);
            params.append("snap_mem", this.snapMemory);
            params.append("snap_qui", this.quiesceFS);
            params.append("snap_remove_child", this.removeChild);
            params.append("snap_sol", this.consolidate);
            params.append("keep_days", this.keepDays);
            if (params.get("vm_name_list").length === 0 ||
                params.get("vm_vc").length === 0) {
                PNotify.alert({
                    title: "Task Submit Error!",
                    text: "Please check the items you filled in!"
                });
            } else {
                PNotify.info({
                    title: "Submitting...",
                    text: "Submitting Snapshot Tasks...",
                    delay: 2000,
                })
                axios({
                    method: "post",
                    url: "/api/vmware/snapshots/",
                    headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                    data: params
                }).then(function (response) {
                    if (response['data']['code'] === 200) {
                        PNotify.info({
                            title: "Success!",
                            text: "Snapshot Task Submitted!"
                        });
                        $("#create_snapshots_reset").trigger('click');
                    }
                })
            }
        },
    }
})

$(document).ready(function () {
    getSnapshotListObjTableData();
    // setInterval(getSnapshotListObjTableData, 300000);
})

function getSnapshotListObjTableData() {
    $("#loaderIcon").removeAttr("hidden");
    axios.get('/api/vmware/snapshots/').then(function (response) {
        snapshotListObj.tableData = response['data']['data'];
        snapshotListObj.drawTable();
        $("#loaderIcon").attr("hidden", 'true');
    })
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}