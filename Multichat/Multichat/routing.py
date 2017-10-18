from channels import route, include


# Display text of the received message
def message_handler(message):
    print(message['text'])


channel_routing = [
    # route("websocket.receive", message_handler)
    include("chat.routing.websocket_routing", path=r"^/chat/stream"),
    include("chat.routing.custom_routing"),
]
