import pytest
from ..functions.auth import (
    auth_login,
    auth_logout,
    auth_register,
    auth_passwordreset_request,
    auth_passwordreset_reset,
    valid_token,
    generate_password_reset_code,
)
from .helpers import create_mock_user, clear_dbs
from ..errors.ValueError import ValueError


@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield


######################################
##         auth_login Tests         ##
######################################


def test_auth_login_invalid_email():
    # An invalid email with any password
    with pytest.raises(ValueError, match=r"Email entered is not a valid email."):
        auth_login("invalidemail", "anypassword")


def test_auth_login_unregistered_email():
    # A valid, unregistered email with any password
    with pytest.raises(ValueError, match=r"Email entered does not belong to a user."):
        assert auth_login("unregistered@example.com", "anypassword")


def test_auth_login_incorrect_password():
    # A valid, registered email with an incorrect password
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"Password is not correct."):
        assert auth_login(user["email"], "incorrectpassword")


def test_auth_login_valid_login():
    # A valid, registered email with the correct password
    user = create_mock_user()
    cred = auth_login(user["email"], user["password"])
    assert "u_id" in cred and "token" in cred
    assert cred["u_id"] and cred["token"]


######################################
##        auth_logout Tests         ##
######################################


def test_auth_logout_valid_token():
    # A valid token to invalidate
    token = create_mock_user()["token"]
    auth_logout(token)
    assert valid_token(token) is False


def test_auth_logout_invalid_token():
    # An invalid token, should do nothing
    assert auth_logout("random_invalid_token") is None


######################################
##       auth_register Tests        ##
######################################


reg_data = {
    "email": "john@example.com",
    "password": "strongPassword@24",
    "name_first": "John",
    "name_last": "Doe",
}


def test_auth_register_valid_params():
    # All valid params
    cred = auth_register(
        reg_data["email"],
        reg_data["password"],
        reg_data["name_first"],
        reg_data["name_last"],
    )
    assert "u_id" in cred and "token" in cred
    assert cred["u_id"] and cred["token"]


def test_auth_register_long_first_name():
    # A first name longer than 50 chars
    long_first_name = "aweifjlaowiekjawnlejkcnwuklfnal2i3ufhalwydcadienlfawi"
    with pytest.raises(ValueError, match=r"name_first is more than 50 characters."):
        auth_register(
            reg_data["email"],
            reg_data["password"],
            long_first_name,
            reg_data["name_last"],
        )


def test_auth_register_long_last_name():
    # A last name longer than 50 chars
    long_last_name = "aweifjlaowiekjawnlejkcnwuklfnal2i3ufhalwydcadienlfawi"
    with pytest.raises(ValueError, match=r"name_last is more than 50 characters."):
        auth_register(
            reg_data["email"],
            reg_data["password"],
            reg_data["name_first"],
            long_last_name,
        )


def test_auth_register_invalid_email():
    # An invalie email address
    invalid_email = "john.example"
    with pytest.raises(ValueError, match=r"Email entered is not a valid email."):
        auth_register(
            invalid_email,
            reg_data["password"],
            reg_data["name_first"],
            reg_data["name_last"],
        )


def test_auth_register_alreadyregistered_email():
    # A email address belonging to another user
    user = create_mock_user()
    with pytest.raises(
        ValueError, match=r"Email is already being used by another user."
    ):
        auth_register(
            user["email"],
            reg_data["password"],
            reg_data["name_first"],
            reg_data["name_last"],
        )


def test_auth_register_invalid_password():
    # An invalid password
    invalid_password = "weak"
    with pytest.raises(ValueError, match=r"Password entered is not a valid password."):
        auth_register(
            reg_data["email"],
            invalid_password,
            reg_data["name_first"],
            reg_data["name_last"],
        )


#########################################
##  auth_passwordreset_request Tests   ##
#########################################


def test_auth_passwordreset_request_invalid_email():
    # An invalid email address, should throw ValueError
    with pytest.raises(ValueError, match=r"Email entered is not a valid email."):
        auth_passwordreset_request("invalid.com")


def test_auth_passwordreset_request_unregistered_email():
    # A valid, non-registered email address, should throw ValueError
    with pytest.raises(ValueError, match=r"Email entered does not belong to a user."):
        auth_passwordreset_request("mic@example.com")


def test_auth_passwordreset_request_valid_email():
    # A valid, registered email address
    user = create_mock_user()
    assert auth_passwordreset_request(user["email"]) is None


#########################################
##   auth_passwordreset_reset Tests    ##
#########################################


def test_auth_passwordreset_reset_invalid_code():
    # An invalid reset_code with a valid email
    with pytest.raises(ValueError, match=r"reset_code is not a valid reset code."):
        auth_passwordreset_reset("invalidcode", "strongPassword@24")


def test_auth_passwordreset_reset_invalid_password():
    # An invalid password with a valid reset code
    user = create_mock_user()
    reset_code = generate_password_reset_code(user["email"])
    with pytest.raises(ValueError, match=r"Password entered is not a valid password."):
        auth_passwordreset_reset(reset_code, "weak")


def test_auth_passwordreset_reset_valid():
    # A valid password and reset code
    user = create_mock_user()
    email = user["email"]
    reset_code = generate_password_reset_code(email)
    new_password = "newPassword@24"
    auth_passwordreset_reset(reset_code, new_password)
    cred = auth_login(email, new_password)
    assert "u_id" in cred and "token" in cred
    assert cred["u_id"] == user["u_id"]
    assert cred["u_id"] and cred["token"]

