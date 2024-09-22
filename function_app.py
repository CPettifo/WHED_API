import azure.functions as func
import json
import logging
import mysql.connector
import os
from auth0.authentication import GetToken
from dotenv import load_dotenv
load_dotenv()
import auth

app = func.FunctionApp()

db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_size=1,
    host=os.environ["MYSQL_HOST"],
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    database=os.environ["MYSQL_DATABASE"]
)

@app.route(route="currency", auth_level=func.AuthLevel.ANONYMOUS)
@auth.protected
def currency(req: func.HttpRequest, current_user) -> func.HttpResponse:
    with db_pool.get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT currency_name, currency_code FROM cosc320_whed_lex_currency")
            result = cursor.fetchall()

    return func.HttpResponse(
        json.dumps(result),
        status_code=200
    )
    

@app.route(route="login", auth_level=func.AuthLevel.ANONYMOUS)
def authenticate(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    try:
        token = GetToken(
            auth.AUTH0_DOMAIN,
            'nyQjkHxC5rAJkb1QfwDWaSq8JvQeIPRo',
            client_secret='NkKoIAxnZM5fENFQaLuilkWkL2q5GJk75xtlYGLq6hq-NTpsyqTYVKeQ7kBzFpji'
        )
    except Exception as e:
        logging.error(f"Error connect auth0: {e}")
        return func.HttpResponse(
            f"Error: invalid configuration",
            status_code=500
        )
    try:
        result = token.login(
            username=body.get('username'),
            password=body.get('password'),
            audience=auth.API_AUDIENCE,
            realm='Username-Password-Authentication'
        )
        return func.HttpResponse(
            json.dumps({'access_token': result.get("access_token")}),
            status_code=200
        )
    except Exception as e:  
        logging.warning(f"Error login: {e}")
        return func.HttpResponse(
            f"Internal Error",
            status_code=500
        )
    

