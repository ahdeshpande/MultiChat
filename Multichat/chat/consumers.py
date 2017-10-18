from channels.auth import channel_session_user_from_http, channel_session_user
from chat.models import Room
from channels import Channel
import json

from chat.settings import NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS, MSG_TYPE_ENTER, \
    MSG_TYPE_LEAVE
from chat.utils import catch_client_error, get_room_or_error
from chat.exceptions import ClientError


# take user from the http and insert in the channel_session
# makes user available in the message.user attribute
@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    message.channel_session['rooms'] = []


@channel_session_user
def ws_disconnect(message):
    # unsubscribe from any connected room
    for room_id in message.channel_session.get("rooms", set()):
        try:
            room = Room.objects.get(pk=room_id)
            # removes from the room;s send group
            # if this doesn't work, then removes once the first reply message
            #  expires
            room.websocket_group.discard(message.reply_channel)
        except Room.DoesNotExist:
            print("Exception: Room does not exist")


def ws_receive(message):
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)


@channel_session_user
@catch_client_error
def chat_join(message):
    # Find the room they requested (by ID)
    room = get_room_or_error(message["room"], message.user)

    # Send a "enter message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_ENTER)

    # add them in
    room.websocket_group.add(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session[
                                                    'rooms']).union([room.id]))

    # Send a message back that will prompt them to open the room
    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": room.title,
        })
    })


@channel_session_user
@catch_client_error
def chat_leave(message):
    # Find the room they requested (by ID)
    room = get_room_or_error(message["room"], message.user)

    # Send a "leave message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_LEAVE)

    # remove them
    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session[
                                                    'rooms']).difference(
        [room.id]))

    # Send a message back that will prompt them to close the room
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        })
    })


@channel_session_user
@catch_client_error
def chat_send(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    room.send_message(message["message"], message.user)
