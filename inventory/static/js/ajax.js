$('#load_more_pending').click(function (event){
    event.preventDefault();
    var self = $(this),
        url = self.attr("action"),
        ajax_req = $.ajax({
            url: url,
            type: "GET",
            data: {
                load_more_pending: 'True',
                is_admin: is_admin
            },
            success: function(data, textStatus, jqXHR){
                var html_output = '';
                $.each(data['pending'], function(key, value){
                    html_output += '<tr><td>' + value['item_name'] + '</td>';
                    html_output += '<td>' + value['description'] + '</td>';
                    html_output += '<td>' + value['timestamp'] + '</td>';
                    if(is_admin=='True'){
                        html_output += '<td>' + value['user_email'] + '</td>';
                        html_output += '<td><a href="' + provision_item_url + value['provision_id'] + '">Provision Item</a></td>';
                    }

                    html_output += '</tr>';
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
                load_more_approved: 'True',
                is_admin: is_admin
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

$('#profile_update_form :input[type=file]').change(function(event){
    var self = $(this),
        image = self[0].files[0],
        arr = image.name.split('.'),
        ext = arr[arr.length - 1].toLowerCase(),
        imagedata = new FormData();

    var error_list = self.siblings('.errorlist');

    imagedata.append('image', image);
    imagedata.append('csrfmiddlewaretoken', csrf);

    if(ext=='jpg' || ext=='jpeg' || ext=='png'){
        var ajax_req = $.ajax({
                url:self.parent().attr("action"),
                cache: false,
                contentType: false,
                processData: false,
                type: "POST",
                data: imagedata,

                success: function(data, textStatus, jqXHR){
                    if(data['success'] == 'True'){
                        error_list.remove();
                        $('#profile_image').attr('src', data['image']);
                    }
                    else{
                        error_list.remove();
                        var error_list_new = '<ul class="errorlist"><li>' + data['error'] + '</li></ul>';
                        self.parent().append(error_list_new);
                    }
                }
            })
    }
    else{
        error_list.remove();
        var error_list_new = '<ul class="errorlist"><li>Select a valid image. The file you selected was either not an image or a corrupted image.</li></ul>';
        self.parent().append(error_list_new);
    }
})

$('#image_clear').click(function(event){
    event.preventDefault();
    var img_url = $('#profile_image').attr('src');
    if(img_url != ''){
        var self = $(this),
        formData = new FormData();

        formData.append('clear_image', 'True');
        formData.append('csrfmiddlewaretoken', csrf);

        $.ajax({
                url:self.parent().attr("action"),
                cache: false,
                contentType: false,
                processData: false,
                type: "POST",
                data: formData,

                success: function(data, textStatus, jqXHR){
                    alert('Image removed');
                    $('#profile_image').attr('src', '');
                }
        })
    }
})

$('#add_more_provision').click(function(){
    var form_idx = $('#id_form-TOTAL_FORMS').val();
    $('#provision-formset').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
    $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
})

$(document).on("click", '.remove-provision-form', function(event) {
    var form_idx = $('#id_form-TOTAL_FORMS').val();

    if(parseInt(form_idx) > 1){
        var unit = $(this).parent().parent();
        var others = unit.nextAll();

        unit.fadeOut("slow", function(){
            unit.remove();
        });

        others.each(function(){
            reduce_form_number($(this));
        });

        $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) - 1);
    }
    else{
        alert('You can not remove the last form');
    }
});

function reduce_form_number(elem){

    elem.children().each(function(){
        reduce_form_number($(this));
    });

    $.each(elem.get(0).attributes, function(){
        if(this.specified){
            var m = this.value.match(/form-[0-9]+-/g);
            if(m){
                var form_number = parseInt(m[0].match(/[0-9]+/g)) - 1;
                this.value = this.value.replace(/form-[0-9]+/g, 'form-'+form_number);
            }
        }
    });
}