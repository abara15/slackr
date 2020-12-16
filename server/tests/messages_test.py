import pytest
from ..functions.auth import auth_register, get_id_from_token
from ..functions.channels import (
    channel_invite,
    channel_details,
    channel_messages,
    channels_create,
    channel_addowner,
    channel_leave,
)
from ..functions.messages import (
    message_send,
    message_remove,
    message_react,
    message_edit,
    message_sendlater,
    message_unreact,
    message_unpin,
    message_pin,
)
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from .helpers import create_mock_user, generate_messages, clear_dbs
from .random_gen import random_string, random_date
from datetime import datetime, timedelta

@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield



######################################################################
#################### Tests for message_sendlater #####################
######################################################################

def test_message_sendlater_1(): 
    # Channel id is non existent
    user = create_mock_user()
    token = user["token"]
    channel_id = None
    message = "I have to go now!"
    time_sent = datetime(2020, 12, 19, 17, 55, 0, 2) 
    
    with pytest.raises(ValueError, match=r"channel_id does not exist."):
        message_sendlater(token, channel_id, message, time_sent)

def test_message_sendlater_2():
    # Message is more than 1000 characters
    user = create_mock_user()
    token = user["token"]
    message = random_string(1001)
    channel_id = channels_create(token, "Channel 1", True)
    time_sent = datetime(2020, 12, 19, 17, 55, 0, 2) 
    
    with pytest.raises(ValueError, match=r"Message exceeds 1000 characters."):
        message_sendlater(token, channel_id, message, time_sent)
    
    
def test_message_sendlater_3():
    # Time sent is in the past
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message = "We can't travel back in time."
    time_sent = datetime(2017, 12, 19, 17, 55, 0, 2) 
    
    with pytest.raises(ValueError, match=r"Time_sent cannot be in the past."):
        message_sendlater(token, channel_id, message, time_sent)

def test_message_sendlater_4():
    # Authorised user not part of channel
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message = "User aint part of channel"
    time_sent = datetime(2020, 12, 19, 17, 55, 0, 2) 
    
    with pytest.raises(AccessError, match=r"Authorised user not member of the channel."):
        message_sendlater(token2, channel_id, message, time_sent)

def test_message_sendlater_userleaves():
    # User is added then leaves --> Should not be able to send message
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)
    channel_id = channels_create(token, "Channel 1", True)
    channel_invite(token, channel_id, u_id)
    channel_leave(token2, channel_id)
    message = "User aint part of channel"
    time_sent = datetime(2020, 12, 19, 17, 55, 0, 2) 
    
    with pytest.raises(AccessError, match=r"Authorised user not member of the channel."):
        message_sendlater(token2, channel_id, message, time_sent)
    
    
#######################################################################
################## Tests for message_send #############################
#######################################################################


def test_message_send_1():
    # Generic test
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message_send(token, channel_id, "How you doin?")


def test_message_send_2():
    # Generic test 2
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 2", True)
    message_send(token, channel_id, "That can't be true")


def test_message_send_1000():
    # Test for when message > 1000
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message = random_string(1001)
    with pytest.raises(ValueError, match=r"Message exceeds 1000 characters."):
        message_send(token, channel_id, message)


def test_message_send_3():
    # Test for when channel_id doesnt exist
    user = create_mock_user()
    token = user["token"]
    channel_id = 400000
    message = "Yeah Baby"
    with pytest.raises(ValueError, match=r"channel_id does not exist."):
        message_send(token, channel_id, message)


def test_message_send_invalid_user():
    # Test for when Authorised user not member of the channel.
    user = create_mock_user()
    user2 = create_mock_user()
    token = user["token"]
    token2 = user2["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message = "No Clue Mate"
    with pytest.raises(
        AccessError, match=r"Authorised user not member of the channel."
    ):
        message_send(token2, channel_id, message)
        
        
def test_message_send_userleaves():
    # User is added then leaves --> Should not be able to send message
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)
    channel_id = channels_create(token, "Channel 1", True)
    channel_invite(token, channel_id, u_id)
    channel_leave(token2, channel_id)
    message = "User aint part of channel" 
    
    with pytest.raises(AccessError, match=r"Authorised user not member of the channel."):
        message_send(token2, channel_id, message)


##############################################################################
######################### Tests for message_remove ###########################
##############################################################################


def test_message_remove_1():
    # Raise value error when message_id no longer exists
    user = create_mock_user()
    token = user["token"]
    with pytest.raises(ValueError, match=r"Message does not exist."):
        message_remove(token, "randomid")


def test_message_remove_message_invalid():
    # Raise value error when message_id no longer exists
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message_send(token, channel_id, "How was your day?")
    channel_messages(token, channel_id, 0)
    message_id = None
    with pytest.raises(ValueError, match=r"Message does not exist."):
        message_remove(token, message_id)


def test_message_remove_2():
    # Test when owner tries to remove message
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", True)
    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    assert message_remove(token, message_id) == None


def test_message_remove_usermadeowner():
    # User is added to a channel and made admin
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)
    
    channel_id = channels_create(token, "Channel 1", True)
    channel_addowner(token, channel_id, u_id)
    
    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    
    assert message_remove(token2, message_id) == None

# User is not part of channel
def test_message_remove_3():

    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]

    channel_id = channels_create(token, "Channel 1", True)

    message_send(token, channel_id, "How was your day?")

    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]

    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_remove(token2, message_id)


# User is not owner of channel
def test_message_remove_4():

    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)

    channel_id = channels_create(token, "Channel 1", False)
    channel_invite(token, channel_id, u_id)

    message_send(token, channel_id, "How was your day?")

    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]

    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_remove(token2, message_id)


# User is added to channel but should not be able to remove messages (not authorised)
def test_message_remove_5():

    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]

    channel_id = channels_create(token, "Channel 1", False)
    channel_invite(token, channel_id, user2["u_id"])

    message_send(token, channel_id, "How was your day?")

    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]

    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_remove(token2, message_id)


# User is not admin of slackr
def test_message_remove_not_admin():
    owner = create_mock_user()
    user = create_mock_user()
    token = owner["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_remove(user["token"], message_id)


########################################
######### Tests for message_edit #######
########################################

# User creates channel and should have ability to edit messages
def test_message_edit_2():

    user = create_mock_user()
    token = user["token"]

    channel_id = channels_create(token, "Channel 1", True)

    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    message = "My day was good."

    assert message_edit(token, message_id, message) == None


def test_message_edit_3():
    # User is not part of channel_addowner and shouldnt be able to edit messages
    owner = create_mock_user()
    owner_token = owner["token"]
    user = create_mock_user()
    user_token = user["token"]
    channel_id = channels_create(owner_token, "Channel 1", True)
    message_id = message_send(owner_token, channel_id, "How was your day?")[
        "message_id"
    ]
    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_edit(user_token, message_id, "My day was good.")


# User added to channel but is not an owner
def test_message_edit_4():

    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]

    channel_id = channels_create(token, "Channel 1", False)
    channel_invite(token, channel_id, user2["u_id"])

    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    message = "My day was good."

    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_edit(token2, message_id, message)


def test_message_edit_6():
    # User uses a message_id which is invalid/ non-existent
    user = create_mock_user()
    token = user["token"]
    
    with pytest.raises(ValueError, match=r"Message does not exist."):
        message_edit(token, "invalidid", "My day was good.")


def test_message_edit_useradmin():
    # User is not admin of slackr
    owner = create_mock_user()
    owner_token = owner["token"]
    user = create_mock_user()
    user_token = user["token"]
    channel_id = channels_create(owner_token, "Channel 1", False)
    message_id = message_send(owner_token, channel_id, "How was your day?")[
        "message_id"
    ]
    with pytest.raises(
        AccessError, match=r"User does not have the correct permissions."
    ):
        message_edit(user_token, message_id, "Fix it Felix.")


def test_message_edit_empty_to_remove():
    # New message is an empty string so message is removed
    owner = create_mock_user()
    token = owner["token"]
    channel_id = channels_create(token, "Channel", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    message_edit(token, message_id, "")
    messages = channel_messages(token, channel_id, 0)["messages"]
    assert len(messages) == 0


########################################################
############ Tests for message_react ###################
########################################################

# message_id is not valid/ message_id is from the wrong channel
def test_message_react_1():
    user = create_mock_user()
    token = user["token"]
    with pytest.raises(ValueError, match=r"message_id is invalid."):
        message_react(token, "invalidmessageid", 1)


# Test when all input is correct
def test_message_react_2():
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    assert message_react(token, message_id, 1) == None


# React_id is invalid
def test_message_react_3():

    user = create_mock_user()
    token = user["token"]

    channel_id = channels_create(token, "Channel 1", False)

    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]

    react_id = "9"

    with pytest.raises(ValueError, match=r"react_id is invalid."):
        message_react(token, message_id, react_id)


def test_message_react_4():
    # Unauthorised user attempting to react/ User not part of channel
    owner = create_mock_user()
    owner_token = owner["token"]
    user = create_mock_user()
    user_token = user["token"]
    channel_id = channels_create(owner_token, "Channel 1", False)
    message_id = message_send(owner_token, channel_id, "How was your day?")[
        "message_id"
    ]
    with pytest.raises(
        ValueError, match=r"Message is not within same channel as user."
    ):
        message_react(user_token, message_id, 1)


def test_message_react_5():
    # User has already reacted to message
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    message_react(token, message_id, 1)
    with pytest.raises(ValueError, match=r"You have already reacted to this message."):
        message_react(token, message_id, 1)


##########################################################
################ Tests for message_unreact ###############
##########################################################


def test_message_unreact_1():
    # message_id is not valid/ message_id is from the wrong channel
    user = create_mock_user()
    token = user["token"]
    with pytest.raises(ValueError, match=r"message_id is invalid."):
        message_unreact(token, "invalidmessageid", 1)


def test_message_unreact_2():
    # Test when all input is correct
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    react_id = 1
    message_react(token, message_id, react_id)
    assert message_unreact(token, message_id, react_id) == None


def test_message_unreact_3():
    # React_id is invalid
    user = create_mock_user()
    token = user["token"]

    channel_id = channels_create(token, "Channel 1", False)

    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]

    react_id = "9"

    with pytest.raises(ValueError, match=r"react_id is invalid."):
        message_unreact(token, message_id, react_id)


def test_message_unreact_4():
    # Unauthorised user attempting to react/ User not part of channel
    owner = create_mock_user()
    owner_token = owner["token"]
    user = create_mock_user()
    user_token = user["token"]
    channel_id = channels_create(owner_token, "Channel 1", False)
    message_id = message_send(owner_token, channel_id, "How was your day?")[
        "message_id"
    ]
    react_id = 1
    message_react(owner_token, message_id, react_id)
    with pytest.raises(
        ValueError, match=r"Message is not within same channel as user."
    ):
        message_unreact(user_token, message_id, react_id)


# Message has not been reacted to yet
def test_message_unreact_5():
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    with pytest.raises(ValueError, match=r"You have not reacted to this message yet."):
        message_unreact(token, message_id, 1)


##########################################################
############## Tests for message_pin #####################
##########################################################


def test_message_pin_invalid():
    # message_id is invalid/ message doesnt exist
    user = create_mock_user()
    token = user["token"]
    with pytest.raises(ValueError, match=r"Message does not exist."):
        message_pin(token, "invalidmessageid")


def test_message_pin_alreadpinned():
    # Message is already pinned
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    message_pin(token, message_id)
    with pytest.raises(ValueError, match=r"Message is already pinned."):
        message_pin(token, message_id)


def test_message_pin_notmember():
    # User is not a member of the channel
    owner = create_mock_user()
    owner_token = owner["token"]
    user = create_mock_user()
    user_token = user["token"]
    channel_id = channels_create(owner_token, "Channel 1", False)
    message_id = message_send(owner_token, channel_id, "How was your day?")[
        "message_id"
    ]
    with pytest.raises(
        AccessError,
        match=r"User is not a member of channel that targeted message is within.",
    ):
        message_pin(user_token, message_id)
        

def test_message_pin_removeduser():
    # User is added to then leaves channel
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)
    
    channel_id = channels_create(token, "Channel 1", False)
    channel_invite(token, channel_id, u_id)
    channel_leave(token2, channel_id)
    
    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    
    with pytest.raises(
        AccessError, match=r"User is not a member of channel that targeted message is within."
    ):
        message_pin(token2, message_id)

########################################################################
################### Tests for message_unpin ############################
########################################################################


def test_message_unpin_invalidmessage():
    # message_id is invalid/ message doesnt exist
    user = create_mock_user()
    token = user["token"]
    with pytest.raises(ValueError, match=r"Message does not exist."):
        message_unpin(token, "invalidid")


def test_message_unpin_unpinnedalready():
    # Message is already unpinned
    user = create_mock_user()
    token = user["token"]
    channel_id = channels_create(token, "Channel 1", False)
    message_id = message_send(token, channel_id, "How was your day?")["message_id"]
    with pytest.raises(ValueError, match=r"Message is already unpinned."):
        message_unpin(token, message_id)


def test_message_unpin_notmember():
    # User is not a member of the channel
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]

    channel_id = channels_create(token, "Channel 1", False)

    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    message_pin(token, message_id)

    with pytest.raises(
        AccessError, match=r"User is not a member of channel that targeted message is within."
    ):
        message_unpin(token2, message_id)
        
        
def test_message_unpin_removeduser():
    # User is added to then leaves channel
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)
    
    channel_id = channels_create(token, "Channel 1", False)
    channel_invite(token, channel_id, u_id)
    channel_leave(token2, channel_id)
    
    message_send(token, channel_id, "How was your day?")
    messageDict = channel_messages(token, channel_id, 0)
    message_id = messageDict["messages"][0]["message_id"]
    message_pin(token, message_id)
    
    with pytest.raises(
        AccessError, match=r"User is not a member of channel that targeted message is within."
    ):
        message_unpin(token2, message_id)
