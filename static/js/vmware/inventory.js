let vmInventoryObj = new Vue({
    delimiter: ['[{', '}]'],
    el: '#tb_vm_inventory',
    data: {
        selectedIdList: "",
        tableData: "",
        columns: [
            { data: 'hostname' },
            { data: 'vc' },
            { data: 'guest' },
            { data: 'state' },
            { data: 'cpu' },
            { data: 'memory' },
            { data: 'ip' },
            { data: 'path' },
        ],
        buttons: [
            'selectAll',
            'selectNone',
            'copy',
            'excelHtml5',
        ]
    },
    methods: {
        drawTable: function (){
            $('#tb_vm_inventory').DataTable({
                dom: 'Bfrtip',
                data: this.tableData,
                columns: this.columns,
                autoWidth: true,
                processing: true,
                lengthMenu: [50],
                buttons: this.buttons,
                select: true
            })
        }
    }
})

$(document).ready(function () {
    getVmInventoryObjTableData();
    // setInterval(getDeployListObjTableData, 10000);
})

function getVmInventoryObjTableData() {
    $("#loaderIcon").removeAttr('hidden');
    axios.get('/api/vmware/inventory/').then(function (response) {
        vmInventoryObj.tableData = response['data']['data'];
        vmInventoryObj.drawTable();
        $("#loaderIcon").attr("hidden", 'true')
    });
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}