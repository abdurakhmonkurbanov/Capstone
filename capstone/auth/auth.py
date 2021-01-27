import json
from os import getenv
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from dotenv import load_dotenv

from capstone.config import AUTH_URL, API_AUDIENCE


load_dotenv()

AUTH0_DOMAIN = AUTH_URL
ALGORITHMS = ["RS256"]
API_AUDIENCE =  API_AUDIENCE


class AuthError(Exception):
    # init our AUTH ERRO class: error and status code
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """
    GET AUTH HEADER
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {"code": "authorization_header_missing",
            "description": "Authorization header is expected.",},
            401,)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": 'Authorization header must start with "Bearer".',
            },
            401,
        )

    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header", 
                        "description": "Token not found."}, 401)

    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header must be bearer token.",},401,)
    return parts[1]


def check_permissions(permission, payload):
    """ 
    CHECK USER PERMISSION before doing smth
    """

    if "permissions" not in payload: #if permission not found
        raise AuthError(
            {"code": "invalid_claims",
             "description": "Permissions not included in JWT.",},400,)

    elif permission not in payload["permissions"]: # return forbidden
        raise AuthError({"code": "unauthorized", 
                         "description": "Permission not found."}, 403) 

    return True


def verify_decode_jwt(token):
    """ 
    Fetches JSON web key set from Auth0
    """
    # Verify token
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    if "kid" not in unverified_header:
        raise AuthError({"code": "invalid_header", 
                        "description": "Authorization malformed."}, 401)

    rsa_key = {} # empty data

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )
            return payload

        # Raise Error

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token expired."}, 401
            )

        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                             "description": "Incorrect claims.\
                             Please, check the audience and issuer.",},401,)

        except Exception:
            raise AuthError({"code": "invalid_header",
                            "description": "Unable to parse authentication token.",},400,)

    # If no payload has been returned yet, raise error.
    raise AuthError({"code": "invalid_header",
                     "description": "Unable to find the appropriate key.",},400)


def auth_required(permission=""):
    def auth_required_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)

            except:
                raise AuthError(
                    {"code": "unauthorized", "description": "Permissions not found"},
                    401,)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)
        return wrapper
    return auth_required_decorator
