import {count, multiplyCount, getTasks} from "./get_tasks.js";


var url = document.location.href + '/settings/get-tasks';

jQuery(document).ready(function () {
    var jq = jQuery.noConflict();
    getTasks(url)
});

jQuery(document).on('click', '#load-more-button',function () {
    multiplyCount(2);
    getTasks(url,false)
});
