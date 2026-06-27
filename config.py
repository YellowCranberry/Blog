import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    # ------------------------------------------------------------------
    # Hybrid Search Extension Configuration
    # ------------------------------------------------------------------
    # PostgreSQL vector DB URL (required for search to work)
    HYBRID_SEARCH_DB_URL = (
        os.environ.get('HYBRID_SEARCH_DB_URL')
        or 'postgresql+psycopg://postgres:1234@localhost:5433/vectordb'
    )
    # pgvector collection name (think of it like a table namespace)
    HYBRID_SEARCH_COLLECTION = (
        os.environ.get('HYBRID_SEARCH_COLLECTION') or 'blog_search_docs'
    )
    # HuggingFace embedding model — change to a larger model for better quality
    HYBRID_SEARCH_EMBEDDING_MODEL = (
        os.environ.get('HYBRID_SEARCH_EMBEDDING_MODEL')
        or 'sentence-transformers/all-MiniLM-L6-v2'
    )
    # Set to '' or remove to disable the local LLM (search-only mode)
    HYBRID_SEARCH_LLM_MODEL = os.environ.get('HYBRID_SEARCH_LLM_MODEL', '')
    # How many metrics events to keep in memory for the admin dashboard
    HYBRID_SEARCH_METRICS_MAXLEN = 200
    # Logging level for all hybrid_search.* loggers
    HYBRID_SEARCH_LOG_LEVEL = os.environ.get('HYBRID_SEARCH_LOG_LEVEL', 'INFO')

    # Admin password for protected routes like /admin/search-metrics
    # Override with ADMIN_PASSWORD environment variable in production
    ADMIN_METRICS_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'user_data.sqlite')



class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig
}    

