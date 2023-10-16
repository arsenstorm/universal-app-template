import base64
import os
import json
from flask import g, current_app, jsonify, Blueprint, request
import time
import stripe
import secrets
import datetime

from utils.utilities_module import send_email
from html_templates.purchase_email.email import make_purchase_email

webhooks_bp = Blueprint('webhooks', __name__)


@webhooks_bp.route('/', methods=['GET', 'POST'])
def webhook_function():
    return jsonify({"message": "Hello from Socrasica Webhooks!"}), 200

@webhooks_bp.route('/stripe', methods=['GET', 'POST'])
def stripe_webhook_function():
    cursor = g.db.cursor()

    # verify webhook signature
    payload = request.data
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    sig_header = request.headers.get('Stripe-Signature')

    endpoint_secret = current_app.config['STRIPE_SIGNING_SECRET']

    event = None

    try:
        if endpoint_secret is not None:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
    except ValueError as e:
        # Invalid payload
        return jsonify({"message": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({"message": "Invalid signature"}), 400
    
    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        # sign the user up for the package
        # send the user an email

        # double check payment status
        if session['payment_status'] != 'paid':
            # forcing a 400 error to trigger a retry from Stripe - probably not the best way to do this but its okay for now
            return jsonify({"message": "Payment not completed"}), 400

        package_id = session['metadata']['item_id']
        is_upgrade = session['metadata']['is_upgrade'] == "True" or session['metadata']['is_upgrade'] == "true" or session['metadata']['is_upgrade'] == True
        print(session['metadata'])
        package_name = package_id.split('-')[0].capitalize()
        email = session['customer_details']['email'] if session['customer_details']['email'] is not None else ""
        name = session['customer_details']['name'] if session['customer_details']['name'] is not None else ""
        phone = session['customer_details']['phone'] if session['customer_details']['phone'] is not None else ""
        
        user_id_exists = True

        while user_id_exists is not None:
            user_id = "user_" + secrets.token_urlsafe(32)
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            user_id_exists = cursor.fetchone()

        statements_left = 0

        if package_name == "Essentialist":
            statements_left = 1
        elif package_name == "Perfectionist":
            statements_left = 9999
        elif package_name == "International":
            statements_left = 9999

        if not is_upgrade:
            cursor.execute(
                "INSERT INTO users (user_id, email, name, created_at, phone_number, package, statements_left) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_id, email, name, datetime.datetime.now(), phone, package_name, statements_left))
            g.db.commit()

            # Send email to user
            body_message = """Hey, [NAME]!

            Welcome to Socrasica!

            You bought the [PACKAGE_NAME] package, and this email is confirmation that we’ve received your payment.

            When you’re ready to start, head over to &rarr; https://app.socrasica.com
            """

            body_message = body_message.replace("[NAME]", name)
            body_message = body_message.replace("[PACKAGE_NAME]", package_name)

            html_template = make_purchase_email(
                name,
                package_name
            )

            send_email(
                email,
                'Welcome to Socrasica!',
                body_message,
                html_template
            )
        
        if is_upgrade:
            # add statements to user
            # check if the email exists in the database

            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s", (email,))
            
            user_id = cursor.fetchone()

            if user_id is None:
                # send an email to the user saying something went wrong with the upgrade, and to contact support
                body_message = """Hey, [NAME]!

                We tried to upgrade your account, but something went wrong. Please contact support at support@socrasica.com

                Thanks!
                """

                body_message = body_message.replace("[NAME]", name)

                send_email(
                    email,
                    'Socrasica - Problem with your upgrade!',
                    body_message
                )

                return jsonify({"message": "User not found"}), 400

            cursor.execute(
                "UPDATE users SET statements_left = statements_left + %s, package = %s WHERE user_id = %s", (statements_left, package_name, user_id[0],))
            g.db.commit()

            # Send email to user
            body_message = """Hey, [NAME]!

            Thanks for upgrading your Socrasica account!

            You bought the [PACKAGE_NAME] package, and this email is confirmation that we’ve received your payment.

            When you’re ready to start, head over to &rarr; https://app.socrasica.com
            """

            body_message = body_message.replace("[NAME]", name)
            body_message = body_message.replace("[PACKAGE_NAME]", package_name)

            html_template = make_purchase_email(
                name,
                package_name
            )

            send_email(
                email,
                'Socrasica - Successful Upgrade!',
                body_message,
                html_template
            )

        return jsonify({"message": "Payment completed"}), 200
    
    return jsonify({"message": "Hello from Stripe Webhooks"}), 200