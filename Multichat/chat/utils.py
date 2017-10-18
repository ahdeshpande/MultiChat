from functools import wraps

from chat.exceptions import ClientError
from chat.models import Room


def catch_client_error(func):
    @wraps(func)
    def inner(message, *args, **kwrargs):
        try:
            return func(message, *args, **kwrargs)
        except ClientError as e:
            e.send_to(message.reply_channel)

    return inner


def get_room_or_error(room_id, user):
    if not user.is_authenticated():
        raise ClientError("USER_HAS_TO_LOGIN")
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    if room.staff_only and not user.is_staff:
        raise ClientError("ROOM_ACCESS_DENIED")
    return room
