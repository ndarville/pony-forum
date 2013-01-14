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

// Makes a POST request to a view at "/js/"
// that takes the arguments `object_id` and `action` representing
// the object ID and the operation.
//
// Upon success, the `text()` inside the element is replaced with
// the opposite action provided by the Django view. E.g.:
// <a href="..." id="123">Re-subscribe</a> ->
// <a href="..." id="123">Unsubscribe</a>
    $('.js').on('click', function(e) {
        if ($('.last:contains("Log Out")').length) {
            // Overrule the default nonjs action when the submit button is clicked.
            // This allows us to handle the logic with our JavaScript instead.
            e.preventDefault();

            var $this     = $(this),
                object_id = this.id,
                action    = $this.text(),
                href      = this.href;

            $.post("/js/", {
                object_id: object_id,
                action:    action,
                href:      href
                },
                function(data) {
                    $this.text(data);
            });
        }
    });
});
