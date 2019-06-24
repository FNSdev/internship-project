import {createTask} from "./create_task.js";


jQuery(document).on('submit', '#create-sub-task-form', function (e) {
    e.preventDefault()
    var jq = jQuery.noConflict();
    var form = jQuery(this);
    var errors_div = document.getElementById('create-sub-task-errors');
    createTask(window.location.href + '/create-sub-task', form, errors_div)
});