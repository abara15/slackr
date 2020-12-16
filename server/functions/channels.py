from datetime import datetime
from operator import itemgetter
from .auth import get_id_from_token
from ..db import users, channels, messages, reacts
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from ..tests.random_gen import random_string, random_date


def channel_invite(token, channel_id, u_id):
    """
    Invites a user (with user id u_id) to join a channel with ID channel_id. Once
    invited the user is added to the channel immediately.

    Raises:
        AccessError: The authorised user is not a member of the channel.
        ValueError: channel_id does not exist.
        ValueError: u_id does not exist.
    """
    authorised_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    user_to_invite = users.get(u_id)
    if user_to_invite is None:
        raise ValueError("u_id does not exist.")
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if authorised_u_id not in channel["all_members"]:
        raise AccessError("The authorised user is not a member of the channel.")
    channels.set(channel_id, "all_members", u_id)


def channel_details(token, channel_id):
    """
    Given a Channel with ID channel_id that the authorised user is part of, provide
    basic details about the channel.

    Returns:
        { name: string, owner_members, all_members }
        *_members: { u_id: number, name_first: string, name_last: string }

    Raises:
        ValueError: channel_id does not exist.
        AccessError: The authorised user is not a member of the channel.
    """
    authorised_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if authorised_u_id not in channel["all_members"]:
        raise AccessError("The authorised user is not a member of the channel.")
    name = channel["name"]
    all_members = []
    owner_members = []
    for member_id in channel["all_members"]:
        member = users.get(member_id)
        all_members.append(
            {
                "u_id": member["u_id"],
                "name_first": member["first_name"],
                "name_last": member["last_name"],
                "profile_img_url ": member["img_url"],
            }
        )
    for owner_id in channel["owners"]:
        owner = users.get(owner_id)
        owner_members.append(
            {
                "u_id": owner["u_id"],
                "name_first": owner["first_name"],
                "name_last": owner["last_name"],
                "profile_img_url ": owner["img_url"],
            }
        )
    return {"name": name, "all_members": all_members, "owner_members": owner_members}


def channel_messages(token, channel_id, start=0):
    """
    Given a Channel with ID channel_id that the authorised user is part of, return
    up to 50 messages between index "start" and "start + 50". Message with index 0
    is the most recent message in the channel. This function returns a new index
    "end" which is the value of "start + 50", or, if this function has returned
    the least recent messages in the channel, returns -1 in "end" to indicate
    there are no more messages to load after this return.

    Returns:
        { messages, start: number, end: number }
        messages: { 
            message_id: number, 
            u_id: number,
            message: string,
            time_created: datetime,
            react_ids
            is_pinned: boolean,
            is_unread: boolean }
        react_ids: { react_id: string -> [u_ids: number]}


    Raises:
        ValueError: channel_id does not exist.
        ValueError: start is greater than the total number of messages in the channel.
        AccessError: Authorised user is not a member of the channel.
    """
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if auth_u_id not in channel["all_members"]:
        raise AccessError("The authorised user is not a member of the channel.")
    messages_results = messages.query("channel_id", "==", channel_id)
    if start > len(messages_results):
        raise ValueError(
            "start is greater than the total number of messages in the channel."
        )
    if start < 0:
        raise ValueError("Invalid value for start.")
    sorted_messages = sorted(messages_results, key=itemgetter("time_created"))
    sorted_messages.reverse()
    end = len(sorted_messages) if start + 50 > len(sorted_messages) - 1 else start + 50
    messages_list = sorted_messages[start:end]
    returned_messages = []
    for message in messages_list:
        returned_messages.append(
            {
                "message_id": message["message_id"],
                "u_id": message["u_id"],
                "message": message["message"],
                "is_pinned": message["is_pinned"],
                "time_created": message["time_created"],
            }
        )
    for message in returned_messages:
        reacts_results = reacts.get(message["message_id"])
        returned_reacts = []
        for react_id in reacts_results:
            if not react_id == "message_id":
                returned_reacts.append(
                    {
                        "react_id": react_id,
                        "u_ids": reacts_results[react_id],
                        "is_this_user_reacted": auth_u_id in reacts_results[react_id],
                    }
                )
        message["reacts"] = returned_reacts
    return {
        "messages": returned_messages,
        "start": start,
        "end": -1 if end == len(sorted_messages) else end,
    }


def channel_leave(token, channel_id):
    """
    Given a channel ID, the user removed as a member of this channel.

    Raises:
        ValueError: channel_id does not refer to a valid channel that the authorised user is part of.
    """
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel does not exist")
    if auth_u_id not in channel["all_members"]:
        raise AccessError("Authorised user is not a member of the channel.")
    channels.remove(channel_id, "all_members", auth_u_id)


def channel_join(token, channel_id):
    """
    Given a channel_id of a channel that the authorised user can join, adds them
    to that channel.

    Raises:
        ValueError: channel_id does not refer to a valid channel that the authorised user is part of.
        AccessError: channel_id refers to a channel that is private (when the authorised user is not an admin).
    """
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel_id does not exist.")
    user = users.get(auth_u_id)
    if user["is_admin"] is not True and channel["is_public"] is False:
        raise AccessError("channel is not public")

    channels.set(channel_id, "all_members", auth_u_id)


def channel_addowner(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of this channel.

    Raises:
        ValueError: channel_id does not refer to a valid channel that the authorised user is part of.
        ValueError: u_id is not an owner of the channel.
        AccessError: Authorised user is not an owner of the slackr, or an owner of this channel.
    """
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if u_id in channel["owners"]:
        raise ValueError("user is already an owner")
    user = users.get(auth_u_id)
    if auth_u_id not in channel["owners"] and user["is_admin"] is False:
        raise AccessError("You do not have permission to add owners")

    channels.set(channel_id, "owners", u_id)


def channel_removeowner(token, channel_id, u_id):
    """
    Remove user with user id u_id an owner of this channel.

    Raises:
        ValueError: channel_id does not refer to a valid channel that the authorised user is part of.
        ValueError: u_id is not an owner of the channel.
        AccessError: Authorised user is not an owner of the slackr, or an owner of this channel.
    """
    auth_u_id = get_id_from_token(token)
    channel = channels.get(channel_id)
    if channel is None:
        raise ValueError("channel_id does not exist.")
    if u_id not in channel["owners"]:
        raise ValueError("user is not an owner")
    user = users.get(auth_u_id)
    if auth_u_id not in channel["owners"] and user["is_admin"] is False:
        raise AccessError("You do not have permission to remove owners")

    channels.remove(channel_id, "owners", u_id)


def channels_list(token):
    """
    Provide a list of all channels (and their associated details) that
    the authorised user is part of.

    Returns:
        { channels }
        channels: { id, name }
    """
    auth_u_id = get_id_from_token(token)
    all_channels = channels.query("all_members", "contains", auth_u_id)
    channels_list = []
    for channel in all_channels:
        channels_list.append(
            {"channel_id": channel["channel_id"], "name": channel["name"]}
        )
    return {"channels": channels_list}


def channels_listall(token):
    """
    Provide a list of all channels (and their associated details).

    Returns:
        { channels }
        channels: { id, name }
    """
    channels_results = channels.list()
    channels_list = []
    for channel in channels_results:
        channels_list.append(
            {"channel_id": channel["channel_id"], "name": channel["name"]}
        )
    return {"channels": channels_list}


def channels_create(token, name, is_public):
    """
    Creates a new channel with that name that is either a public or private channel.

    Returns:
        channel_id: number

    Raises:
        ValueError: Name is more than 20 characters long.
    """
    auth_u_id = get_id_from_token(token)
    if len(name) > 20:
        raise ValueError("")
    channel_payload = {
        "name": name,
        "all_members": [auth_u_id],
        "owners": [auth_u_id],
        "is_public": is_public,
        "is_standup_active": False,
        "time_finish": None,
        "standup_queue": [],
    }
    return channels.add(channel_payload)
