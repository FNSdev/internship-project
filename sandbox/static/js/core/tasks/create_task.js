import {getCookie, csrfSafeMethod} from '../../csrf.js'


export function createTask(url, form, errors_div) {
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
        url: url,
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
                    errors_div.append('<p><span class="badge badge-danger">' + field +
                        ' : ' + messages[i] + '</span></p>')
                }
            }
        }
    })
}

jQuery(document).on('submit', '#create-task-form', function (e) {
    e.preventDefault()
    var jq = jQuery.noConflict();
    var form = jQuery(this);
    var errors_div = jQuery('#create-task-errors');
    createTask(window.location.href + '/create-task', form, errors_div)
});
