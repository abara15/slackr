import pytest
from ..functions.channels import (
    channel_invite,
    channel_details,
    channel_messages,
    channels_create,
    channel_leave,
    channel_join,
    channel_addowner,
    channel_removeowner,
    channels_list,
    channels_listall,
)
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from .helpers import create_mock_user, generate_messages, clear_dbs

from ..functions.auth import get_id_from_token

@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield


######################################
##       channel_invite Tests       ##
######################################


def test_channel_invite_unathorized_private():
    # User not authorized on specified channel (private channel).
    inviting_user = create_mock_user()
    another_user = create_mock_user()
    user_being_invited = create_mock_user()
    channel_id = channels_create(another_user["token"], "channelName", is_public=False)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        channel_invite(inviting_user["token"], channel_id, user_being_invited["u_id"])


def test_channel_invite_unathorized_public():
    # User not authorized on specified channel (public channel).
    inviting_user = create_mock_user()
    another_user = create_mock_user()
    user_being_invited = create_mock_user()
    channel_id = channels_create(another_user["token"], "channelName", is_public=True)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        channel_invite(inviting_user["token"], channel_id, user_being_invited["u_id"])


def test_channel_invite_invalid_u_id():
    # u_id does not refer to a valid user to be invited.
    inviting_user = create_mock_user()
    channel_id = channels_create(inviting_user["token"], "channelName", is_public=False)
    with pytest.raises(ValueError, match=r"u_id does not exist."):
        channel_invite(inviting_user["token"], channel_id, "invaliduserid")


def test_channel_invite_valid():
    # Valid invite operation.
    inviting_user = create_mock_user()
    user_being_invited = create_mock_user()
    channel_id = channels_create(inviting_user["token"], "channelName", False)
    channel_invite(inviting_user["token"], channel_id, user_being_invited["u_id"])
    details = channel_details(inviting_user["token"], channel_id)
    assert "all_members" in details and len(details["all_members"]) == 2
    assert any(
        member["u_id"] == user_being_invited["u_id"]
        for member in details["all_members"]
    )


######################################
##       channel_details Tests      ##
######################################


def test_channel_details_invalid_ch_id():
    # A non-existant channel id
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"channel_id does not exist."):
        channel_details(user["token"], "invalidchannelid")


def test_channel_details_unathorized_public():
    # Authorized user not a member of a public channel
    owner = create_mock_user()
    another_user = create_mock_user()
    channel_id = channels_create(owner["token"], "channelname", is_public=True)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        channel_details(another_user["token"], channel_id)


def test_channel_details_unathorized_private():
    # Authorized user not a member of a private channel
    owner = create_mock_user()
    another_user = create_mock_user()
    channel_id = channels_create(owner["token"], "channelname", is_public=False)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        channel_details(another_user["token"], channel_id)


def test_channel_details_valid():
    # A valid operation
    user = create_mock_user()
    channel_name = "channelName"
    channel_id = channels_create(user["token"], channel_name, is_public=True)
    details = channel_details(user["token"], channel_id)
    assert "name" in details and "all_members" in details and "owner_members" in details
    assert details["name"] == channel_name
    assert details["all_members"][0]["u_id"] == user["u_id"]
    assert details["owner_members"][0]["u_id"] == user["u_id"]


######################################
##      channel_messages Tests      ##
######################################


def setup_messages_test(number_of_messages=0):
    user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=False)
    generate_messages(user["token"], channel_id, number_of_messages)
    return (user, channel_id)


def test_channel_messages_invalid_start():
    # An invalid value for start (-ve value, for example)
    user, channel_id = setup_messages_test()
    with pytest.raises(ValueError, match=r"Invalid value for start."):
        channel_messages(user["token"], channel_id, start=-51)


def test_channel_messages_start_too_large():
    # A start value that is greater than the number of messages
    user, channel_id = setup_messages_test(number_of_messages=30)
    with pytest.raises(
        ValueError,
        match=r"start is greater than the total number of messages in the channel.",
    ):
        channel_messages(user["token"], channel_id, start=40)


def test_channel_messages_does_not_exist():
    # A channel_id that does not exist
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"channel_id does not exist."):
        channel_messages(user["token"], "invalidchannelid")


def test_channel_messages_unathorized_user_public():
    # A user auth token belonging to a valid user that is not part of a public channel
    user = create_mock_user()
    another_user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=True)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        channel_messages(another_user["token"], channel_id)


def test_channel_messages_unathorized_user_private():
    # A user auth token belonging to a valid user that is not part of a private channel
    user = create_mock_user()
    another_user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=False)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        channel_messages(another_user["token"], channel_id)


def test_channel_messages_get_empty():
    # A channel with no messages, should return empty messages list
    user, channel_id = setup_messages_test()
    result = channel_messages(user["token"], channel_id)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) == 0
    assert result["start"] == 0 and result["end"] == -1


def test_channel_messages_response_structure():
    # A channel with 20 messages and no start - to test return structre of messages list of dicts
    user, channel_id = setup_messages_test(number_of_messages=20)
    result = channel_messages(user["token"], channel_id)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) >= 1
    sample_msg = result["messages"][0]
    response_attributes = ["message_id", "u_id", "time_created", "message", "reacts"]
    assert all(attribute in sample_msg for attribute in response_attributes)


def test_channel_messages_get_some_no_start():
    # A channel with more than 50 messages and no start
    user, channel_id = setup_messages_test(number_of_messages=60)
    result = channel_messages(user["token"], channel_id)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) == 50
    assert result["start"] == 0 and result["end"] == 50


def test_channel_messages_get_some_with_start():
    # A channel with more than 50 messages and a specific, valid start
    user, channel_id = setup_messages_test(number_of_messages=60)
    result = channel_messages(user["token"], channel_id, start=5)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) == 50
    assert result["start"] == 5 and result["end"] == 55


def test_channel_messages_get_all_no_start():
    # A channel with less than 50 messages and no start
    user, channel_id = setup_messages_test(number_of_messages=40)
    result = channel_messages(user["token"], channel_id)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) == 40
    assert result["start"] == 0 and result["end"] == -1


def test_channel_messages_get_all_with_start():
    # A channel with less than 50 messages and a specific, valid start
    user, channel_id = setup_messages_test(number_of_messages=40)
    result = channel_messages(user["token"], channel_id, start=20)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) == 20
    assert result["start"] == 20 and result["end"] == -1


def test_channel_messages_get_all_exactly_50():
    # A channel with exactly 50 messages and no start
    user, channel_id = setup_messages_test(number_of_messages=50)
    result = channel_messages(user["token"], channel_id)
    assert "messages" in result and "start" in result and "end" in result
    assert len(result["messages"]) == 50
    assert result["start"] == 0 and result["end"] == -1


####################################################
###### Tests for channel_leave #####################
####################################################


def test_channel_leave_invalid():
    user = create_mock_user()
    try:
        # try and leave invalid channel should raise error
        channel_leave(user["token"], "123456789")
        assert 0
    except ValueError:
        pass


def test_channel_leave():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=False)
    channel_leave(user["token"], channel_id)
    try:
        channel_details(user["token"], channel_id)  # should raise AccessError
        assert 0
    except AccessError:
        pass

def test_channel_leave_twice():
    user = create_mock_user()
    token = user["token"]
    user2 = create_mock_user()
    token2 = user2["token"]
    u_id = get_id_from_token(token2)
    
    channel_id = channels_create(token, "Channel 1", False)
    channel_invite(token, channel_id, u_id)
    channel_leave(token2, channel_id)
    
    with pytest.raises(
        AccessError, match=r"Authorised user is not a member of the channel."
    ):
        channel_leave(token2, channel_id)
    

############################################################
############## Tests for channel_join ######################
############################################################


def test_channel_join_public():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=True)
    channel_leave(user["token"], channel_id)  # channel_leave must be completed
    channel_join(user["token"], channel_id)
    channel_data = channel_details(user["token"], channel_id)
    assert any(user["u_id"] == member["u_id"] for member in channel_data["all_members"])


def test_channel_join_private():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=False)
    channel_leave(user["token"], channel_id)  # channel_leave must be completed
    try:
        channel_join(user["token"], channel_id)  # should raise AccessError
        assert 0
    except AccessError:
        pass


def test_channel_join_invalid():
    user = create_mock_user()
    try:
        # try and join invalid channel should raise error
        channel_join(user["token"], "123456789")
        assert 0
    except ValueError:
        pass


##################################################
############# Tests for channel_addowner #########
##################################################


def test_channel_addowner_already_owner():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=True)
    try:
        channel_addowner(user["token"], channel_id, user["u_id"])  # should except
        assert 0
    except ValueError:
        pass


def test_channel_addowner_no_channel():
    user = create_mock_user()
    try:
        # channel doesnt exist should raise value error
        channel_addowner(user["token"], "123456789", user["u_id"])
        assert 0
    except ValueError:
        pass


def test_channel_addowner_access_error():
    # try to add an owner without having the authority
    owner = create_mock_user()
    user = create_mock_user()
    candidate = create_mock_user()
    channel_id = channels_create(owner["token"], "channelName", is_public=True)
    channel_join(user["token"], channel_id)
    channel_join(candidate["token"], channel_id)
    try:
        # try and add an owner should fail
        channel_addowner(user["token"], channel_id, candidate["u_id"])
    except AccessError:
        pass


def test_channel_addowner():
    owner = create_mock_user()
    user = create_mock_user()
    channel_id = channels_create(owner["token"], "channelName", is_public=True)
    channel_join(user["token"], channel_id)
    channel_addowner(owner["token"], channel_id, user["u_id"])
    channel_data = channel_details(owner["token"], channel_id)
    assert any(
        user["u_id"] == member["u_id"] for member in channel_data["owner_members"]
    )


############################################
######### Tests for channel_removeowner ####
############################################


def test_channel_removeowner_no_channel():
    user = create_mock_user()
    try:
        # try to remove from invalid channel id
        channel_removeowner(user["token"], "123456789", user["u_id"])
        assert 0
    except ValueError:
        pass


def test_channel_removeowner_not_owner():
    owner = create_mock_user()
    user = create_mock_user()
    channel_id = channels_create(owner["token"], "channelName", is_public=True)
    channel_join(user["token"], channel_id)
    try:
        # trying to remove someone who isnt an owner
        channel_removeowner(owner["token"], channel_id, user["u_id"])
        assert 0
    except ValueError:
        pass


def test_channel_removeowner_access_error():
    owner = create_mock_user()
    user = create_mock_user()
    channel_id = channels_create(owner["token"], "channelName", is_public=True)
    channel_join(user["token"], channel_id)
    try:
        # try and remove owner without permission
        channel_removeowner(user["token"], channel_id, owner["u_id"])
    except AccessError:
        pass


def test_channel_removeowner():
    owner = create_mock_user()
    user = create_mock_user()
    candidate = create_mock_user()
    channel_id = channels_create(owner["token"], "channelName", is_public=True)
    channel_join(user["token"], channel_id)
    channel_join(candidate["token"], channel_id)
    # channel_addowner must be implemented
    channel_addowner(owner["token"], channel_id, candidate["u_id"])
    channel_removeowner(owner["token"], channel_id, candidate["u_id"])
    data = channel_details(owner["token"], channel_id)
    assert candidate["u_id"] not in data["owner_members"]


#############################################
######### Tests for channels_list ###########
#############################################

def test_channels_list_empty():
    user = create_mock_user()
    assert channels_list(user["token"]) == {"channels": []}


def test_channels_list_in_all():
    user = create_mock_user()
    channel_one = channels_create(user["token"], "channelOne", is_public=True)
    channel_two = channels_create(user["token"], "channelTwo", is_public=True)
    assert channels_list(user["token"]) == {
        "channels": [
            {"name": "channelOne", "channel_id": channel_one,},
            {"name": "channelTwo", "channel_id": channel_two},
        ]
    }


def test_channels_list_in_some():
    userOne = create_mock_user()
    userTwo = create_mock_user()
    channel_one = channels_create(userOne["token"], "channelOne", is_public=True)
    channels_create(userTwo["token"], "channelTwo", is_public=True)
    assert channels_list(userOne["token"]) == {
        "channels": [{"name": "channelOne", "channel_id": channel_one,}]
    }

#############################################
######### Tests for channels_listall ########
#############################################

def test_channels_listall_empty():
    user = create_mock_user()
    assert channels_listall(user["token"]) == {"channels": []}


def test_channels_listall_channels():
    user = create_mock_user()
    channel_one = channels_create(user["token"], "channelOne", is_public=True)
    channel_two = channels_create(user["token"], "channelTwo", is_public=True)
    assert channels_list(user["token"]) == {
        "channels": [
            {"name": "channelOne", "channel_id": channel_one,},
            {"name": "channelTwo", "channel_id": channel_two},
        ]
    }


#############################################
######### Tests for channels_create ###########
#############################################

def test_channels_create_longName():
    user = create_mock_user()
    try:
        channels_create(user["token"], "VeryLongChannelNameForError", is_public=True)
        assert 0
    except ValueError:
        pass


def test_channels_create():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "channelName", is_public=True)
    # should fail if channel doesnt exist
    channel_details(user["token"], channel_id)

