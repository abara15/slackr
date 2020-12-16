from ..db import users, messages, channels, get_full_message
from .auth import get_id_from_token, valid_email
from ..tests.random_gen import random_string


def search(token, query_str):
    """
    Given a query string, return a collection of messages in all of the channels that the user has joined that match the query
    Args: 
        token, query_str   
    Returns:
        { messages: [] }
    Raises:
        N/A
    """

    u_id = get_id_from_token(token)  # Decode token for the u_id
    channels_results = channels.query("all_members", "contains", u_id)
    if channels_results == [] or query_str == "":
        return {"messages": []}
    else:
        results = []
        for channel in channels_results:
            all_messages = messages.query("channel_id", "==", channel["channel_id"])
            for message in all_messages:
                if query_str in message["message"]:
                    results.append(get_full_message(u_id, message["message_id"]))

        return {"messages": results}  # Returns list of messages with query in it
