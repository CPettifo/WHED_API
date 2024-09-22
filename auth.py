import logging
import os
from urllib.request import urlopen
import azure.functions as func
import json
from jose import jwt

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
API_AUDIENCE = os.environ["AUTH0_API_AUDIENCE"]
ALGORITHMS = ["RS256"]


def _get_rsa_keys(token):
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    
    unverified_header = jwt.get_unverified_header(token)
    try: 
        kid = unverified_header["kid"]
    except Exception as e:
        raise Exception("Error: could not find kid in token")
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    raise Exception("Error: could not find rsa key for kid: "+kid)

def protected(fn):
    def wrapper(req: func.HttpRequest) -> func.HttpResponse:
        try:
            tokenHeader = req.headers.get('Authorization')
            if not tokenHeader:
                return func.HttpResponse(
                    "Error: token not found",
                    status_code=401
                )
            headerParts = tokenHeader.split(" ")
            if len(headerParts) != 2:
                return func.HttpResponse(
                    "Error: invalid token format",
                    status_code=401
                )
            if headerParts[0].lower() != "bearer":
                return func.HttpResponse(
                    "Error: invalid token type",
                    status_code=401
                )
            token = headerParts[1]
            try: 
                rsa_keys = _get_rsa_keys(token)
            except Exception as e:
                return func.HttpResponse(
                    f"Error: {e}",
                    status_code=401
                )

            if rsa_keys:
                try:
                    payload = jwt.decode(
                        token,
                        key= rsa_keys,
                        algorithms=ALGORITHMS,
                        audience=API_AUDIENCE,
                        issuer="https://"+AUTH0_DOMAIN+"/"
                    )
                except jwt.ExpiredSignatureError:
                    return func.HttpResponse(
                        "Error: token expired",
                        status_code=401
                    )
                except jwt.JWTClaimsError:
                    return func.HttpResponse(
                        "Error: invalid claims",
                        status_code=401
                    )
                except Exception as e:
                    return func.HttpResponse(
                        f"Error: {e}",
                        status_code=401
                    )
                logging.info(f"User {payload.get('sub')} accessed {fn.__name__}")
                return fn(req, current_user=payload)
            
            return func.HttpResponse(
                "Error: invalid token",
                status_code=401
            )

        except Exception as e:
            logging.error(f"Error verify token: {e}")
            return func.HttpResponse(
                f"Error: {e}",
                status_code=401
            )
    wrapper.__name__ = fn.__name__
    return wrapper