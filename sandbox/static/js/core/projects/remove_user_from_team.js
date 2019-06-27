import {getCookie, csrfSafeMethod} from '../../csrf.js'


jQuery(document).on('click', '.remove', function (e) {
    var jq = jQuery.noConflict();
    var user_email = jQuery(e.target).parent().parent().prop('id');
    jQuery.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    jQuery.ajax({
        type: 'POST',
        url:  window.location.href + '/remove-user/' + user_email,
        success: function (response){
            alert(response['message']);
            if(response['status'] == 'ok') {
                jQuery(e.target).parent().parent().remove()
            }
        }
    })
});
