import hashlib

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import Chat, Confirm
from core.constants import TYPE_GROUP

SALT = 'letsgo-application'

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Confirm)
def add_to_chat(sender, update_fields, created, instance, **kwargs):

    if created:
        return

    if not instance.is_approved:
        return

    is_group = instance.meeting.group_type == TYPE_GROUP
    chat_exist = Chat.objects.filter(meeting=instance.meeting).exists()
    is_member = Chat.objects.filter(meeting=instance.meeting, users__in=[instance.user]).exists()

    if is_member:
        logger.warning('User already member. Meeting id: {0}, user id: {1}'.format(
            instance.meeting.id,
            instance.user.id)
        )
        return

    if is_group and chat_exist:
        chat = Chat.objects.get(meeting=instance.meeting)
        chat.users.add(instance.user)
        # TODO send push to confirm user
        return

    if not chat_exist:
        chat = Chat.objects.create(
            owner=instance.meeting.owner,
            title=instance.meeting.title,
            meeting=instance.meeting,
            channel_slug='{0}'.format(
                hashlib.sha224('{0}{1}{2}'.format(
                    instance.id,
                    instance.meeting_id,
                    SALT
                ).encode('utf-8')).hexdigest()[:20]
            )
        )
        chat.users.add(instance.user)
        # TODO SEND PUSH TO CONFIRM USER
        return

    logger.warning('Something go wrong. One by one meeting already have a chat')
