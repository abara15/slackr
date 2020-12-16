import re
from threading import Timer
from datetime import datetime, timedelta
from ..tests.random_gen import random_string
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from .auth import get_id_from_token
from ..db import users, messages, channels, reacts, get_full_message


def message_sendlater(token, channel_id, message, time_sent):
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if auth_u_id not in channel["all_members"]:
        raise AccessError("Authorised user not member of the channel.")
    if len(message) > 1000:
        raise ValueError("Message exceeds 1000 characters.")
    if time_sent < datetime.now(): 
        raise ValueError("Time_sent cannot be in the past.")
    
    t = Timer(time_sent.seconds() + 1, message_send, [token, channel_id, message])
    t.start()


def message_send(token, channel_id, message):
    """
    Send a message from authorised_user to the channel specified by channel_id.

    Raises:
        ValueError: channel_id does not exist.
        ValueError: Message exceeds 1000 characters.
        AccessError: Authorised user not the member of channel.
    """
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if auth_u_id not in channel["all_members"]:
        raise AccessError("Authorised user not member of the channel.")
    if len(message) > 1000:
        raise ValueError("Message exceeds 1000 characters.")
    message_payload = {
        "channel_id": channel_id,
        "u_id": auth_u_id,
        "message": message,
        "is_pinned": False,
        "time_created": datetime.now().timestamp(),
    }
    message_id = messages.add(message_payload)
    react_payload = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    reacts.addWithId(react_payload, message_id)
    print(messages)
    return {"message_id": message_id}


def message_remove(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel.

    Raises:
        ValueError: Message (based on ID) no longer exists.
        AccessError: When none of the following is true.
            Message with message_id was not sent by the authorised user making this request.
            The authorised user is an admin or owner of this channel or the slackr.
    """

    auth_u_id = get_id_from_token(token)
    user = users.get(auth_u_id)
    message = messages.get(message_id)

    if message is None:
        raise ValueError("Message does not exist.")

    channel = channels.get(message["channel_id"])

    if (
        user["is_admin"] is False
        and user["is_slackr_owner"] is False
        and auth_u_id != message["u_id"]
        and auth_u_id not in channel["owners"]
    ):
        raise AccessError("User does not have the correct permissions.")

    messages.delete_record(message_id)
    reacts.delete_record(message_id)


def message_edit(token, message_id, message):
    """
    Given a message, update it's text with new text.

    Raises:
        AccessError: When none of the following is true.
            Message with message_id was not sent by the authorised user making this request.
            The authorised user is an admin or owner of this channel or the slackr.
    """

    auth_u_id = get_id_from_token(token)
    user = users.get(auth_u_id)
    message_payload = messages.get(message_id)

    if message_payload is None:
        raise ValueError("Message does not exist.")

    if (
        user["is_admin"] is False
        and user["is_slackr_owner"] is False
        and auth_u_id != message_payload["u_id"]
    ):
        raise AccessError("User does not have the correct permissions.")

    if message == "":
        return message_remove(token, message_id)

    messages.set(message_id, "message", message)


def message_react(token, message_id, react_id):
    """
    Given a message within a channel the authorised user is part of, add a "react"
    to that particular message.

    Raises:
        ValueError when:
        Message_id is not a valid message within a channel that the authorised user has joined.
        React_id is not a valid React ID.
        Message with ID message_id already contains an active React with ID react_id.
    """
    auth_u_id = get_id_from_token(token)
    message = messages.get(message_id)

    if message is None:
        raise ValueError("message_id is invalid.")

    channel = channels.get(message["channel_id"])
    full_message = get_full_message(auth_u_id, message_id)

    if react_id not in [1, 2, 3, 4, 5, 6, 7]:
        raise ValueError("react_id is invalid.")

    if auth_u_id not in channel["all_members"]:
        raise ValueError("Message is not within same channel as user.")

    already_reacted = False
    for react in full_message["reacts"]:
        if react["is_this_user_reacted"]:
            already_reacted = True

    if already_reacted:
        raise ValueError("You have already reacted to this message.")

    reacts.set(message_id, react_id, auth_u_id)


def message_unreact(token, message_id, react_id):
    """
    Given a message within a channel the authorised user is part of, remove a "react" to that
    particular message

    Raises:
        ValueError when:
        Message_id is not a valid message within a channel that the authorised user has joined.
        React_id is not a valid React ID.
        Message with ID message_id does not contain an active React with ID react_id.
    """
    auth_u_id = get_id_from_token(token)
    message = messages.get(message_id)

    if message is None:
        raise ValueError("message_id is invalid.")

    channel = channels.get(message["channel_id"])
    full_message = get_full_message(auth_u_id, message_id)

    if react_id not in [1, 2, 3, 4, 5, 6, 7]:
        raise ValueError("react_id is invalid.")

    if auth_u_id not in channel["all_members"]:
        raise ValueError("Message is not within same channel as user.")

    already_reacted = False
    for react in full_message["reacts"]:
        if react["is_this_user_reacted"]:
            already_reacted = True

    if not already_reacted:
        raise ValueError("You have not reacted to this message yet.")

    reacts.remove(message_id, react_id, auth_u_id)


def message_pin(token, message_id):
    """
    Given a message within a channel, mark it as "pinned" to be given
    special display treatment by the frontend.

    Raises:
        ValueError: message_id is not a valid message.
        ValueError: Message with ID message_id is already pinned.
        ValueError: Authorised user is not an admin.
        AccessError: Authorised user is not a member of the channel that the message is within.
    """
    auth_u_id = get_id_from_token(token)
    message = messages.get(message_id)

    if message is None:
        raise ValueError("Message does not exist.")

    channel = channels.get(message["channel_id"])

    if message["is_pinned"] is True:
        raise ValueError("Message is already pinned.")

    if auth_u_id not in channel["all_members"]:
        raise AccessError(
            "User is not a member of channel that targeted message is within."
        )

    messages.set(message_id, "is_pinned", True)


def message_unpin(token, message_id):
    """
        Given a message within a channel, remove it's mark as unpinned.

        Raises:
            ValueError when:
                message_id is not a valid message
                The authorised user is not an admin
                Message with ID message_id is already unpinned.
            AccessError when:
                The authorised user is not a member of the channel that the message is within.
    """
    auth_u_id = get_id_from_token(token)
    message = messages.get(message_id)

    if message is None:
        raise ValueError("Message does not exist.")

    channel = channels.get(message["channel_id"])

    if message["is_pinned"] is False:
        raise ValueError("Message is already unpinned.")

    if auth_u_id not in channel["all_members"]:
        raise AccessError(
            "User is not a member of channel that targeted message is within."
        )

    messages.set(message_id, "is_pinned", False)

