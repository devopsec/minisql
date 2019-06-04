/* define modal dynamic modal handling functions (needed for redraws) */
function handleOpenUpdateModal(e) {
    var modal_body = $('#edit .modal-body');
    var row_index = $(e.target).closest('tr').index();
    var fields = modal_body.find("input[name^='field']");
    var table_fields = $('#dataTable > tbody > tr:eq(' + row_index + ') td:not(:nth-last-child(-n+2))');
    var self = null;
    for (var i = 0; i < fields.length; i++) {
        self = $(fields[i]);
        self.val($(table_fields[i]).text());
        if (self.attr('type') === 'checkbox') {
            if (self.val() == 1) {
                self.prop('checked', true);
            }
            else {
                self.prop('checked', false);
            }
        }
    }
    
    var id = $('#dataTable > tbody > tr:eq(' + row_index + ') td:eq(0)').text();
    var id_field = modal_body.find("input[name='row_id']").get(0);
    $(id_field).val(id);
}

function handleOpenDeleteModal(e) {
    var modal_body = $('#delete .modal-body');
    var row_index = $(e.target).closest('tr').index();
    var id = $('#dataTable > tbody > tr:eq(' + row_index + ') td:eq(0)').text();
    var id_field = modal_body.find("input[name='row_id']").get(0);
    $(id_field).val(id);
}


/* any handlers depending on DOM elems go here */
$(document).ready(function() {
    /* init datatable */
    var table = $('#dataTable').DataTable({
        "lengthChange": true,
        "ordering": true,
        "paging": true,
        "searching": true,
        "responsive": true,
        "columnDefs": [
            { "orderable": false, "targets": [0] }
        ],
        "order": [[ 1, 'asc' ]],
        "dom": '<"wrapper-horizontal edge-centered filter-header"lfr><t><"wrapper-horizontal edge-centered filter-footer"ip>',
        /* update event listeners */
        fnDrawCallback: function() {
            $('.open-Update').click(handleOpenUpdateModal);
            $('.open-Delete').click(handleOpenDeleteModal);
        }
    });
    /* show inital table */
    table.draw();

    /* handle clearing and updating modal data */
    $('#open-Add').click(function() {
        /* Clear out the modal */
        var modal_body = $('#add .modal-body');
        var fields = modal_body.find("input[name^='field']");
        fields.each(function() {
            $(this).val('');
        });
    });
    
    /* these would be known and updated automatically in the real world */
    $('#add, #edit').find('form').submit(function(e) {
        var form = $(e.target);
        var fields = form.find("input[name^='field']");
        
        /* add value to checkboxes */
        var self = null;
        fields.each(function() {
            self = $(this);
            
            if (self.attr('type') === 'checkbox') {
                if (self.get(0).checked) {
                    self.val(1);
                } else {
                    self.val(0);
                }
            }
        });
        
        /* update column names for edit form */
        if ($(this).parent().parent().parent().parent().attr('id') === 'edit') {
            var table_columns = fields.map(function (i, elem) {
                return elem.className.replace('form-control','').trim();
            }).get();
            form.find('input[name="column_names"]').val(table_columns);
        }
        
        /* for demo just set them to 1 */
        var matches = [];
        var id_class_name = "";
        fields.each(function() {
            matches = this.className.match(/[\w]+_id|approved/g);
            if (matches != null) {
                id_class_name = matches[0];
                if (['approved','address_id', 'customer_id', 'agent_id', 'policy_id', 'premium_id', 'insurance_company_id'].indexOf(id_class_name) >= 0) {
                    $(this).val(1);
                }
            }
        });
        
        return true;
    });
});
