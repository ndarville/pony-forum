$(document).ready(function() {
// This CSRF token allows us to make POST requests
    $(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host, // host + port
                protocol = document.location.protocol,
                sr_origin = '//' + host,
                origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    $('.js').on('click', function(e) {
        // Only perform the following if user is logged in,
        // detected by checking for a "Log out" in navigation.
        if ($('.last:contains("Log Out")').length) {
            // Overrule default nonjs action when submit button is clicked
            // to allow handling the the logic with our JavaScript instead.
            e.preventDefault();

            var $this     = $(this),
                object_id = $("#thread-id").val(),
                user_id   = this.id,
                action    = $this.text()

            $.post("/thread/co-editors/js/", {
                object_id: object_id,
                user_id:   user_id,
                action:    action
                },
                function(data) {
                    $this.text(data);
            });
        }
    });
});
