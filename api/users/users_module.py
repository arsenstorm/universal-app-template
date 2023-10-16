# Server Imports
from flask import current_app, g, request, jsonify, make_response, url_for, redirect
from datetime import timedelta
from argon2 import PasswordHasher, exceptions
import argon2

# Other Imports
import time
import secrets
import datetime
from utils.utilities_module import get_site_parameters, send_email
from html_templates.account_login.email import make_login_email

# Email Imports
from html_templates.reset_email.email import make_reset_email


def signup_user():
    # Instantiate the password hasher
    ph = PasswordHasher()
    # setting these parameters as defaults.

    # To hash a password:
    # pw_hash = ph.hash(PASSWORD)

    # To check a password:
    # ph.verify(pw_hash, PASSWORD)

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        name = request.form.get('name')
        terms_accepted = request.form.get('terms')
        referrer = request.form.get('referrer', None)

        # verify user data

        if password != password_confirm:
            return jsonify(
                {
                    "message": "Passwords do not match",
                    "errors": [
                        "The passwords you have entered do not match."
                    ],
                    "valid": False
                }
            ), 400

        if terms_accepted != "true":
            return jsonify(
                {
                    "message": "Terms not accepted",
                    "errors": [
                        "You must accept the terms and conditions to create an account."
                    ],
                    "valid": False
                }
            ), 400

        # max size of email, name, and password is 255 characters
        if len(str(email)) > 255 or len(str(name)) > 255 or len(str(password)) > 255:
            return jsonify(
                {
                    "message": "Invalid data",
                    "errors": [
                        "Your details are too long."
                    ],
                    "valid": False
                }
            ), 400

        cursor = g.db.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user is not None:
            return jsonify(
                {
                    "message": "User already exists",
                    "errors": [
                        "A user with this email already exists."
                    ],
                    "valid": False
                }
            ), 400

        # hash password
        hashed_password = ph.hash(password)

        # add user to database
        user_id_exists = True

        while user_id_exists is not None:
            user_id = "user_" + secrets.token_urlsafe(32)
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            user_id_exists = cursor.fetchone()

        referral_link_exists = True

        while referral_link_exists is not None:
            referral_link = "https://refer.socrasica.com/" + \
                secrets.token_urlsafe(12)
            cursor.execute(
                "SELECT user_id FROM users WHERE referral_link = %s", (referral_link,))
            referral_link_exists = cursor.fetchone()

        cursor.execute(
            "INSERT INTO users (user_id, email, password, name, created_at, referral_link) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, email, hashed_password, name, datetime.datetime.now(), referral_link))
        g.db.commit()

        # generate auth_token
        auth_token = "auth_" + secrets.token_urlsafe(32)

        # set the auth_token for the user
        cursor.execute(
            "UPDATE users SET auth_token = %s WHERE user_id = %s", (auth_token, user_id))
        g.db.commit()

        warning = []

        if referrer is not None:
            # add referrer to database
            # verify referrer exists

            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = %s", (referrer,))
            referrer_user = cursor.fetchone()

            if referrer_user is not None:
                cursor.execute(
                    "INSERT INTO referrals (referring_id, referred_id) VALUES (%s, %s)", (referrer, user_id))
                g.db.commit()
            else:
                warning.append("Referring UserID does not exist.")

        response = make_response(jsonify({
            'status': 'success',
            "message": "User account created, and logged in successfully!",
            "warnings": warning,
            "auth_token": auth_token,
            'valid': True
        }))

        # return success message
        response.set_cookie(
            'auth_token',
            value=auth_token,
            domain=current_app.config['COOKIE_DOMAIN'],
            path='/',
            expires=time.time() + 2419200,
            httponly=False,
            samesite=current_app.config['COOKIE_SAMESITE'],
            secure=True)

        return response

    return jsonify({"message": "Invalid Method"}), 405


def verify_user_email():
    # Instantiate the password hasher
    ph = PasswordHasher()
    token = request.args.get('token')
    selector = request.args.get('selector')

    # verify user data

    cursor = g.db.cursor()

    cursor.execute(
        "SELECT user_id FROM user_verification WHERE email_verification_token = %s AND email_verification_selector = %s", (token, selector))
    user = cursor.fetchone()

    if user is None:
        return jsonify(
            {
                "message": "Invalid token",
                "errors": [
                    "The token you have entered is invalid."
                ],
                "valid": False
            }
        ), 400

    # update user's email_verified_at to the current time
    cursor.execute(
        "UPDATE users SET email_verified_at = %s AND verified = %s WHERE user_id = %s", (datetime.datetime.now(), True, user[0]))
    g.db.commit()

    return jsonify(
        {
            "message": "Email verified successfully",
            "valid": True
        }
    ), 200


def login_user():
    # Instantiate the password hasher
    ph = PasswordHasher()
    # setting these prameters as defaults.

    if request.method == "POST":
        # get user data from request
        # email and password (form data)

        email = request.form.get('email', None)
        code = request.form.get('code', None)

        if email is None:
            return jsonify(
                {
                    "message": "Invalid data",
                    "errors": [
                        "You must enter an email address."
                    ],
                    "valid": False
                }
            ), 400

        # verify user data

        cursor = g.db.cursor()

        cursor.execute(
            "SELECT user_id, most_recent_code, name, code_expiry FROM users WHERE email = %s", (email,))
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

        if code is None:
            # we send a code to the user's email
            # generate 6 digit code
            code = secrets.randbelow(999999)
            code = str(code).zfill(6)

            # hash code for security
            hashed_code = ph.hash(code)
            # in 30 minutes, the code will expire
            expiry_time = datetime.datetime.now() + timedelta(minutes=30)

            # update user's most_recent_code to the current code
            cursor.execute(
                "UPDATE users SET most_recent_code = %s, code_expiry = %s WHERE user_id = %s", (hashed_code, expiry_time, user[0]))
            g.db.commit()

            # send email to user
            body_message = """Hey, [NAME]

            We’ve received a request to log in to your Socrasica account.

            Enter the code when prompted to log in.

            Code: [CODE]
            
            If you didn’t request to log in to your Socrasica account, don’t worry. Your account is safe.
            
            Thanks,
            Socrasica"""

            body_message = body_message.replace("[NAME]", user[2])
            body_message = body_message.replace("[CODE]", code)

            html_message = make_login_email(user[2], code)

            send_email(email, "Socrasica Account Login",
                       body_message, html_message)

            return jsonify(
                {
                    "message": "Code sent",
                    "valid": True
                }
            ), 200
        else:
            if user[3] < datetime.datetime.now():
                return jsonify(
                    {
                        "message": "Code expired",
                        "errors": [
                            "You didn’t enter the code we sent you in time. Please try logging in again."
                        ],
                        "valid": False
                    }
                ), 400

            most_recent_code = user[1]

            # We can also add a check here to catch invalid password hash exceptions.
            try:
                if not ph.verify(most_recent_code, code):
                    return jsonify(
                        {
                            "message": "Invalid code",
                            "errors": [
                                "You’ve entered an incorrect code."
                            ],
                            "valid": False
                        }
                    ), 400
            except (argon2.exceptions.VerifyMismatchError, argon2.exceptions.InvalidHash):
                return jsonify(
                    {
                        "message": "Invalid code",
                        "errors": [
                            "You’ve entered an incorrect code."
                        ],
                        "valid": False
                    }
                ), 400
            except Exception as e:
                return jsonify(
                    {
                        "message": "An error occurred",
                        "errors": [
                            "An error occurred. Please try again."
                        ],
                        "valid": False,
                        "debug": str(e)
                    }
                ), 500

            # add user to database

            # generate auth_token
            auth_token = "auth_" + secrets.token_urlsafe(32)

            # set the auth_token for the user
            cursor.execute(
                "UPDATE users SET auth_token = %s, code_expiry = %s, most_recent_code = %s WHERE user_id = %s", (auth_token, datetime.datetime.now(), None, user[0]))
            g.db.commit()

            response = make_response(jsonify({
                'status': 'success',
                "message": "User logged in successfully",
                "auth_token": auth_token,
                'valid': True
            }))

            # return success message
            response.set_cookie(
                'auth_token',
                value=auth_token,
                domain=current_app.config['COOKIE_DOMAIN'],
                path='/',
                expires=time.time() + 2419200,
                httponly=False,
                samesite=current_app.config['COOKIE_SAMESITE'],
                secure=True)

            return response

    return jsonify({"message": "Invalid Method"}), 405


def reset_user_password():
    cursor = g.db.cursor()
    ph = PasswordHasher()

    if request.method == "POST":
        email = request.form.get('email')

        cursor.execute(
            "SELECT user_id, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user is None:
            return jsonify(
                {
                    "message": "User not found",
                    "errors": [
                        "We couldn’t find an account matching the email you entered."
                    ],
                    "valid": False
                }
            ), 400

        name = user[1]
        # Step 1: Generate selector and token
        selector = secrets.token_urlsafe(16)
        token = secrets.token_urlsafe(32)

        # Step 2: Hash the token
        hashed_token = ph.hash(token)

        # Step 3: Save selector, hashed_token, and expiration to database
        expiration = datetime.datetime.now() + timedelta(hours=1)
        cursor.execute(
            "INSERT INTO password_reset_tokens (selector, hashed_token, user_id, expiration) VALUES (%s, %s, %s, %s)",
            (selector, hashed_token, user[0], expiration)
        )
        g.db.commit()

        # Step 4: Send Email
        reset_url = url_for(
            's1.s1_reset_user',
            _external=True,
            selector=selector,
            token=token
        )

        email_subject = "Password Reset Request"
        email_body = f"Please click the following link to reset your password: {reset_url}"

        email_html = make_reset_email(name, reset_url)

        send_email(email, email_subject, email_body, email_html)

        return jsonify(
            {
                "message": "Password reset email sent",
                "valid": True
            }
        ), 200
    elif request.method == "GET":
        selector = request.args.get('selector')
        token = request.args.get('token')

        if not selector or not token:
            if current_app.config['IS_PRODUCTION']:
                return redirect('https://auth.services.socrasica.com/#reset')
            else:
                return redirect('http://localhost:3000/#reset')

        cursor.execute(
            "SELECT user_id, expiration FROM password_reset_tokens WHERE selector = %s",
            (selector,)
        )
        row = cursor.fetchone()

        if row is None:
            if current_app.config['IS_PRODUCTION']:
                return redirect('https://auth.services.socrasica.com/#reset')
            else:
                return redirect('http://localhost:3000/#reset')

        user_id, expiration = row

        # Check if the token has expired
        if datetime.datetime.now() > expiration:
            if current_app.config['IS_PRODUCTION']:
                return redirect('https://auth.services.socrasica.com/#reset')
            else:
                return redirect('http://localhost:3000/#reset')
        else:
            if current_app.config['IS_PRODUCTION']:
                return redirect('https://auth.services.socrasica.com/reset?selector=' + selector + '&token=' + token)
            else:
                return redirect('http://localhost:3000/reset?selector=' + selector + '&token=' + token)

    else:
        return jsonify({"message": "Invalid Method"}), 405


def check_if_reset_token_expire():
    cursor = g.db.cursor()
    selector = request.form.get('selector')

    cursor.execute(
        "SELECT selector, expiration FROM password_reset_tokens WHERE selector = %s",
        (selector,)
    )
    row = cursor.fetchone()

    if row is None:
        return jsonify({
            "errors": [
                "Invalid link"
            ]
        }), 400

    selector, expiration = row

    # Check if the token has expired
    if datetime.datetime.now() > expiration:
        return jsonify({
            "errors": [
                "Link has expired"
            ]
        }), 400

    return jsonify({"message": "Link is valid"}), 200


def complete_password_reset():
    cursor = g.db.cursor()
    ph = PasswordHasher()

    selector = request.form.get('selector')
    token = request.form.get('token')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')

    # Validate selector and token
    if not selector or not token:
        return jsonify({
            "errors": [
                "An error occurred. Please try requesting a new link."
            ]
        }), 400

    # Check database for selector
    cursor.execute(
        "SELECT hashed_token, user_id, expiration FROM password_reset_tokens WHERE selector = %s",
        (selector,)
    )
    row = cursor.fetchone()

    if row is None:
        return jsonify({
            "errors": [
                "An error occurred. Please try requesting a new link."
            ]
        }), 400

    hashed_token, user_id, expiration = row

    # Check if the token has expired
    if datetime.datetime.now() > expiration:
        return jsonify({
            "errors": [
                "This link has expired. Please try requesting a new link."
            ]
        }), 400

    # Check if the passwords match
    if password != password_confirm:
        return jsonify({
            "errors": [
                "The passwords you have entered do not match."
            ]
        }), 400

    # Verify the token against the hashed token from the database
    try:
        ph.verify(hashed_token, token)

        # Hash the new password
        hashed_password = ph.hash(password)

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password = %s WHERE user_id = %s", (hashed_password, user_id))
        g.db.commit()

        # Delete the token from the database
        cursor.execute(
            "DELETE FROM password_reset_tokens WHERE selector = %s", (selector,))
        g.db.commit()
    except exceptions.VerifyMismatchError:
        return jsonify({
            "errors": [
                "An error occurred. Please try requesting a new link."
            ]
        }), 400

    return jsonify({"message": "Password reset successful"}), 200
