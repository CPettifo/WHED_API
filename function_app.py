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

@app.route(route="currency", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@auth.protected
def get_currencies(req: func.HttpRequest, current_user) -> func.HttpResponse:
    with db_pool.get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT currency_name, currency_code FROM cosc320_whed_lex_currency")
            result = cursor.fetchall()

    return func.HttpResponse(
        json.dumps(result),
        status_code=200
    )


@app.route(route="currency/{currency_code}", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
@auth.protected
def delete_currency(req: func.HttpRequest, current_user) -> func.HttpResponse:

    currency_code = req.route_params.get('currency_code')
    if not isinstance(currency_code, str):
        return func.HttpResponse(
            "currency_code is required",
            status_code=400
        )

    if not currency_code.isalpha() or len(currency_code) != 3:
        return func.HttpResponse(
            "currency_code should be three capitalized alphabetic characters",
            status_code=400
        )

    try:
        with db_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    DELETE FROM cosc320_whed_lex_currency
                    WHERE currency_code = %s
                    """,
                    (currency_code,)
                )
                connection.commit()

    except Exception as e:
        logging.error(f"Error deleting currency: {e}")
        return func.HttpResponse(
            "Internal Error",
            status_code=500
        )

    return func.HttpResponse(
        status_code=204
    )


@app.route(route="currency", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
@auth.protected
def post_currency(req: func.HttpRequest, current_user) -> func.HttpResponse:

    body = req.get_json()
    if not body:
        return func.HttpResponse(
            "Invalid request",
            status_code=400
        )
    
    currency_code = body.get('currency_code')
    currency_name = body.get('currency_name')


    if not isinstance(currency_name, str):
        return func.HttpResponse(
            "currency_name is required",
            status_code=400
        )
    
    # currency_code should be a string
    if not isinstance(currency_code, str):
        return func.HttpResponse(
            "currency_code is required",
            status_code=400
        )

    if not currency_code.isalpha() or len(currency_code) != 3:
        return func.HttpResponse(
            "currency_code should be three capitalized alphabetic characters",
            status_code=400
        )
    
    if not currency_name.isalpha() and len(currency_name) > 0:
        return func.HttpResponse(
            "currency_name should be alphabetic characters",
            status_code=400
        )

    try:
        with db_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO cosc320_whed_lex_currency
                        (currency_name, currency_code)
                    VALUES
                        (%s, %s)
                    """,
                    (currency_name, currency_code)
                )
                cursor
                connection.commit()

    except Exception as e:
        logging.error(f"Error inserting currency: {e}")
        return func.HttpResponse(
            "Internal Error",
            status_code=500
        )

    return func.HttpResponse(
        status_code=201
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
    

