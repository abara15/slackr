from datetime import datetime, timedelta
from threading import Timer
from queue import Queue
from ..db import users, channels, messages, reacts
from .auth import get_id_from_token, valid_email
from .messages import message_send
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError

def channel_none(channel):
    if channel is None:
        raise ValueError("Channel does not exist.")

def u_id_check(u_id, channel):
    if u_id not in channel["all_members"]:
        raise AccessError("The authorised user is not a member of the channel.")

def active_check(variable):
    if variable is True:
        raise ValueError("An active standup is currently running in this channel.")
    else:
        raise ValueError("An active standup is not currently running in this channel.")


def standup_start(token, channel_id, length):
    """
    For a given channel, start the standup period whereby for the next 15 minutes if someone calls
    "standup_send" with a message, it is buffered during the 15 minute window then at the end of
    the 15 minute window a message will be added to the message queue in the channel from the user
    who started the standup.
    Args:
        token, channel_id
    Returns:
        { time_finish }
    Raises:
        ValueError when: Channel ID is not a valid channel
        ValueError when: An active standup is currently running in this channel
        AccessError when: The authorised user is not a member of the channel that the message is within
    """
    u_id = get_id_from_token(token)  # Decodes the token and returns u_id
    channel = channels.get(channel_id)

    # Error Raises
    channel_none(channel)
    u_id_check(u_id, channel)
    active_check(channel["is_standup_active"])

    # Takes current time and adds 15 mins
    time_finish = datetime.now() + timedelta(seconds=length)
    print(time_finish)

    channels.set(channel_id, "is_standup_active", True)
    channels.set(channel_id, "time_finish", time_finish)
    t = Timer(length + 1, standup_finish, [token, u_id, channel_id])
    t.start()

    return {"time_finish": time_finish.timestamp()}


def standup_active(token, channel_id):
    """
    Returns if the given channel is in standup and the time that the standup will finish.
    Returns:
        { is_active, time_finish }
    Raises:
        ValueError: If channel_id does not exist.
    """
    get_id_from_token(token)
    channel = channels.get(channel_id)

    # Error Raises
    channel_none(channel)

    time_finish = channel["time_finish"]
    if time_finish is not None:
        time_finish = time_finish.timestamp()

    return {
        "is_active": channel["is_standup_active"],
        "time_finish": time_finish,
    }


def standup_send(token, channel_id, message):
    """
    Sending a message to get buffered in the standup queue, assuming a standup is currently active.
    Args:
        token, channel_id, message
    Returns:
        {}
    Raises:
        ValueError: Channel ID is not a valid channel
        ValueError: Message is more than 1000 characters.
        ValueError: An active standup is not currently running in this channel
        AccessError: The authorised user is not a member of the channel that the message is within
    """
    u_id = get_id_from_token(token)  # Decodes the token and returns u_id
    channel = channels.get(channel_id)
    user = users.get(u_id)

    # Error Raises
    channel_none(channel)
    u_id_check(u_id, channel)
    active_check(channel["is_standup_active"])
    if len(message) > 1000:
        raise ValueError("Message is more than 1000 characters.")

    handle = user["handle_str"]
    added_message = f"{handle}: {message}"
    channels.set(channel_id, "standup_queue", added_message)


def standup_finish(token, u_id, channel_id):
    channel = channels.get(channel_id)
    queuedMessages = channel["standup_queue"]
    sentMessage = ""

    while len(queuedMessages) != 0:
        message = queuedMessages[0]
        sentMessage += message
        if len(queuedMessages) != 1:
            sentMessage += "\n"
        channels.remove(channel_id, "standup_queue", message)

    if sentMessage != "":
        message_id = messages.add(
            {
                "channel_id": channel_id,
                "u_id": u_id,
                "message": sentMessage,
                "is_pinned": False,
                "time_created": datetime.now().timestamp(),
            }
        )
        react_payload = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
        reacts.addWithId(react_payload, message_id)

    channels.set(channel_id, "is_standup_active", False)
    channels.set(channel_id, "time_finish", None)
