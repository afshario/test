import os

DSN = os.getenv("DSN", "")
RATE = os.getenv("RATE")
APP_MESSAGE = os.getenv("APP_MESSAGE", "APP_MESSAGE is not set")
APP_ENV = os.getenv("APP_ENV", "APP_ENV is not set")
SECRET_GREETING = os.getenv("SECRET_GREETING", "SECRET_GREETING is not set")