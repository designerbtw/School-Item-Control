// static/js/base.js

$(document).ready(function() {
    // Automatically hide flash messages after 5 seconds
    setTimeout(function() {
        $('.flashes .alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 2500);

    // Manually hide flash messages on close button click
    $('.flashes .alert .close').on('click', function() {
        $(this).closest('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    });
});