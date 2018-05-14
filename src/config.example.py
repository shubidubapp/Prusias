class Config(object):
    DEBUG = True
    SECRET_KEY = "HELLO_WORLD"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db'
    CACHE_TYPE = "redis"


class ProductionConfig(Config):
    DEBUG = True
