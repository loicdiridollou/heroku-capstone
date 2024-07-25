"""Authorization module."""

import json
from functools import wraps
from urllib.request import urlopen

from flask import request
from jose import ExpiredSignatureError, jwt
from jose.exceptions import JWTClaimsError

from config import auth0_config

AUTH0_DOMAIN = auth0_config["AUTH0_DOMAIN"]
ALGORITHMS = ["RS256"]
API_AUDIENCE = "image"


## AuthError Exception
"""
AuthError Exception
A standardized way to communicate auth failure modes
"""


class AuthError(Exception):
    """Custom Exception."""

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header


def get_token_auth_header():
    """Get token for header."""
    auth = request.headers.get("Authorization", None)

    if not auth:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected",
            },
            401,
        )

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must start with Bearer",
            },
            401,
        )

    elif len(parts) == 1:
        raise AuthError(
            {"code": "invalid_header", "description": "Token not found"}, 401
        )

    elif len(parts) > 2:
        raise AuthError(
            {"code": "invalid_header", "description": "Too many arguments"}, 401
        )

    return parts[1]


def check_permissions(permission, payload):
    """Ensure permissions are correct."""
    if "permissions" not in payload:
        raise AuthError(
            {"code": "unauthorized", "description": "Permission not included in JWT"},
            400,
        )

    if permission not in payload["permissions"]:
        raise AuthError(
            {"code": "unauthorized", "description": "Permission not found."},
            status_code=403,
        )
    return True


def verify_decode_jwt(token):
    """Decode json web token."""
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    if "kid" not in unverified_header:
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization malformed."}, 401
        )

    rsa_key = {}
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

        # Raise Error if token is not valide anymore.
        except ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token expired."}, 401
            ) from None

        # Raise Error if token is claiming wrong audience.
        except JWTClaimsError:
            raise AuthError(
                {
                    "code": "invalid_claims",
                    "description": "Incorrect claims. Please, check the audience and issuer.",
                },
                401,
            ) from None

        # In all other Error cases, give generic error message
        except Exception:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token.",
                },
                400,
            ) from None

    # If no payload has been returned yet, raise error.
    raise AuthError(
        {
            "code": "invalid_header",
            "description": "Unable to find the appropriate key.",
        },
        400,
    )


def requires_auth(permission=""):
    """Decode authorization token."""

    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
