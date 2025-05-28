# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

print("DATABASE_URL:", os.environ.get('DATABASE_URL'))
print("SECRET_KEY:", os.environ.get('SECRET_KEY'))
print("MAIL_USERNAME:", os.environ.get('MAIL_USERNAME'))
print("MAIL_PASSWORD:", os.environ.get('MAIL_PASSWORD'))