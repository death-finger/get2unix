let userGroupsListObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "tb_usergroups_list",
    data: {
        selectedIdList: "",
        tableData: "",
        columns: [
            {data: 'id'},
            {data: 'group_name'},
            {data: 'user_list'},
        ],
        buttons: [
            {
                text: "Add",
                attr: {
                    'data-toggle': 'modal',
                    'data-target': '#modal_add_sudo'
                },
            },
            {
                text: "Delete",
                action: function () {
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
            $('#tb_usergroups_list').DataTable({
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
        }
    }
})

$(document).ready(function () {
    console.log('Before getUserGroupsListObjTableData()')
    getUserGroupsListObjTableData();
    console.log('After getUserGroupsListObjTableData')
})

function getUserGroupsListObjTableData() {
    axios.get('/security/permsudo/list/').then(function (response) {
        userGroupsListObj.tableData = response['data']['data']
        console.log(response['data'])
        userGroupsListObj.drawTable()
    })
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}