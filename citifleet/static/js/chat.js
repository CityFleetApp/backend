$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var token = $('#token').val();

    $("#connectform").on("submit", function(event) {
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        var token = $('#token').val();
        chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname + '?token=' + token);

        chatsock.onmessage = function(message) {
            var data = JSON.parse(message.data);
            var chat = $("#chat")
            var ele = $('<tr></tr>')

            ele.append(
                $("<td></td>").text(data.author)
            )
            ele.append(
                $("<td></td>").text(data.text)
            )
            ele.append(
                $("<td><img src='" + data.image + "' /></td>")
            )

            chat.append(ele)
        };
        return false;
    });

    $("#chatform").on("submit", function(event) {
        var file    = document.querySelector('input[type=file]').files[0];
        var reader  = new FileReader();

        if (file) {
            reader.readAsDataURL(file);
        } else {
            var message = {
                method: 'post_message',
                room: $('#room').val(),
                text: $('#message').val(),
                image: reader.result
            }

            chatsock.send(JSON.stringify(message));
            $("#message").val('').focus();
            return false;
        }

        reader.addEventListener("load", function () {
            var message = {
                method: 'post_message',
                room: $('#room').val(),
                text: $('#message').val(),
                image: reader.result
            }
            chatsock.send(JSON.stringify(message));
            $("#message").val('').focus();
            return false;
        }, false);

        return false;
    });
});

