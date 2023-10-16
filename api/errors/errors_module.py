# error_handlers.py
from flask import jsonify, request
import datetime
import time


def generate_error_response(message, status_code, error_string):
    return jsonify({
        'error': {
            'message': str(message)
        },
        'debugging': {
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'unixtime': time.time(),
            'method': request.method,
            'error': error_string,
        }
    }), status_code


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(e):
        return generate_error_response(e, 404, '404 Not Found')

    @app.errorhandler(500)
    def internal_server_error(e):
        return generate_error_response(e, 500, '500 Internal Server Error')
    
    @app.errorhandler(502)
    def bad_gateway(e):
        return generate_error_response(e, 502, '502 Bad Gateway')    

    @app.errorhandler(400)
    def bad_request(e):
        return generate_error_response(e, 400, '400 Bad Request')

    @app.errorhandler(401)
    def unauthorized(e):
        return generate_error_response(e, 401, '401 Unauthorized')
