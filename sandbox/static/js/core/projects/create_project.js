import {getCookie, csrfSafeMethod} from '../../csrf.js'


jQuery(document).on('submit', '#create-project-form', function (e) {
    e.preventDefault();
    var jq = jQuery.noConflict();
    var form = jQuery(this);
    var errors_div = document.getElementById('create-project-errors');
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
        url: window.location.href,
        data: form.serialize(),
        success: function (response) {
            alert(response['message']);
            jQuery('#owned-projects').append('<div class="card mt-3" style="width: 18rem;">' +
                '<h5 class="card-header">\n' +
                '<a href=' + response['project_url'] + '>' + response['project_name'] + '</a>' +
                '</h5>' +
                '<div class="card-body">\n' +
                '<p class="card-text">' + response['project_description'] + '</p>' +
                '<a href="' + response['github_url'] + '" class="card-link">View on GitHub</a>' +
                '</div>' +
                '</div>')
        },
        error: function (response) {
            response = response['responseJSON'];
            alert(response['message']);
            let errors = response['errors'];
            for(let field in errors) {
                let messages = [];
                for (let i in errors[field]) {
                    messages.push(errors[field][i]['message'])
                    jQuery('#create-project-errors').append('<p><span class="badge badge-danger">' + field +
                        ' : ' + messages[i] + '</span></p>')
                }
            }
        }
    })
});