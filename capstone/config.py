from os import urandom, getenv
from dotenv import load_dotenv

from capstone.views import app, db


load_dotenv()

SECRET_KEY = urandom(32)
DATABASE_URL = getenv("DATABASE_URL")
TRACK_MODIFICATIONS = getenv("TRACK_MODIFICATIONS")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = TRACK_MODIFICATIONS
app.secret_key = SECRET_KEY

AUTH_URL = getenv("AUTH_URL")
API_AUDIENCE = getenv("API_AUDINCE")
CLIENT_ID = getenv("CLIENT_ID")
REDIRECT_URL = getenv("REDIRECT_URL")

auth0_url = f"{AUTH_URL}/authorize?audience={API_AUDIENCE}&response_type=token&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}"




