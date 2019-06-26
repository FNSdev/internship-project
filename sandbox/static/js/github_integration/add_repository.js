import {getCookie, csrfSafeMethod} from '../csrf.js'


jQuery(document).on('click', '.add', function(e) {
    var jq = jQuery.noConflict();
    var repository = e.target.id;

    jQuery.ajaxSetup({
        beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    jQuery.ajax ({
        type: 'POST',
        url: '/github-integration/add-repository',
        data: {
            repository: repository,
        },
        success: function(response) {
            alert(response['message'])
            var get_task_result = function () {
                jQuery.ajax ({
                    type: 'GET',
                    url: '/github-integration/get-celery-task-status',
                    data: {
                        task_id: response['task_id']
                    },
                    success: function (response) {
                        if (response['status'] == 'ready') {
                            alert(response['message'])
                        }
                        else {
                            setTimeout(get_task_result, 2 * 1000)
                        }

                    }
                })
            };
            get_task_result()
        }
    })
});