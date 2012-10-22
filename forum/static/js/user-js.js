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
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
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

// Makes a POST request to a view at "/user/js/" that takes the arguments
// `object_id` and `action` representing the object ID and the operation.
//
// Upon success, the `val()` inside the element is replaced with
// the opposite action provided by the Django view. E.g.: 
// <a href="#" id="123">Like</a> ->
// <a href="#" id="123">Remove like</a>
    $('.js').on('click', function(e) {
        // Overrule the default nonjs action when the submit button is clicked.
        // This allows us to handle the logic with our JavaScript instead.
        e.preventDefault();

        var $this     = $(this);
        var person_id = this.id;
        var text      = $this.val();

        $.post("/user/js/", {
            person_id: person_id,
            text:      text
            },
            function(data) {
                $this.val(data);
        });
    });
});