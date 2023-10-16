# Imports
import os

# DB Stuff
DB_DRIVER = '{ODBC Driver 17 for SQL Server}'
DB_HOST = os.environ.get('DB_HOST', '')
DB_PORT = os.environ.get('DB_PORT', 1433)
DB_NAME = os.environ.get('DB_NAME', '')
DB_USER = os.environ.get('DB_USER', '')
DB_PASS = os.environ.get('DB_PASS', '')

DB_CONN = f"DRIVER={DB_DRIVER};SERVER=tcp:{DB_HOST},{DB_PORT};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS}"

SERVER_TOKEN = "..."

# AI Stuff

OPENAI_API_KEY = 'sk-...'
OPENAI_ORGANIZATION = 'org-...'

# Cookie Stuff
if os.environ.get('DEPLOYED_ON_AWS'):
    COOKIE_DOMAIN = '...'
    COOKIE_SAMESITE = 'Lax'
    IS_PRODUCTION = True
else:
    COOKIE_DOMAIN = None
    COOKIE_SAMESITE = 'None'
    IS_PRODUCTION = False

# Email Stuff

REFRESH_TOKEN = os.environ.get(
    'REFRESH_TOKEN', '...')
CLIENT_ID = os.environ.get(
    'CLIENT_ID', '...')
CLIENT_SECRET = os.environ.get(
    'CLIENT_SECRET', '...')
DEFAULT_EMAIL = os.environ.get('DEFAULT_EMAIL', '...')

# Stripe Stuff

STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '...')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '...')
STRIPE_SIGNING_SECRET = os.environ.get('STRIPE_SIGNING_SECRET', None)

# BASE URLs
APP_BASE_URL = os.environ.get('APP_BASE_URL', 'http://localhost:3000')
PAY_BASE_URL = os.environ.get('PAY_BASE_URL', 'http://localhost:3001')
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5001')
LANDING_BASE_URL = os.environ.get('LANDING_BASE_URL', 'http://localhost:2997')


# Permissions

PERMISSIONS_DICT = {
    1: 'basic',
    2: 'manage_posts',
    4: 'manage_users',
    8: 'manage_payouts',
    16: 'manage_permissions',
    32: 'manage_reviews',
    64: 'c',
    128: 'd',
    256: 'e',
    512: 'f',
    1024: 'g',
    2048: 'h',
    4096: 'i',
    8192: 'j',
    16384: 'k',
    32768: 'l',
    65536: 'm',
    131072: 'n',
    262144: 'o',
    524288: 'p',
    1048576: 'q',
    2097152: 'r',
    4194304: 's',
    8388608: 't',
    16777216: 'u',
    33554432: 'v',
    67108864: 'w',
    134217728: 'x',
    268435456: 'y',
    536870912: 'z',
    1073741824: 'aa',
    2147483648: 'ab',
    4294967296: 'ac',
    8589934592: 'ad',
    17179869184: 'ae',
    34359738368: 'af',
    68719476736: 'ag',
    137438953472: 'ah',
    274877906944: 'ai',
    549755813888: 'aj',
    1099511627776: 'ak',
    2199023255552: 'al',
    4398046511104: 'am',
    8796093022208: 'an',
    17592186044416: 'ao',
    35184372088832: 'ap',
    70368744177664: 'aq',
    140737488355328: 'administrator',
}

REVERSE_PERMISSIONS_DICT = {v: k for k, v in PERMISSIONS_DICT.items()}