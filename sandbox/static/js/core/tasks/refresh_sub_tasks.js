import {csrfSafeMethod, getCookie} from "../../csrf.js";


var url = document.location.href + '/get-sub-tasks';
var count = 1;
var tasks_rows = document.getElementById('tasks');

function getSubTasks (repeat=true) {
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
                var branches = task['branches'];
                var branches_html = '';
                branches.forEach(branch => {
                    branches_html += '<p><a href="' + branch['url'] +
                        '" a>' + branch['name'] + '</a></p>'
                });
                jQuery('#tasks').append('<tr>' +
                    '<td>' + task['name'] + '</td>' +
                    '<td>' + task['priority'] + '</td>' +
                    '<td>' + task['status'] + '</td>' +
                    '<td>' + task['deadline'] + '</td>' +
                    '<td>' + branches_html + '</td>' +
                    '</tr>')
            });
            if(repeat) {
                setTimeout(getSubTasks, 10 * 1000);
            }
        },
        error: function (response) {
            setTimeout(getSubTasks, 1 * 1000);
        }
    })
}


jQuery(document).ready(function () {
    var jq = jQuery.noConflict();
    getSubTasks()
});

jQuery(document).on('click', '#load-more-button',function () {
    count *= 2;
    getSubTasks(false)
});
