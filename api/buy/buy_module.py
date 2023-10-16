# Server Imports
from flask import current_app, g, make_response, jsonify, request

# Other Imports
import time
import stripe

POSSIBLE_ITEMS_LIVE_LINKS = {
    'essentialist': 'https://buy.stripe.com/28o6pf7FvgzN6qseUU',
    'perfectionist': 'https://buy.stripe.com/bIY8xnf7X4R59CE3cd',
    'international': 'https://buy.stripe.com/8wM28Zgc10APaGI7su',
    'essentialist-upgrade': 'https://buy.stripe.com/28o6pf7FvgzN6qseUU',
    'perfectionist-upgrade': 'price_1NsQHIJYeTnJg0pUXYj6eF41',
}

POSSIBLE_ITEMS_TEST_LINKS = {
    'essentialist': 'https://buy.stripe.com/test_aEU6ryfy50AD8Y8fYY',
    'perfectionist': 'https://buy.stripe.com/test_dR6bLSfy5abd7U49AB',
    'international': 'https://buy.stripe.com/test_eVa03a5Xvbfh5LWeUW',
    'essentialist-upgrade': 'https://buy.stripe.com/28o6pf7FvgzN6qseUU',
    'perfectionist-upgrade': 'price_1NsQHIJYeTnJg0pUXYj6eF41',
}


POSSIBLE_ITEMS_LIVE = {
    'essentialist': 'price_1NsQncJYeTnJg0pUNCs1G09j',
    'perfectionist': 'price_1NsQnhJYeTnJg0pUCCyXHB8L',
    'international': 'price_1Nvd56JYeTnJg0pUH0pO4yDl',
    'essentialist-upgrade': 'price_1Nx9zjJYeTnJg0pUHwoBuasD',
    'perfectionist-upgrade': 'price_1NxA0BJYeTnJg0pUd5LXjJzM',
}

POSSIBLE_ITEMS_TEST = {
    'essentialist': 'price_1NsQHIJYeTnJg0pUXYj6eF41',
    'perfectionist': 'price_1NsQIBJYeTnJg0pU6nn9CUuJ',
    'international': 'price_1Nvd4eJYeTnJg0pUSdCr21Ok',
    'essentialist-upgrade': 'price_1Nx6WQJYeTnJg0pUUQMQlfSk',
    'perfectionist-upgrade': 'price_1Nx6XHJYeTnJg0pUdTGPTV37',
}


def get_item_to_buy():
    item_id = request.form.get('item_id', None)
    production_mode = current_app.config.get('IS_PRODUCTION', False)

    # Set the correct POSSIBLE_ITEMS list depending on production_mode
    POSSIBLE_ITEMS = POSSIBLE_ITEMS_LIVE if production_mode else POSSIBLE_ITEMS_TEST

    if item_id is None or item_id not in POSSIBLE_ITEMS:
        return jsonify(
            {
                "message": "Item not found",
                "errors": [
                    "We couldn’t find an item matching the one you entered."
                ],
                "valid": False
            }
        ), 400

    # if item_id contains 'upgrade' then we need to check if the user is already subscribed
    # if they are, then we need to return the upgrade price

    is_upgrade = False

    if 'upgrade' in item_id:
        is_upgrade = True

    # if the user is currently either on the "Perfectionist" or "International" package, then they can't upgrade
    cursor = g.db.cursor()

    # get the auth_token cookie and use that
    auth_token = request.cookies.get('auth_token', None)

    if auth_token is not None:
        cursor.execute(
            "SELECT package FROM users WHERE auth_token = %s", (auth_token,))
        package = cursor.fetchone()

        if package is not None:
            package = package[0]

            if package == "Perfectionist" or package == "International":
                # they should have unlimited reviews, so they can't upgrade, instead add reviews (if they've somehow run out)
                cursor.execute(
                    "UPDATE users SET statements_left = 9999 WHERE auth_token = %s", (auth_token,))
                g.db.commit()

                return jsonify(
                    {
                        "message": "User already has unlimited reviews",
                        "errors": [
                            "You already have unlimited reviews, so you can’t upgrade."
                        ],
                        "valid": False
                    }
                ), 435

    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', None)
    success_url = current_app.config['PAY_BASE_URL'] + \
        '/?id={CHECKOUT_SESSION_ID}'
    cancel_url = current_app.config['LANDING_BASE_URL'] + '/#pricing'

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': POSSIBLE_ITEMS[item_id],
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'item_id': item_id,
                'is_upgrade': is_upgrade
            },
            phone_number_collection={
                # collect number if not upgrade
                'enabled': not is_upgrade
            }
        )
    except Exception as e:
        return jsonify(
            {
                "message": "Checkout failed",
                "errors": [
                    "We couldn’t create a checkout for the item you entered."
                ],
                "valid": False,
                "e": str(e)
            }
        ), 400

    return jsonify(
        {
            "message": "Checkout created",
            "errors": [],
            "valid": True,
            "item_id": item_id,
            "item_link": session.url,
        }
    ), 200


def confirm_checkout():
    # /s1/checkout/confirm
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', None)

    checkout_id = request.form.get('checkout_id', None)

    if checkout_id is None:
        return jsonify(
            {
                "message": "Checkout not found",
                "errors": [
                    "We couldn’t find a checkout matching the one you entered."
                ],
                "valid": False
            }
        ), 400

    checkout = None

    try:
        checkout = stripe.checkout.Session.retrieve(checkout_id)
    except Exception as e:
        return jsonify(
            {
                "message": "Checkout not found",
                "errors": [
                    "We couldn’t find a checkout matching the one you entered."
                ],
                "valid": False,
                "e": str(e)
            }
        ), 400

    item_paid_for = checkout.metadata.get('item_id', None)
    item_is_paid = checkout.payment_status == 'paid'

    if item_paid_for is None or not item_is_paid:
        return jsonify(
            {
                "message": "Checkout not found",
                "errors": [
                    "We couldn’t find a checkout matching the one you entered."
                ],
                "valid": False
            }
        ), 400

    return jsonify(
        {
            "message": "Payment confirmed",
            "errors": [],
            "valid": True,
            "item_id": item_paid_for,
            "item_name": item_paid_for.capitalize(),
            "checkout_id": checkout_id,
            "total": checkout.amount_total,
            "total_decimal": checkout.amount_total / 100,
            "total_formatted": f"{checkout.amount_total / 100:.2f} {checkout.currency.upper()}",
            "currency": checkout.currency.upper(),
            "email": checkout.customer_details.email,
            "phone": checkout.customer_details.phone,
            "is_upgrade": checkout.metadata.get('is_upgrade', False)
        }
    ), 200
