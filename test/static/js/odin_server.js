api_version = '0.1';

$( document ).ready(function() {

    update_api_version();
    update_api_adapters();
    update_my_settable_parameter();
    poll_update()
});

function poll_update() {
    update_background_task();
    update_my_parameter();
    setTimeout(poll_update, 500);   
}

function update_api_version() {

    $.getJSON('/api', function(response) {
        $('#api-version').html(response.api);
        api_version = response.api;
    });
}

function update_api_adapters() {

    $.getJSON('/api/' + api_version + '/adapters/', function(response) {
        adapter_list = response.adapters.join(", ");
        $('#api-adapters').html(adapter_list);
    });
}

function update_background_task() {
    $.getJSON('/api/' + api_version + '/jacksAdapter/background_task', function(response) {
        var task_count_ioloop = response.background_task.ioloop_count;
        var task_count_thread = response.background_task.thread_count;
        var task_enabled = response.background_task.enable;
        $('#task-count-ioloop').html(task_count_ioloop);
        $('#task-count-thread').html(task_count_thread);
        $('#task-enable').prop('checked', task_enabled);
    });
}

function update_my_parameter() {
    $.getJSON('/api/' + api_version + '/jacksAdapter', function(response) {
        var my_parameter = response.my_parameter;
        $('#my-parameter').html(my_parameter);
    });
}

function update_my_settable_parameter() {
    $.getJSON('/api/' + api_version + '/jacksAdapter', function(response) {
        var my_settable_parameter = response.my_settable_parameter;
        $('#my-settable-parameter').prop('value', my_settable_parameter);
        var my_settable_parameter_2 = response.my_settable_parameter_2;
        $('#my-settable-parameter-2').prop('value', my_settable_parameter_2);
        var my_settable_parameter_text = response.my_settable_parameter_text;
        $('#my-settable-parameter-text').prop('value', my_settable_parameter_text);
        var my_settable_parameter_mode = response.my_settable_parameter_mode;
        $('#my-settable-parameter-mode').prop('value', my_settable_parameter_mode);
    });
}

function change_my_settable_parameter() {
    var my_settable_parameter = $('#my-settable-parameter').prop('value');
    $.ajax({
        type: "PUT",
        url: '/api/' + api_version + '/jacksAdapter',
        contentType: "application/json",
        data: JSON.stringify({'my_settable_parameter': Number(my_settable_parameter)})
    });
}

function change_my_settable_parameter_2() {
    var my_settable_parameter_2 = $('#my-settable-parameter-2').prop('value');
    $.ajax({
        type: "PUT",
        url: '/api/' + api_version + '/jacksAdapter',
        contentType: "application/json",
        data: JSON.stringify({'my_settable_parameter_2': Number(my_settable_parameter_2)})
    });
}

function change_my_settable_parameter_text() {
    var my_settable_parameter_text = $('#my-settable-parameter-text').prop('value');
    $.ajax({
        type: "PUT",
        url: '/api/' + api_version + '/jacksAdapter',
        contentType: "application/json",
        data: JSON.stringify({'my_settable_parameter_text': my_settable_parameter_text})
    });
}

function change_my_settable_parameter_mode() {
    var my_settable_parameter_mode = $('#my-settable-parameter-mode').prop('value');
    $.ajax({
        type: "PUT",
        url: '/api/' + api_version + '/jacksAdapter',
        contentType: "application/json",
        data: JSON.stringify({'my_settable_parameter_mode': my_settable_parameter_mode})
    });
}

function change_enable() {
    var enabled = $('#task-enable').prop('checked');
    console.log("Enabled changed to " + (enabled ? "true" : "false"));
    $.ajax({
        type: "PUT",
        url: '/api/' + api_version + '/jacksAdapter/background_task',
        contentType: "application/json",
        data: JSON.stringify({'enable': enabled})
    });
}
