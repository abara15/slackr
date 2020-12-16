import pytest
from ..functions.auth import auth_register
from ..functions.users import (
    user_profile,
    user_profile_setname,
    user_profile_setemail,
    user_profile_sethandle,
    user_profiles_uploadphoto,
    users_all,
)
from .helpers import create_mock_user, clear_dbs
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from ..db import users


@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield


reg_data = {
    "img_url": "anyurl",
    "x_start": "anyxstart",
    "y_start": "anyystart",
    "x_end": "anyxend",
    "y_end": "anyyend",
}

################################################################################
#   user_profile - for a valid user, returns information about their email,    #
#                  first name, last name and handle                            #
################################################################################


def test_user_profile_valid():
    # Test if user exists / Correct info used
    user = create_mock_user()
    token = user["token"]
    u_id = user["u_id"]
    assert user_profile(token, u_id) == {
        "email": user["email"],
        "name_first": user["name_first"],
        "name_last": user["name_last"],
        "handle_str": user["name_first"] + user["name_last"],
        "profile_img_url": user["img_url"],
    }


def test_user_profile_handlechanged():
    # Test that user can sethandle and return correct info
    user = create_mock_user()
    token = user["token"]
    u_id = user["u_id"]
    user["handle_str"] = "BigDaddy"

    user_profile_sethandle(token, "BigDaddy")

    assert user_profile(token, u_id) == {
        "email": user["email"],
        "name_first": user["name_first"],
        "name_last": user["name_last"],
        "handle_str": user["handle_str"],
        "profile_img_url": user["img_url"],
    }


def test_user_profile_invald_token():
    # Test when user uses invalid token
    user = create_mock_user()
    with pytest.raises(AccessError, match=r"Invalid token."):
        user_profile("invalidtoken", user["u_id"])


def test_user_profile_invald_uid():
    # Test when u_id does not exist
    user = create_mock_user()
    token = user["token"]
    with pytest.raises(ValueError, match=r"u_id does not exist."):
        user_profile(token, "invaliduid")


################################################################################
#   user_profile_setname - update the authorised user's first and last name    #
################################################################################


def test_user_profile_setname_long_first_name():
    # Test 1 - ValueError when name_first is more than 50 characters
    user = create_mock_user()
    name_first = "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiop"
    with pytest.raises(
        ValueError, match=r"First Name should be between 1 and 50 characters."
    ):
        user_profile_setname(user["token"], name_first, user["name_last"])


def test_user_profile_setname_long_last_name():
    # Test 2 - ValueError when name_last is more than 50 characters
    user = create_mock_user()
    name_last = "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiop"
    with pytest.raises(
        ValueError, match=r"Last Name should be between 1 and 50 characters."
    ):
        user_profile_setname(user["token"], user["name_first"], name_last)


def test_user_profile_setname_empty_strings():
    # Test 3 - ValueError with invalid/empty input
    user = create_mock_user()
    name_last = ""
    with pytest.raises(
        ValueError, match=r"Last Name should be between 1 and 50 characters."
    ):
        user_profile_setname(user["token"], user["name_first"], name_last)


def test_user_profile_setname_valid():
    # Test 4 - Valid test
    user = create_mock_user()
    token = user["token"]
    u_id = user["u_id"]
    new_name_first = "new_first"
    new_name_last = "new_last"
    user_profile_setname(token, new_name_first, new_name_last)
    profile = user_profile(token, u_id)
    assert (
        profile["name_first"] is new_name_first
        and profile["name_last"] is new_name_last
    )


################################################################################
#      user_profile_setemail - update the authorised user's email address      #
################################################################################


def test_user_profile_setemail_invalid_email():
    # Test 1 - ValueError when Email entered is not a valid email.
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"Email is not valid."):
        user_profile_setemail(user["token"], "invalidemail")


def test_user_profile_setemail_email_in_use():
    # Test 2 - ValueError when email address is already being used by another user
    user = create_mock_user()
    another_user = create_mock_user()
    with pytest.raises(ValueError, match=r"is already in use."):
        user_profile_setemail(user["token"], another_user["email"])


def test_user_profile_setemail_empty_string():
    # Test 3 - ValueError with invalid/empty input
    user = create_mock_user()
    email = ""
    with pytest.raises(ValueError, match=r"Email is not valid."):
        user_profile_setemail(user["token"], email)


def test_user_profile_setemail_valid():
    # Test 4 - Valid test
    user = create_mock_user()
    new_email = "john@example.com"
    user_profile_setemail(user["token"], new_email)
    profile = user_profile(user["token"], user["u_id"])
    assert profile["email"] is new_email


################################################################################
#      user_profile_sethandle - update the authorised user's handle            #
################################################################################


def test_user_profile_sethandle_length():
    # Test 1 - ValueError when handle_str is no more than 20 characters
    user = create_mock_user()
    handle_str = "qwertyuiopasdfghjklzxcvbnm_sdfghjk"
    with pytest.raises(
        ValueError, match=r"Handle should be between 3 and 20 characters."
    ):
        user_profile_sethandle(user["token"], handle_str)


def test_user_profile_sethandle_empty_string():
    # Test 2 - ValueError with invalid/empty input
    user = create_mock_user()
    handle_str = ""
    with pytest.raises(
        ValueError, match=r"Handle should be between 3 and 20 characters."
    ):
        user_profile_sethandle(user["token"], handle_str)


def test_user_profile_sethandle_valid():
    # Test 3 - Valid test
    user = create_mock_user()
    new_handle = "newhandle"
    user_profile_sethandle(user["token"], new_handle)
    profile = user_profile(user["token"], user["u_id"])
    assert profile["handle_str"] is new_handle


################################################################################
#      user_profiles_uploadphoto - Given a URL of an image on the internet,     #
#                                 crops the image within bounds (x_start,      #
#                                 y_start) and (x_end, y_end). Position        #
#                                 (0,0) is the top left.                       #
################################################################################


# def test_user_profiles_uploadphoto_http_status():
#     # Test 1 - ValueError when img_url is returns an HTTP status other than 200.
#     user = create_mock_user()
#     img_url = "http://imaginaryurl.com"
#     with pytest.raises(ValueError, match=r"URL and dimensions entered are invalid."):
#         user_profiles_uploadphoto(
#             user["token"],
#             img_url,
#             reg_data["x_start"],
#             reg_data["y_start"],
#             reg_data["x_end"],
#             reg_data["y_end"],
#         )


# def test_user_profiles_uploadphoto_within_dimensions():
#     # Test 2 - ValueError when x_start, y_start, x_end, y_end are all within the dimensions of the image at the URL.
#     user = create_mock_user()
#     x_start = "-5"
#     y_start = "4"
#     x_end = "25"
#     y_end = "10"
#     with pytest.raises(ValueError, match=r"URL and dimensions entered are invalid."):
#         user_profiles_uploadphoto(
#             user["token"], reg_data["img_url"], x_start, y_start, x_end, y_end
#         )


# def test_user_profiles_uploadphoto_empty_string():
#     # Test 3 - ValueError with invalid/empty input
#     user = create_mock_user()
#     img_url = ""
#     x_start = ""
#     y_start = ""
#     x_end = ""
#     y_end = ""
#     with pytest.raises(ValueError, match=r"URL and dimensions entered are invalid."):
#         user_profiles_uploadphoto(
#             user["token"], img_url, x_start, y_start, x_end, y_end
#         )


# def test_user_profiles_uploadphoto_valid():
#     # Test 4 - Valid test
#     user = create_mock_user()
#     assert (
#         user_profiles_uploadphoto(
#             user["token"],
#             reg_data["img_url"],
#             reg_data["x_start"],
#             reg_data["y_start"],
#             reg_data["x_end"],
#             reg_data["y_end"],
#         )
#         is None
#     )


##############################################
#              users_all                     #
##############################################


def test_users_all():
    first_user = create_mock_user()
    r1 = users_all(first_user["token"])["users"]
    assert len(r1) == 1
    second_user = create_mock_user()
    r2 = users_all(second_user["token"])["users"]
    assert len(r2) == 2

