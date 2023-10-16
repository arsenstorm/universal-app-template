# Socrasica API Server

# Server Imports
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from errors.errors_module import register_error_handlers

# Other Imports
import pymssql
import time
import openai
import importlib

from config import IS_PRODUCTION

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, supports_credentials=True)
register_error_handlers(app)

# Apply configuration from config.py
app.config.from_pyfile('config.py')

# Registering blueprints
security_levels = ['v1', 'webhooks']
for security_level in security_levels:
    module = importlib.import_module(
        f"{security_level}.{security_level}_module")
    blueprint = getattr(module, f"{security_level}_bp")
    app.register_blueprint(blueprint, url_prefix=f'/{security_level}')


def open_db():
    if 'db' not in g:
        g.db = pymssql.connect(
            app.config['DB_HOST'], app.config['DB_USER'], app.config['DB_PASS'], app.config['DB_NAME'])
    if 'db_courses' not in g:
        g.db_courses = pymssql.connect(
            app.config['DB_COURSES_HOST'], app.config['DB_COURSES_USER'], app.config['DB_COURSES_PASS'], app.config['DB_COURSES_NAME'])
    return g.db, g.db_courses


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    db_courses = g.pop('db_courses', None)

    if db is not None:
        db.close()

    if db_courses is not None:
        db_courses.close()


@app.before_request
def before_request():
    g.db, g.db_courses = open_db()
    g.start_time = time.time()
    openai.api_key = app.config['OPENAI_API_KEY']
    print(f"Request: {request.method} {request.path}")


@app.after_request
def after_request(response):
    response.headers["Content-Type"] = "application/json"
    elapsed_time = time.time() - g.start_time
    print(f"Time taken to process the request: {elapsed_time} seconds")
    return response


@app.route(
    '/',
    methods=[
        'GET',
        'POST',
        'PUT',
        'DELETE'
    ]
)
def index():
    return jsonify({
        'status': 200,
        'message': 'Socrasica API Server'
    })


if __name__ == '__main__':
    if IS_PRODUCTION:
        app.run(debug=True)
    else:
        app.run(debug=True, port=5001)
