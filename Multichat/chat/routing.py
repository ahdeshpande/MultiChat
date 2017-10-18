from channels import route
from chat.consumers import ws_connect, ws_disconnect, ws_receive, chat_join, \
    chat_leave, chat_send

websocket_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.disconnect", ws_disconnect),
    route("websocket.receive", ws_receive),
]

custom_routing = [
    route("chat.receive", chat_join, command="^join$"),
    route("chat.receive", chat_leave, command="^leave$"),
    route("chat.receive", chat_send, command="^send$"),
]
