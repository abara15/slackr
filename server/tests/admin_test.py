import pytest
from ..functions.admin import admin_userpermission_change
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError
from .helpers import create_mock_user, clear_dbs


@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield


################################################################################
#   admin_userpermission_change - Given a User by their user ID, set           #
#                                 their permissions to new permissions         #
#                                 described by permission_id                   #
################################################################################


def test_admin_userpermission_change_invalid_user_id():
    # Test 1 - ValueError when u_id does not refer to a valid user
    user = create_mock_user()
    with pytest.raises(ValueError, match=r"u_id does not refer to a valid user."):
        admin_userpermission_change(user["token"], "invalid", 1)


def test_admin_userpermission_change_invalid_permission_id():
    # Test 2 - ValueError when permission_id does not refer to a value permission
    user = create_mock_user()
    permission_id = "invalidpermissionid"
    with pytest.raises(
        ValueError, match=r"permission_id does not refer to a value permission."
    ):
        admin_userpermission_change(user["token"], user["u_id"], permission_id)


def test_admin_userpermission_change_not_admin_owner():
    # Test 3 - AccessError when the authorised user is not an admin or owner
    create_mock_user()  # Because first user is an owner.
    member = create_mock_user()
    another_member = create_mock_user()
    u_id = another_member["u_id"]
    with pytest.raises(
        AccessError, match=r"The authorised user is not an admin or owner."
    ):
        admin_userpermission_change(member["token"], u_id, 2)


def test_admin_userpermission_invalid_owner_change():
    # Test 4 - AccessError when an admin trys to change an owner permission
    owner = create_mock_user()
    admin = create_mock_user()
    admin_userpermission_change(owner["token"], admin["u_id"], 2)
    with pytest.raises(
        AccessError,
        match=r"Admins/members cannot change owner permissions or make other users owners.",
    ):
        admin_userpermission_change(admin["token"], owner["u_id"], 2)


def test_admin_userpermission_change_valid():
    # Test 5 - Valid test
    owner = create_mock_user()
    member = create_mock_user()
    assert admin_userpermission_change(owner["token"], member["u_id"], 2) is None
