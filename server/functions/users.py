from ..db import users, get_user_profile
from .auth import get_id_from_token, valid_email
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError

# for uploadPhoto
from PIL import Image
import requests
from io import BytesIO


def len_error(variable, min, max, property="This"):
    if len(variable) < min or len(variable) > max:
        raise ValueError(f"{property} should be between {min} and {max} characters.")


def len_error_check(variable, error_check):
    if len(error_check) != 0:
        raise ValueError(f"'{variable}' is already in use.")


def user_profile(token, u_id):
    """
    For a valid user, returns information about their email, first name, last name, and handle
    Args: 
        token
        u_id     
    Returns:
        { email, name_first, name_last, handle_str }   
    Raises:
        ValueError when: User with u_id is not a valid user
    """
    get_id_from_token(token)
    user = users.get(u_id)
    print(users.get(u_id))

    if user is None:
        raise ValueError("u_id does not exist.")

    return get_user_profile(u_id)


def user_profile_setname(token, name_first, name_last):
    """
    Update the authorised user's first and last name
    Args: 
        token, name_first, name_last    
    Returns:
        {}   
    Raises:
        ValueError when: name_first is not between 1 and 50 characters in length
        ValueError when: name_last is not between 1 and 50 characters in length
    """

    u_id = get_id_from_token(token)  # Decode token for the u_id

    # Error Raises
    len_error(name_first, 1, 50, "First Name")
    len_error(name_last, 1, 50, "Last Name")

    users.set(u_id, "first_name", name_first)  # Update name_first if no error
    users.set(u_id, "last_name", name_last)  # Update name_last if no error


def user_profile_setemail(token, email):
    """
    Update the authorised user's email address
    Args: 
        token, email
    Returns:
        {}   
    Raises:
        ValueError when: Email entered is not a valid email.
        ValueError when: Email address is already being used by another user.
    """

    u_id = get_id_from_token(token)  # Decode token for the u_id

    error_check_valid = valid_email(
        email
    )  # Checks validity of email. True if valid, False if invalid
    error_check_in_use = users.query(
        "email", "==", email
    )  # Searches if email is already in use

    # Error Raises
    len_error_check(email, error_check_in_use)
    if error_check_valid is False:
        raise ValueError("Email is not valid.")

    users.set(u_id, "email", email)  # Update email if no error


def user_profile_sethandle(token, handle_str):
    """
    Update the authorised user's handle (i.e. display name)
    Args: 
        token, handle_str
    Returns:
        {}   
    Raises:
        ValueError when: handle_str must be between 3 and 20 characters.
        ValueError when: handle is already used by another user.
    """

    u_id = get_id_from_token(token)  # Decode token for the u_id

    error_check_in_use = users.query(
        "handle_str", "==", handle_str
    )  # Searches if handle is already in use

    # Error Raises
    len_error(handle_str, 3, 20, "Handle")
    len_error_check(handle_str, error_check_in_use)

    users.set(u_id, "handle_str", handle_str)  # Update handle if no error


def user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """
    Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
    Args: 
        token, img_url, x_start, y_start, x_end, y_end
    Returns:
        {}   
    Raises:
        ValueError when: img_url is returns an HTTP status other than 200.
        ValueError when: any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.
    """
    u_id = get_id_from_token(token)  # Decode token for the u_id
    response = requests.get(img_url)  # Load image from URL

    if response.status_code != 200:
        raise ValueError("Image URL returned a HTTP status other than 200.")

    image = Image.open(BytesIO(response.content))  # Read image from URL if no error
    width, height = image.size  # Get image size

    if (x_start < 0) or (y_start < 0) or (x_end > width) or (y_end > height):
        raise ValueError(
            "The new dimensions are not within the bounds of the image at the URL."
        )

    img_cropped = image.crop((x_start, y_start, x_end, y_end))  # Crop if no error

    filename = f"{u_id}.jpg"
    save_path = f"./frontend/prebundle/imgs/{filename}"
    img_cropped.save(save_path, "JPEG")  # Save cropped image to imgs folder

    users.set(u_id, "img_url", f"/imgs/{filename}")  # Update img_url

    return {}


def users_all(token):
    """
    Gets a list of all users on slackr.
    Returns:
        { users: []}
    Raises:
        AccessError: When token is invalid.
    """
    get_id_from_token(token)
    all_users = users.list()
    returned_users = []
    for user in all_users:
        returned_users.append(get_user_profile(user["u_id"]))
    return {"users": returned_users}
