from flask_cors import CORS
from json import dumps
from datetime import datetime
from flask import Flask, request, send_file
from .functions.admin import admin_userpermission_change
from .functions.auth import (
    auth_login,
    auth_logout,
    auth_passwordreset_request,
    auth_passwordreset_reset,
    auth_register,
    valid_token,
)
from .functions.channels import (
    channel_addowner,
    channel_details,
    channel_invite,
    channel_join,
    channel_leave,
    channel_messages,
    channel_removeowner,
    channels_create,
    channels_list,
    channels_listall,
)
from .functions.messages import (
    message_edit,
    message_pin,
    message_react,
    message_remove,
    message_send,
    message_unpin,
    message_sendlater,
    message_unreact,
)
from .functions.search import search
from .functions.standup import standup_send, standup_start, standup_active
from .functions.users import (
    user_profile,
    user_profile_setemail,
    user_profile_sethandle,
    user_profile_setname,
    user_profiles_uploadphoto,
    users_all
)
from .errors.AccessError import AccessError
from .errors.ValueError import ValueError


############################################
# Server Config
############################################


APP = Flask(__name__)
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
CORS(APP)



############################################
# Error Handlers
############################################


def defaultErrorHandler(err):
    if isinstance(err, ValueError) or isinstance(err, AccessError):
        return {
            "code": err.code,
            "name": err.name,
            "message": str(err),
        }
    else:
        return {
                "code": 500,
                "name": "System Error",
                "message": str(err),
            }


@APP.errorhandler(Exception)
def systemErrorHandler(err):
    api_error = defaultErrorHandler(err)
    return dumps(api_error), api_error["code"]


############################################
# Echo Routes
############################################


@APP.route("/echo/get", methods=["GET"])
def echo_get():
    return dumps({"echo": request.args.get("echo"),})


@APP.route("/echo/post", methods=["POST"])
def echo_post():
    return dumps({"echo": request.form.get("echo"),})


############################################
# Auth Routes
############################################


@APP.route("/auth/login", methods=["POST"])
def auth_login_route():
    email = request.form.get("email")
    password = request.form.get("password")
    return dumps(auth_login(email, password)), 200


@APP.route("/auth/logout", methods=["POST"])
def auth_logout_route():
    token = request.form.get("token")
    auth_logout(token)
    return dumps({"is_success": not valid_token(token)}), 200


@APP.route("/auth/register", methods=["POST"])
def auth_register_route():
    email = request.form.get("email")
    password = request.form.get("password")
    name_first = request.form.get("name_first")
    name_last = request.form.get("name_last")
    return dumps(auth_register(email, password, name_first, name_last)), 200


@APP.route("/auth/passwordreset/request", methods=["POST"])
def auth_passwordreset_request_route():
    email = request.form.get("email")
    auth_passwordreset_request(email)
    return dumps({}), 200


@APP.route("/auth/passwordreset/reset", methods=["POST"])
def auth_passwordreset_reset_route():
    reset_code = request.form.get("reset_code")
    new_password = request.form.get("new_password")
    auth_passwordreset_reset(reset_code, new_password)
    return dumps({}), 200


############################################
# Channel(s) Routes
############################################


@APP.route("/channel/invite", methods=["POST"])
def channel_invite_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    u_id = int(request.form.get("u_id"))
    channel_invite(token, channel_id, u_id)
    return dumps({}), 200


@APP.route("/channel/details", methods=["GET"])
def channel_details_route():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    return dumps(channel_details(token, channel_id)), 200


@APP.route("/channel/messages", methods=["GET"])
def channel_messages_route():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))
    return dumps(channel_messages(token, channel_id, start)), 200
 

@APP.route("/channel/leave", methods=["POST"])
def channel_leave_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    channel_leave(token, channel_id)
    return dumps({}), 200


@APP.route("/channel/join", methods=["POST"])
def channel_join_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    channel_join(token, channel_id)
    return dumps({}), 200


@APP.route("/channel/addowner", methods=["POST"])
def channel_addowner_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    u_id = int(request.form.get("u_id"))
    channel_addowner(token, channel_id, u_id)
    return dumps({}), 200


@APP.route("/channel/removeowner", methods=["POST"])
def channel_removeowner_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    u_id = int(request.form.get("u_id"))
    channel_removeowner(token, channel_id, u_id)
    return dumps({}), 200


@APP.route("/channels/list", methods=["GET"])
def channels_list_route():
    token = request.args.get("token")
    return dumps(channels_list(token)), 200


@APP.route("/channels/listall", methods=["GET"])
def channels_listall_route():
    token = request.args.get("token")
    return dumps(channels_listall(token)), 200


@APP.route("/channels/create", methods=["POST"])
def channels_create_route():
    token = request.form.get("token")
    name = request.form.get("name")
    is_public = True if request.form.get("is_public") in ["true", "True"] else False
    channel_id = channels_create(token, name, is_public)
    return dumps({"channel_id": channel_id}), 200


############################################
# Message Routes
############################################


@APP.route("/message/sendlater", methods=["POST"])
def message_sendlater_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    message = request.form.get("message")
    time_sent = datetime.fromtimestamp(int(request.form.get("time_sent")))
    message_sendlater(token, channel_id, message, time_sent)
    return dumps({}), 200


@APP.route("/message/send", methods=["POST"])
def message_send_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    message = request.form.get("message")
    message_send(token, channel_id, message)
    return dumps({}), 200


@APP.route("/message/remove", methods=["DELETE"])
def message_remove_route():
    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    message_remove(token, message_id)
    return dumps({}), 200


@APP.route("/message/edit", methods=["PUT"])
def message_edit_route():
    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    message = request.form.get("message")
    message_edit(token, message_id, message)
    return dumps({}), 200


@APP.route("/message/react", methods=["POST"])
def message_react_route():
    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    react_id = int(request.form.get("react_id"))
    message_react(token, message_id, react_id)
    return dumps({}), 200


@APP.route("/message/unreact", methods=["POST"])
def message_unreact_route():
    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    react_id = int(request.form.get("react_id"))
    message_unreact(token, message_id, react_id)
    return dumps({}), 200


@APP.route("/message/pin", methods=["POST"])
def message_pin_route():
    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    message_pin(token, message_id)
    return dumps({}), 200


@APP.route("/message/unpin", methods=["POST"])
def message_unpin_route():
    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    message_unpin(token, message_id)
    return dumps({}), 200


############################################
# User Routes
############################################


@APP.route("/user/profile", methods=["GET"])
def user_profile_route():
    token = request.args.get("token")
    u_id = int(request.args.get("u_id"))
    return dumps(user_profile(token, u_id)), 200


@APP.route("/user/profile/setname", methods=["PUT"])
def user_profile_setname_route():
    token = request.form.get("token")
    name_first = request.form.get("name_first")
    name_last = request.form.get("name_last")
    user_profile_setname(token, name_first, name_last)
    return dumps({}), 200


@APP.route("/user/profile/setemail", methods=["PUT"])
def user_profile_setemail_route():
    token = request.form.get("token")
    email = request.form.get("email")
    user_profile_setemail(token, email)
    return dumps({}), 200


@APP.route("/user/profile/sethandle", methods=["PUT"])
def user_profile_sethandle_route():
    token = request.form.get("token")
    handle_str = request.form.get("handle_str")
    user_profile_sethandle(token, handle_str)
    return dumps({}), 200


@APP.route("/user/profiles/uploadphoto", methods=["POST"])
def user_profile_uploadphoto_route():
    token = request.form.get("token")
    img_url = request.form.get("img_url")
    x_start = int(request.form.get("x_start"))
    y_start = int(request.form.get("y_start"))
    x_end = int(request.form.get("x_end"))
    y_end = int(request.form.get("y_end"))
    user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    return dumps({}), 200


@APP.route("/users/all", methods=["GET"])
def users_all_route():
    token = request.args.get("token")
    return dumps(users_all(token)), 200


############################################
# Standup Routes
############################################


@APP.route("/standup/start", methods=["POST"])
def standup_start_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    length = int(request.form.get("length"))
    return dumps(standup_start(token, channel_id, length)), 200


@APP.route("/standup/active", methods=["GET"])
def standup_active_route():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    return dumps(standup_active(token, channel_id)), 200


@APP.route("/standup/send", methods=["POST"])
def standup_send_route():
    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    message = request.form.get("message")
    standup_send(token, channel_id, message)
    return dumps({}), 200


############################################
# Search Routes
############################################


@APP.route("/search", methods=["GET"])
def search_route():
    token = request.args.get("token")
    query_str = request.args.get("query_str")
    return dumps(search(token, query_str)), 200


############################################
# Admin Routes
############################################


@APP.route("/admin/userpermission/change", methods=["POST"])
def admin_userpermission_change_route():
    token = request.form.get("token")
    u_id = int(request.form.get("u_id"))
    permission_id = int(request.form.get("permission_id"))
    admin_userpermission_change(token, u_id, permission_id)
    return dumps({}), 200
