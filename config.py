import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'sql12.freesqldatabase.com'),
    'database': os.environ.get('DB_NAME', 'sql12821938'),
    'user': os.environ.get('DB_USER', 'sql12821938'),
    'password': os.environ.get('DB_PASS', 'CD29QJume5'),
    'port': 3306
}