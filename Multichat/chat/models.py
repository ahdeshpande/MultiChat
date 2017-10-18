import json

from django.db import models
from django.utils.six import python_2_unicode_compatible
from channels import Group

from chat.settings import MSG_TYPE_MESSAGE


# Create your models here.
@python_2_unicode_compatible
class Room(models.Model):
    """
    A room for people to chat
    """
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the channels group that sockets should subscribe to, to get sent
        messages as they are generated
        """
        return Group("room-%s" % self.id)

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        final_msg = {'room': str(self.id),
                     'message': message,
                     'username': user.username,
                     'type': msg_type}
        self.websocket_group.send({
            "text": json.dumps(final_msg)
        })
