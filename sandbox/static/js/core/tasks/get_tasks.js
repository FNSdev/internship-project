import {getCookie, csrfSafeMethod} from '../../csrf.js'

export var count = 1;
var tasks_rows = document.getElementById('tasks');

export function getTasks (url, repeat=true) {
    jQuery.ajaxSetup({
        beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    jQuery.ajax({
        type: 'GET',
        url: url,
        data: {
            count: count
        },
        success: function (response) {
            tasks_rows.innerText = '';
            var tasks = response['tasks'];
            tasks.forEach(task => {
                jQuery('#tasks').append('<tr>' +
                    '<td>' + task['name'] + '</td>' +
                    '<td>' + task['progress'] + ' %</td>' +
                    '<td>' + task['priority'] + '</td>' +
                    '<td>' + task['status'] + '</td>' +
                    '<td>' + task['deadline'] + '</td>' +
                    '</tr>')
            });
            if(repeat) {
                setTimeout(getTasks, 10 * 1000, url);
            }
        },
        error: function (response) {
            setTimeout(getTasks, 1 * 1000, url);
        }
    })
}

export function multiplyCount(multiplier) {
    count *= multiplier
}
