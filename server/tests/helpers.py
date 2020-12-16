from ..functions.auth import auth_register
from ..functions.messages import message_send
from .random_gen import random_string
from ..db import users, channels, messages, reacts


def create_mock_user():
    """Creates a mock user using auth_register and returns all user data."""
    email = f"{random_string(5)}@example.com"
    password = "strongPassword@24"
    name_first = "John"
    name_last = "Doe"
    u_id, token = auth_register(email, password, name_first, name_last).values()
    return {
        "u_id": u_id,
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last,
        "handle_str": None,
        "img_url": None, # Added to fix users_test 1
        "token": token,
    }


def generate_messages(token, channel_id, messages_number):
    """
    Sends a number of random messages (specificed by messages_number) from user to the specified channel (by channel_id).
    Returns all message strings sent in a list in the order of most recently sent -> to oldest one sent.
    """
    messages = []
    for x in range(0, messages_number):
        message = f"{x+1}-{random_string()}"
        messages.append(message)
        message_send(token, channel_id, message)
    messages.reverse()
    return messages


def clear_dbs():
    """
    Clear all system DBs to have a reset system at the beginning of each test.
    """
    users.drop()
    messages.drop()
    channels.drop()
    reacts.drop()
