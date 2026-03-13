from flask import Flask, request, jsonify, render_template
import pymysql

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello Docker Flask + MySQL (templates step)"


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


@app.route("/users", methods=["POST"])
def create_user():
    name = request.form.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
    )

    with conn.cursor() as cursor:
        sql = "INSERT INTO users (name) VALUES (%s)"
        cursor.execute(sql, (name,))
        conn.commit()

    conn.close()

    return jsonify({"name": name}), 201


@app.route("/users", methods=["GET"])
def list_users():
    conn = pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
    )

    with conn.cursor() as cursor:
        sql = "SELECT id, name FROM users"
        cursor.execute(sql)
        rows = cursor.fetchall()

    conn.close()

    users = [{"id": row[0], "name": row[1]} for row in rows]

    return jsonify(users)


@app.route("/users/new", methods=["GET"])
def new_user_form():
    return render_template("new_user.html")


@app.route("/users/list", methods=["GET"])
def user_list_page():
    conn = pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
    )

    with conn.cursor() as cursor:
        sql = "SELECT id, name FROM users"
        cursor.execute(sql)
        rows = cursor.fetchall()

    conn.close()

    users = [{"id": row[0], "name": row[1]} for row in rows]

    return render_template("user_list.html", users=users)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

