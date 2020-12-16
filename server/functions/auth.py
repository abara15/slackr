import re
import jwt
import hashlib
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from ..tests.random_gen import random_string
from ..db import users
from ..errors.AccessError import AccessError
from ..errors.ValueError import ValueError

SERVER_SECRET = "B462F8C92A7605A4674285214059CB6FDA3546D274BA2AE45BFCFD4CC986E263"
TOKEN_EXPIRY_IN_DAYS = 30
blacklist_tokens = []


def auth_login(email, password):
    """
      Given a registered users' email and password and generates a valid token
      for the user to remain authenticated.

      Returns:
          { u_id, token }

      Raises:
          ValueError: Email entered is not a valid email.
          ValueError: Email entered does not belong to a user.
          ValueError: Password is not correct.
    """
    if not valid_email(email):
        raise ValueError("Email entered is not a valid email.")
    results = users.query("email", "==", email)
    if len(results) == 0:
        raise ValueError("Email entered does not belong to a user.")
    user = results[0]
    attempt_pass_hash = hash(password)
    if attempt_pass_hash != user["password_hash"]:
        raise ValueError("Password is not correct.")
    payload = {"u_id": user["u_id"]}
    token = jwt_encode(payload)
    return {"u_id": user["u_id"], "token": token}


def auth_logout(token):
    """
      Given an active token, invalidates the token to log the user out.
      If the token is not valid, does nothing.
    """
    if token in blacklist_tokens or not valid_token(token):
        return
    blacklist_tokens.append(token)


def auth_register(email, password, name_first, name_last):
    """
      Given a user's first and last name, email address, and password, create a
      new account for them and return a new token for authentication in
      their session.

      Returns:
          { u_id, token }

      Raises:
          ValueError: Email entered is not a valid email.
          ValueError: Email is already being used by another user.
          ValueError: Password entered is not a valid password.
          ValueError: name_first is more than 50 characters.
          ValueError: name_last is more than 50 characters.
    """
    if not valid_email(email):
        raise ValueError("Email entered is not a valid email.")
    if not len(name_first) <= 50:
        raise ValueError("name_first is more than 50 characters.")
    if not len(name_last) <= 50:
        raise ValueError("name_last is more than 50 characters.")
    if not valid_password(password):
        raise ValueError("Password entered is not a valid password.")
    results = users.query("email", "==", email)
    if len(results) != 0:
        raise ValueError("Email is already being used by another user.")
    user_payload = {
        "email": email,
        "handle_str": name_first + name_last,
        "password_hash": hash(password),
        "first_name": name_first,
        "last_name": name_last,
        "img_url": None,
        "is_admin": False,
        "is_slackr_owner": True if users.size() == 0 else False,
        "reset_codes": [],
    }
    users.add(user_payload)
    return auth_login(email, password)


def auth_passwordreset_request(email):
    """
      Given an email address, if the user is a registered user, send's them a
      an email containing a specific secret code, that when entered in
      auth_passwordreset_reset, shows that the user trying to reset the
      password is the one who got sent this email.

      Args:
          email: Email of the account that will reset the password.

      Raises:
          ValueError: Email entered is not a valid email.
          ValueError: Email entered does not belong to a user.
    """
    if not valid_email(email):
        raise ValueError("Email entered is not a valid email.")
    code = generate_password_reset_code(email)
    message = f"Here is your password reset code: {code}."
    # Should send email here.
    # send_email(email, message)


def auth_passwordreset_reset(reset_code, new_password):
    """
      Given a reset code for a user, set that user's new password to
      the password provided.

      Raises:
          ValueError: reset_code is not a valid reset code.
          ValueError: Password entered is not a valid password.
    """
    results = users.query("reset_codes", "contains", reset_code)
    if len(results) == 0:
        raise ValueError("reset_code is not a valid reset code.")
    if not valid_password(new_password):
        raise ValueError("Password entered is not a valid password.")
    u_id = results[0]["u_id"]
    users.remove(u_id, "reset_codes", reset_code)
    users.set(u_id, "password_hash", hash(new_password))


##################################
##           Helpers            ##
##################################


def valid_email(email):
    """
      Checks if the given string is a valid email address.
      Regular Expression From: https://emailregex.com.

      Returns:
        boolean
    """
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    match = re.search(regex, email)
    return True if match else False


def valid_token(token):
    """
      Given an auth token, returns True if it's valid, False otherwise.

      Returns:
        boolean
    """
    attempt_decode = jwt_decode(token)
    if not attempt_decode or token in blacklist_tokens:
        return False
    return True


def valid_password(password):
    """
      Given a password, returns True if it's valid, False otherwise.

      Returns:
        boolean
    """
    return len(password) > 6


def generate_password_reset_code(email):
    """
    Generates a random string to be used as a password reset code.

    Returns:
        string
    """
    results = users.query("email", "==", email)
    if len(results) == 0:
        raise ValueError("Email entered does not belong to a user.")
    user = results[0]
    code = random_string(64)
    users.set(user["u_id"], "reset_codes", code)
    return code


def hash(string):
    """
    Given a string, returns it's SHA256 hash.
    """
    return hashlib.sha256(string.encode()).hexdigest()


def jwt_encode(payload):
    """
    Returns a signed JWT token with the given payload.
    """
    expiry = datetime.now() + timedelta(TOKEN_EXPIRY_IN_DAYS)
    payload["expires_on"] = expiry.timestamp()
    return jwt.encode(payload, SERVER_SECRET, algorithm="HS256").decode("utf-8")


def jwt_decode(token):
    """
    Given a valid JWT token, returns it's payload.
    If the JWT token is not valid or cannot be parsed, returns None.
    """
    try:
        decoded = jwt.decode(token, SERVER_SECRET, algorithms=["HS256"])
        if "expires_on" not in decoded:
            raise Error()
        expiry = datetime.fromtimestamp(decoded["expires_on"])
        is_expired = datetime.now() > expiry
        if is_expired:
            raise Error()
        return decoded
    except:
        return None


def send_email(email, message):
    """
    Given a message, sends it by email using localhost as SMTP.
    """
    mail = EmailMessage()
    mail.set_content(message)
    mail["Subject"] = "Slackr Password Reset"
    mail["From"] = "Slackr Team"
    mail["To"] = email
    s = smtplib.SMTP("localhost")
    s.send_message(mail)
    s.quit()


def get_id_from_token(token):
    """
    Given a JWT token, returns u_id of user.
    Raises a value error if token is not valid.
    """
    if not valid_token(token):
        raise AccessError("Invalid token.")
    u_id = jwt_decode(token)["u_id"]
    return u_id
