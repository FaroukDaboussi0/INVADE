from datetime import timedelta
from pymongo import MongoClient

class Config:
    SECRET_KEY = 'BCG-e2380a'
    BASE_URL = 'http://127.0.0.1:27017'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'faroukdaboussi2009@gmail.com'
    MAIL_PASSWORD = 'uswm lmkn fnmb xuih'
    MONGODB_SETTINGS = {
        'db' : 'salem',
        'host' : 'localhost',
        'port' : 27017
    }

    JWT_SECRET_KEY = 'BCG-e2380a'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_REFRESH_TOKEN_EXPIRES = 86400
    JWT_TOKEN_LOCATION = 'headers'
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_CSRF_CHECK_FORM = True
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_ALGORITHM = 'HS256'


    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = MongoClient('mongodb://localhost:27017/')
    SESSION_MONGODB_DB = 'salem'
    SESSION_MONGODB_COLLECT = 'sessions'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7) 
    EXCLUDED_ROUTES = ["auth.register","auth.login","auth.verify_account"]
    
  

