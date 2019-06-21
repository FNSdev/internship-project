import {getCookie, csrfSafeMethod} from '../../csrf.js'


jQuery(document).on('click', '.decline', function (e) {
    var jq = jQuery.noConflict();
    var invite_id = jQuery(e.target).parent().prop('id');
    jQuery.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    jQuery.ajax({
        type: 'POST',
        url: window.location.href + '/decline/' + invite_id,
        success: function (response){
            alert(response['message'])
            jQuery(e.target).parent().siblings('.status').text('Status: declined')
        }
    })
});
