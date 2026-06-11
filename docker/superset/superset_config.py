SECRET_KEY = "threatlake-super-secret-key"

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://threatlake:threatlake@postgres:5432/superset"

WTF_CSRF_ENABLED = False
TALISMAN_ENABLED = False
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
}

