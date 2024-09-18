from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# MySQL Configuration
# For now it is a test localhost
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "whed_prive"

mysql = MySQL(app)

# Test to get orgIDs
@app.route("/org_ids", methods = ["POST"])
def get_ids():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT OrgID FROM whed_org")
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Successfully returned orgids"})

if __name__ == "__main__":
    app.run(debug = True)

    