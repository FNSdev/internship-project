import {multiplyCount, getActivities} from "./get_activities.js";


var url = document.location.href + '/get-activities';

jQuery(document).ready(function () {
    var jq = jQuery.noConflict();
    getActivities(url)
});

jQuery(document).on('click', '#load-more-activities-button',function () {
    multiplyCount(2);
    getActivities(url,false)
});
