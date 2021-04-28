let sudoListObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#tb_sudo_list",
    data: {
        selectedIdList: "",
        tableData: "",
        columns: [
            { data: 'id' },
            { data: 'ticket' },
            { data: 'hosts' },
            { data: 'users' },
            { data: 'status' },
            { data: 'time_created' },
            { data: 'effective_days' },
            { data: 'operator' },
        ],
        buttons: [
            {
                text: "Add",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_add_sudo'
                },
            },
            {
                text: "Delete",
                action: function (){
                    sudoListObj.deleteSudo()
                }
            },
            'selectAll',
            'selectNone',
            'excelHtml5'
        ]
    },
    methods: {
        drawTable: function () {
            $('#tb_sudo_list').DataTable({
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
        deleteSudo: function (){
            this.selectedIdList = [];
            let dt = $('#tb_sudo_list').DataTable();
            let rowSelected = dt.rows({selected: true}).data();
            for ( let i = 0; i < rowSelected.length; i++){
                this.selectedIdList.push(rowSelected[i].id)
            }
            let params = new URLSearchParams();
            params.append("task_id", this.selectedIdList);
            params.append('action', 'delete')
            axios({
                method: 'post',
                url: '/security/tempsudo/task/',
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

let addSudoObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#modal_add_sudo",
    data: {
        users: "",
        hosts: "",
        ticket: "",
        effective_days: 3,
    },
    methods: {
        submitTask: function () {
            let params = new URLSearchParams();
            params.append("users", this.users);
            params.append("hosts", this.hosts);
            params.append('ticket', this.ticket);
            params.append("effective_days", this.effective_days);
            params.append('action', 'add');
            if (params.get("hosts").length === 0 ||
                params.get("users").length === 0) {
                PNotify.alert({
                    title: "Task Submit Error!",
                    text: "Please check the items you filled in!"
                });
            } else {
                axios({
                    method: "post",
                    url: "/security/tempsudo/task/",
                    headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                    data: params
                }).then(function (response) {
                    if (response['data']['code'] === 200) {
                        PNotify.info({
                            title: "Success!",
                            text: "Deploy Task Submitted!"
                        });
                        $("#add_sudo_reset").trigger('click');
                    }
                })
            }
        },
    }
})

$(document).ready(function () {
    getSudoListObjTableData();
    // setInterval(getSudoListObjTableData, 300000);
})

function getSudoListObjTableData() {
    $("#loaderIcon").removeAttr("hidden");
    axios.get('/security/tempsudo/task/').then(function (response) {
        sudoListObj.tableData = response['data']['data']
        sudoListObj.drawTable();
        $("#loaderIcon").attr("hidden", 'true');
    })
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}