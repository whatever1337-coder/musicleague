from flask import url_for

from musicleague.messenger.context import create_context
from musicleague.messenger.context import STATUS_DEFAULT
from musicleague.messenger.context import STATUS_LINK_ACCOUNT
from musicleague.messenger.send import send_message
from musicleague.persistence.select import select_user
from musicleague.persistence.update import upsert_user


def process_new_user(messenger_id):
    create_context(messenger_id, status=STATUS_LINK_ACCOUNT)

    send_message(
        messenger_id,
        "Hi! I don't believe we've spoken before. Please provide the ID given "
        "to you on the Music League website.\nIf you don't have one, you "
        "can find it here: {}".format(url_for('user_id', _external=True)))


def process_link_user(context, message_text):
    user = select_user(message_text)
    if not user:
        send_message(context.id,
                     "I'm sorry. I didn't find a user with that ID.")
        return

    context.status = STATUS_DEFAULT
    context.user = user
    context.save()

    user.messenger = context
    upsert_user(user)

    send_message(context.id,
                 "I've linked your Facebook and Music League accounts!\n"
                 "You will now receive notifications from me in Messenger.")
