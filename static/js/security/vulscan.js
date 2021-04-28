let vulScanListObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#tb_vulscan_list",
    data: {
        selectedId: "",
        tableData: "",
        columns: [
            {data: 'id'},
            {data: 'server_name'},
            {data: 'family'},
            {data: 'release'},
            {data: 'scan_date'}
        ],
        buttons: [
            {
                text: "Add",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_add_vulscan'
                },
            },
            {
                text: "View",
                attr: {
                    'data-bs-toggle': 'modal',
                    'data-bs-target': '#modal_view_report'
                },
                action: function () {
                    vulScanListObj.viewReport()
                }
            },
            'selectNone',
            'excelHtml5',
            {
                text: "VulsRepo",
                action: function (){
                    window.open('http://htpc:5111');
                }

            }
        ]
    },
    methods: {
        drawTable: function () {
            $('#tb_vulscan_list').DataTable({
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
        viewReport: function () {
            tb = $('#tb_view_report');
            tb.DataTable().destroy();
            this.selectedId = "";
            let dt = $('#tb_vulscan_list').DataTable();
            let rowSelected = dt.rows({selected: true}).data();
            if (typeof rowSelected[0] == "undefined" || rowSelected[0] == null) {
                PNotify.error({
                    title: 'Error!',
                    text: "Please select one line to view!"
                });
                return;
            }
            this.selectedId = rowSelected[0].id;
            tb.DataTable({
                dom: 'Bfrtip',
                columns: [
                    {
                        'class': 'details-control',
                        'orderable': false,
                        'data': null,
                        'defaultContent': ''
                    },
                    {'data': 'cve_id'},
                    {'data': 'status'},
                    {'data': 'details'},
                    {'data': 'next_check_date'},
                ],
                autoWidth: true,
                processing: true,
                lengthMenu: [50],
                order: [[2, 'desc']],
                buttons: [
                    'excelHtml5'
                ],
                select: false,
                ajax: {
                    url: "/api/security/vulscan/details/" + this.selectedId,
                    cache: true
                }
            });
            $('#tb_view_report tbody').on('click', 'td.details-control', function () {
                let table = $('#tb_view_report').DataTable();
                let tr = $(this).closest('tr');
                let row = table.row(tr);
                if (row.child.isShown()) {
                    $('div.slider', row.child()).slideUp(function () {
                        row.child.hide();
                        tr.remove('shown');
                    });
                } else {
                    row.child(formatRow(row.data()), 'no-padding').show();
                    tr.addClass('shown');
                    $('div.slider', row.child()).slideDown();
                }
            });
        },
    }
})

let vulScanFormObj = new Vue({
    delimiters: ['[{', '}]'],
    el: "#modal_add_vulscan",
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
                    url: "/api/security/vulscan/",
                    headers: {'X-CSRFToken': getCookie('csrftoken', document.cookie)},
                    data: params
                }).then(function (response) {
                    if (response['data']['code'] === 200) {
                        window.alert('Please create the config file with provided content and run' +
                            'vulsctl manually!');
                        PNotify.notice({
                            title: "config.toml generated!",
                            text: response['data']['data'],
                            maxTextHeight: '600px',
                            minHeight: '200px',
                            hide: false,
                            sticker: true,
                        });
                        $("#add_vulscan_reset").trigger('click');
                    }
                })
            }
        }
    }
})


$(document).ready(function () {
    getVulScanListObjTableData();
    $("#modal_view_report .btn-close").click(function (){
        location.reload();
    })
})

function getVulScanListObjTableData() {
    $("#loaderIcon").removeAttr("hidden");
    axios.get('/api/security/vulscan/').then(function (response) {
        vulScanListObj.tableData = response['data']['data']
        vulScanListObj.drawTable();
        $("#loaderIcon").attr("hidden", 'true');
    })
}

function getCookie(name, token) {
    let value = '; ' + token
    let parts = value.split('; ' + name + '=')
    if (parts.length === 2) return parts.pop().split(';').shift()
}

function formatRow(d) {
    console.log(d);
    let thHtml = '<thead><tr><th>Package</th><th>Fix State</th><th>Fixed In</th></tr></thead>'
    let trHtml = ''

    for (let i=0;i<d.affected_packages.length;i++){
        trHtml += '<tr><td>' + d.affected_packages[i].name + '</td>' +
            '<td>' + d.affected_packages[i].fixState + '</td>' +
            '<td>' + d.affected_packages[i].fixedIn + '</td></tr>'
    }

    return '<div class="slider"><table width="80%">' + thHtml + trHtml + '</table></div>';
}

function destoryTable(){
    console.log("Destory Table");
    tb = $('#tb_view_report');
    tb.DataTable().destroy();
}
