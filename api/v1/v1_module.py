from flask import Blueprint, jsonify, current_app, request, g
# from .service_a import some_function_from_service_a
# where service_a is a python module in the same directory
# as this file stored as service_a.py
from utils.utilities_module import get_site_parameters, send_email
from dashboard.dashboard_module import get_dashboard
from buy.buy_module import get_item_to_buy

v1_bp = Blueprint('v1', __name__)


@v1_bp.route('/', methods=['GET', 'POST'])
def v1_index():
    return jsonify({"message": "Hello from v1!"}), 200


# @v1_bp.route('/test/email', methods=['POST', 'GET'])
# def send_email_test():
    # return send_email("arsen@nerverift.com", "Test Email", "This is a test email.", cc='arsen@devrift.co,storm@devrift.co', bcc='arsen@shkrumelyak.com,storm@nerverift.com', reply_to='support@socrasica.com')


@v1_bp.route('/anonymous/dashboard', methods=['POST'])
def anonymous_dashboard():
    return get_dashboard()

# Note that Jsonify takes an additional 0.2 ms to run

### v1 Does not require any authentication ###

@v1_bp.route('/buy/get', methods=['POST'])
def buy_get():
    return get_item_to_buy()
