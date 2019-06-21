import {getCookie, csrfSafeMethod} from '../../csrf.js'


jQuery(document).on('submit', '#invite-user-form', function (e) {
    e.preventDefault()
    var jq = jQuery.noConflict();
    var form = jQuery(this);
    var errors_div = document.getElementById('invite-user-errors');
    errors_div.innerText = '';
    jQuery.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    jQuery.ajax({
        type: 'POST',
        url: window.location.href + '/invite-user',
        data: form.serialize(),
        success: function (response) {
            alert(response['message'])
        },
        error: function (response) {
            response = response['responseJSON'];
            alert(response['message']);
            let errors = response['errors'];
            for(let field in errors) {
                let messages = []
                for (let i in errors[field]) {
                    messages.push(errors[field][i]['message'])
                    jQuery('#invite-user-errors').append('<p><span class="badge badge-danger">' + field +
                        ' : ' + messages[i] + '</span></p>')
                }
            }
        }
    })
});