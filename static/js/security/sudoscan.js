let sudoScanListObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#tb_sudo_scan_list",
    data: {
        selectedId: "",
        tableData: "",
        columns: [
            {data: 'task_id'},
            {data: 'time_created'},
            {data: 'operator'},
            {data: 'status'}
        ],
        buttons: [
            {
                text: "Add",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_add_sudo_scan'
                },
            },
            {
                text: "View",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_view_result'
                },
                action: function () {
                    sudoScanListObj.viewResult()
                }
            },
            'selectNone',
            'excelHtml5'
        ]
    },
    methods: {
        drawTable: function () {
            $('#tb_sudo_scan_list').DataTable({
                dom: 'Bfrtip',
                data: this.tableData,
                columns: this.columns,
                autoWidth: true,
                processing: true,
                lengthMenu: [50],
                order: [[0, 'desc']],
                buttons: this.buttons,
                select: true
            })
        },
        viewResult: function () {
            tb = $('#tb_view_result');
            tb.DataTable().destroy();
            this.selectedId = "";
            let dt = $('#tb_sudo_scan_list').DataTable();
            let rowSelected = dt.rows({selected: true}).data();
            if (typeof rowSelected[0] == "undefined" || rowSelected[0] == null){
                PNotify.error({
                    title: 'Error!',
                    text: "Please select one line to view!"
                });
                return;
            }
            this.selectedId = rowSelected[0].task_id;
            tb.DataTable({
                dom: 'Bfrtip',
                columns: [
                    {'data': 'hostname'},
                    {'data': 'user'},
                    {'data': 'user_type'},
                    {'data': 'src_host'},
                    {'data': 'run_as'},
                    {'data': 'commands'}
                ],
                autoWidth: true,
                processing: true,
                lengthMenu: [50],
                order: [[0, 'desc']],
                buttons: [
                    'excelHtml5'
                ],
                select: false,
                ajax: {
                    url: "/api/security/sudoscan/" + this.selectedId,
                    cache: true
                }
            })
        },
    }
})

let sudoScanFormObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#modal_add_sudo_scan",
    data: {
        host_list: ""
    },
    methods: {
        submitTask: function () {
            let params = new URLSearchParams();
            params.append("host_list", this.host_list);
            if (params.get('host_list').length === 0) {
                PNotify.alert({
                    title: "Task Submit Error!",
                    text: "Please check the hosts you filled in!"
                });
            } else {
                axios({
                    method: "post",
                    url: "/api/security/sudoscan/",
                    headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                    data: params
                }).then(function (response) {
                    if (response['data']['code'] === 200) {
                        PNotify.info({
                            title: "Success!",
                            text: "Scan Task Submitted!"
                        });
                        $("#add_sudo_scan_reset").trigger('click');
                    }
                })
            }
        }
    }
})

$(document).ready(function () {
    getSudoScanListObjTableData();
    // setInterval(getSudoListObjTableData, 300000);
})

function getSudoScanListObjTableData() {
    $("#loaderIcon").removeAttr("hidden");
    axios.get('/api/security/sudoscan/').then(function (response) {
        sudoScanListObj.tableData = response['data']['data']
        sudoScanListObj.drawTable();
        $("#loaderIcon").attr("hidden", 'true');
    })
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}