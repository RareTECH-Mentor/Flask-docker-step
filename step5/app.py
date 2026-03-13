from flask import Flask
import pymysql

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello Docker Flask + MySQL"


@app.route("/db")
def db_test():
    conn = pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
    )

    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()

    conn.close()

    return f"MySQL Version: {result}"


if __name__ == "__main__":
    app.run(host="0.0.0.0")

