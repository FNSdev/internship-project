import {createTask} from "./create_task.js";


jQuery(document).on('submit', '#update-form', function (e) {
    e.preventDefault()
    var jq = jQuery.noConflict();
    var form = jQuery(this);
    var errors_div = document.getElementById('update-form-errors');
    createTask(window.location.href + '/update', form, errors_div)
});
