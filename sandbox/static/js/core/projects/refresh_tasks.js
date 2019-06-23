import {getCookie, csrfSafeMethod} from '../../csrf.js'

var count = 1;
var tasks_rows = document.getElementById('tasks');

var getTasks = function(repeat=true) {
    jQuery.ajaxSetup({
        beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    jQuery.ajax({
        type: 'GET',
        url: window.location.href + '/get-tasks',
        data: {
            count: count
        },
        success: function (response) {
            tasks_rows.innerText = '';
            var tasks = response['tasks'];
            console.log(tasks);
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
                setTimeout(getTasks, 10 * 1000);
            }
        },
        error: function (response) {
            setTimeout(getTasks, 1 * 1000);
        }
    })
};


jQuery(document).ready(function () {
    var jq = jQuery.noConflict();
    getTasks()
});

jQuery(document).on('click', '#load-more-button',function () {
    count *= 2;
    getTasks(false)
});





