$('#load_more_pending').click(function (event){
    event.preventDefault();
    var self = $(this),
        url = self.attr("action"),
        ajax_req = $.ajax({
            url: url,
            type: "GET",
            data: {
                load_more_pending: 'True'
            },
            success: function(data, textStatus, jqXHR){
                var html_output = '';
                $.each(data['pending'], function(key, value){
                    html_output += '<tr><td>' + value['item_name'] + '</td><td>';
                    if(is_admin=='True')
                        html_output += '<a href="' + provision_item_url + value['provision_id'] + '">Provision Item</a>';
                    else
                        html_output += value['description'];

                    html_output += '</td></tr>';
                });
                $('#pending_table').append(html_output);
                self.remove();
            }
        });
})

$('#load_more_approved').click(function (event){
    event.preventDefault();
    var self = $(this),
        url = self.attr("action"),
        ajax_req = $.ajax({
            url: url,
            type: "GET",
            data: {
                load_more_approved: 'True'
            },
            success: function(data, textStatus, jqXHR){
                var html_output = '';
                $.each(data['approved'], function(key, value){
                    html_output += '<tr><td>' + value['item_name'] + '</td><td>' + value['description'] + '</td><td>';
                    html_output += value['returnable'] + '</td><td>' + value['return_by'] + '</td>';

                    if(is_admin=='True'){
                        html_output += '<td>' + value['user_email'] + '</td>';
                        html_output += '<td>' + value['returned'] + '</td>';
                        if(value['returned'] == 'N/A')
                            html_output += '<td>N/A</td>';
                        else
                            html_output += '<td><a href="' + provision_list_url + value['provision_id'] +'">Mark Returned</a></td>';
                    }
                });
                $('#approved_table').append(html_output);
                self.remove();
            }
        });
})