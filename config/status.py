# coding:utf-8
"""Here is some status defination."""

STATUS = dict([
    # Normal Error
    (3001, 'Username or password is invalid'),
    (3002, 'Account is inactivated.'),
    (3003, 'Email not Register'),
    (3004, 'User name or email already exists.'),
    (3005, 'User\'s session key not exists, need to login.'),
    (3006, 'User\'s session value not exists, need to login'),
    (3007, 'Other people login this account, session is invalid.'),
    (3008, 'User Permission Deny.'),
    (3011, 'Account is not exists, please sign up.'),
    (3012, 'Address is not allowed.'),
    (3014, 'Nick Name already set.'),
    (3015, 'Either "nickname" or "password" should be in arguments.'),
    (3016, 'Either "username" or "email" should be in arguments.'),
    (3031, 'Not Regular Password'),
    (3032, 'Not Regular Email'),
    (3033, 'Not Regular Nickname'),
    (3100, 'Permission Deny.'),
    (3104, 'Chat Not Exists.'),
    (3105, 'Can not enter this chat.'),
    (3106, 'Chat owner missed.'),
    (3150, 'Chat Member Exists.'),
    (3151, 'Chat Member Not Exists.'),
    (3152, 'No Message Found.'),
    (4003, 'Permission Denied.'),
    (4004, 'Not Found Error.'),
    (4005, 'Permission Error.'),
    (5003, 'Server Error.')
])


def get_status_message(code):
    if code == -1:
        return None

    try:
        return STATUS[code]
    except KeyError:
        raise KeyError(f'Unknown status {code}.')
