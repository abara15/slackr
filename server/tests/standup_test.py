import pytest
from ..functions.standup import standup_start, standup_send
from ..functions.channels import channels_create
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from .helpers import create_mock_user, clear_dbs, random_string


@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield


reg_data = {"token": "anytoken", "name": "anyname", "message": "anymessage"}

################################################################################
#   standup_start - For a given channel, start the standup period whereby      #
#                   for the next 15 minutes if someone calls "standup_send"    #
#                   with a message, it is buffered during the 15 minute window #
#                   then at the end of the 15 minute window a message will be  #
#                   added to the message queue in the channel from the user    #
#                   who started the standup.                                   #
################################################################################


def test_standup_start_nonexistant_channel():
    # Test 1 - ValueError when Channel (based on ID) does not exist
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"Channel does not exist."):
        standup_start(user["token"], "doesnotexist", 1)


def test_standup_start_not_member():
    # Test 2 - AccessError when the authorised user is not a member of the channel that the message is with
    user = create_mock_user()
    another_user = create_mock_user()
    channel_id = channels_create(user["token"], "anyname", is_public=True)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        standup_start(another_user["token"], channel_id, 1)


def test_standup_start_empty_strings():
    # Test 3 - ValueError with invalid/empty input
    user = create_mock_user()
    channel_id = ""
    with pytest.raises(ValueError, match=r"Channel does not exist."):
        standup_start(user["token"], channel_id, 1)


# def test_standup_start_valid():
#     # Test 4 - Valid test
#     user = create_mock_user()
#     channel_id = channels_create(user["token"], "anyname", is_public=True)
#     standup_start(user["token"], channel_id, 1)
#     standup_send(user["token"], channel_id, "Test msg.")


# def test_standup_start_already_active():
#     # Test 5 - Standup already active
#     user = create_mock_user()
#     channel_id = channels_create(user["token"], "anyname", is_public=True)
#     standup_start(user["token"], channel_id, 1)
#     with pytest.raises(
#         ValueError, match=r"An active standup is currently running in this channel."
#     ):
#         standup_start(user["token"], channel_id, 1)


################################################################################
#   standup_end - Sending a message to get buffered in the standup queue,      #
#                 assuming a standup is currently active                       #
################################################################################


def test_standup_send_nonexistant_channel():
    # Test 1 - ValueError when channel (based on ID) does not exist
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"Channel does not exist."):
        standup_send(user["token"], "doesnotexist", "anymessage")


# def test_standup_send_long_message():
#     # Test 2 - ValueError when message is more than 1000 characters
#     user = create_mock_user()
#     channel_id = channels_create(user["token"], "anyname", is_public=True)
#     with pytest.raises(ValueError, match=r"Message is more than 1000 characters."):
#         standup_send(user["token"], channel_id, random_string(1001))


def test_standup_send_not_member():
    # Test 3 - AccessError when the authorised user is not a member of the channel that the message is within
    user = create_mock_user()
    another = create_mock_user()
    channel_id = channels_create(user["token"], "anyname", is_public=True)
    with pytest.raises(
        AccessError, match=r"The authorised user is not a member of the channel."
    ):
        standup_send(another["token"], channel_id, "anymessage")


def test_standup_send_no_stand_up():
    # Test 4 - AccessError when if the standup time has stopped
    user = create_mock_user()
    channel_id = channels_create(user["token"], "anyname", is_public=True)
    with pytest.raises(
        ValueError, match=r"An active standup is not currently running in this channel."
    ):
        standup_send(user["token"], channel_id, reg_data["message"])


# def test_standup_send_valid():
#     # Test 6 - Valid test
#     user = create_mock_user()
#     channel_id = channels_create(user['token'], 'anyname', is_public=True)
#     standup_start(user['token'], channel_id)
#     standup_send(user['token'], channel_id, 'anymessasge')
#     standup_send(user['token'], channel_id, 'anothermessage')
