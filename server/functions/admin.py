from ..db import users
from .auth import get_id_from_token
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError


def admin_userpermission_change(token, u_id, permission_id):
    """
    Given a User by their user ID, set their permissions to new permissions
    described by permission_id.

    Returns:
        {}

    Raises:
        ValueError: u_id does not refer to a valid user.
        ValueError: permission_id does not refer to a value permission.
        AccessError: The authorised user is not an admin or owner.
    """
    auth_u_id = get_id_from_token(token)
    calling_user = users.get(auth_u_id)
    user_to_change = users.get(u_id)

    # Error Raises
    if user_to_change is None:
        raise ValueError("u_id does not refer to a valid user.")
    if permission_id not in [1, 2, 3]:
        raise ValueError("permission_id does not refer to a value permission.")
    if calling_user["is_admin"] is False and calling_user["is_slackr_owner"] is False:
        raise AccessError("The authorised user is not an admin or owner.")
    if (
        user_to_change["is_slackr_owner"] is True or permission_id == 1
    ) and calling_user["is_slackr_owner"] is False:
        raise AccessError(
            "Admins/members cannot change owner permissions or make other users owners."
        )

    # Actual functions
    if permission_id == 1:
        users.set(u_id, "is_slackr_owner", True)
        users.set(u_id, "is_admin", False)
    elif permission_id == 2:
        users.set(u_id, "is_slackr_owner", False)
        users.set(u_id, "is_admin", True)
    elif permission_id == 3:
        users.set(u_id, "is_slackr_owner", False)
        users.set(u_id, "is_admin", False)
