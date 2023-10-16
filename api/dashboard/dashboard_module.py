# Server Imports
from flask import current_app, g, request, jsonify, make_response
import hashlib
import hmac
import urllib.parse

# Other Imports
from utils.utilities_module import get_site_parameters, get_welcome_message, get_user_progress, get_dashboard_items, has_referred, get_bank_statement, get_user_permissions


def get_dashboard():
    # setting these prameters as defaults.
    # get auth_token and path from POST form data
    cursor = g.db.cursor()
    auth_token = request.form.get('auth_token', None)
    is_logged_in = False
    force_redirect = False

    cursor.execute(
        "SELECT user_id, name, email, created_at, package, is_staff, statements_left FROM users WHERE auth_token = %s", (auth_token,))
    user = cursor.fetchone()

    if user is None:
        return jsonify(
            {
                "message": "User not found",
                "errors": [
                    "We couldn’t find an account matching the email and password you entered."
                ],
                "valid": False
            }
        ), 400

    is_logged_in = True
    user_id = user[0]
    package = user[4]
    is_staff = user[5]

    permissions = {}
    user_data = {
        "user": {
            "is_logged_in": True,
            "id": user_id,
            "name": user[1],
            "email": user[2],
            "created_at": user[3],
            "package": package,
            "is_staff": is_staff,
            "statements_left": user[6],
            "img": {
                "src": "/favicon.ico",
                "alt": ""
            }
        }
    }

    permissions = get_user_permissions(user_id)

    response = {
        "message": "Dashboard Returned",
        "banner": {
            "message": "We are currently testing new features. They may not work as expected and may change at any time.",
            "messageID": "beta_experimental_features",
        },
        "valid": True,
        "config": {
            "settings": {
                "title": "Settings",
                "href": "#"
            },
            "logout": {
                "title": "Logout",
                "href": "/logout"
            },
            "profile": {
                "title": "Your Profile",
                "href": "#"
            }
        },
        "shortcuts": [],
        "force_redirect": force_redirect,
        "permissions": permissions,
    }

    # Add the parameters to the response
    response.update(user_data)

    return response, 200
