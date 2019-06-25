import {getCookie, csrfSafeMethod} from '../../csrf.js'

var count = 5;
var activities_rows = document.getElementById('activities');

export function getActivities (url, repeat=true) {
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
            activities_rows.innerText = '';
            var activities = response['activities'];
            activities.forEach(activity => {
                jQuery('#activities').append(activity);
            });
            if(repeat) {
                setTimeout(getActivities, 10 * 1000, url);
            }
        },
        error: function (response) {
            setTimeout(getActivities, 1 * 1000, url);
        }
    })
}

export function multiplyCount(multiplier) {
    count *= multiplier
}
