$(function () {
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws"
    var ws_path = ws_scheme + "://" + window.location.host + "/chat/stream"
    console.log("Connecting to " + ws_path)
    var socket = new ReconnectingWebSocket(ws_path)

    socket.onopen = function () {
        console.log("Connected to chat socket")
    }
    socket.onclose = function () {
        console.log("Disconnected from chat socket")
    }

    // Processing responses from the server
    socket.onmessage = function (message) {
        // Decode JSON
        console.log("Got websocket message " + message.data)
        var data = JSON.parse(message.data)
        // Handle errors
        if (data.error) {
            alert(data.error)
            return
        }
        // Handle joining
        if (data.join) {
            console.log("Joining room " + data.join)
            var roomdiv = $(
                "<div class='room' id='room-" + data.join + "'>" +
                "<h2>" + data.title + "</h2>" +
                "<div class='messages'></div>" +
                "<input><button>Send</button>" +
                "</div>"
            )
            $("#chats").append(roomdiv)

            // Send button and input box
            roomdiv.find("button").on("click", function () {
                socket.send(JSON.stringify({
                    "command": "send",
                    "room": data.join,
                    "message": roomdiv.find("input").val()
                }))
                roomdiv.find("input").val("")
                return false
            })
            // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave)
            $("#room-" + data.leave).remove()

        } else if (data.message || data.type != 0) {
            var msgdiv = $("#room-" + data.room + " .messages")
            var ok_msg = ""

            switch (data.type) {
                case 0:
                    // Message
                    ok_msg = "<div class='message'>" +
                        "<span class='username'>" + data.username + "</span>" +
                        "<span class='body'>" + data.message + "</span>" +
                        "</div>";
                    break;
                case 1:
                    // Warning/Advice messages
                    ok_msg = "<div class='contextual-message text-warning'>" + data.message + "</div>";
                    break;
                case 2:
                    // Alert/Danger messages
                    ok_msg = "<div class='contextual-message text-danger'>" + data.message + "</div>";
                    break;
                case 3:
                    // "Muted" messages
                    ok_msg = "<div class='contextual-message text-muted'>" + data.message + "</div>";
                    break;
                case 4:
                    // User joined room
                    ok_msg = "<div class='contextual-message text-muted'>" + data.username + " joined the room!" + "</div>";
                    break;
                case 5:
                    // User left room
                    ok_msg = "<div class='contextual-message text-muted'>" + data.username + " left the room!" + "</div>";
                    break;
                default:
                    console.log("Unsupported message type!");
                    return;
            }
            msgdiv.append(ok_msg);
            msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
        } else {
            console.log("Cannot handle message!")
        }

    }

    // if joined the room or not
    function inRoom(roomId) {
        return $("#room-" + roomId).length > 0
    }

    // Room join/leave
    $("li.room-link").click(function () {
        roomId = $(this).attr("data-room-id")
        if (inRoom(roomId)) {
            // Leave room
            $(this).removeClass("joined")
            socket.send(JSON.stringify({
                "command": "leave",
                "room": roomId
            }))
        } else {
            // Join room
            $(this).addClass("joined")
            socket.send(JSON.stringify({
                "command": "join",
                "room": roomId
            }))
        }
    })
})