from flask import Flask, request, jsonify
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


@app.route("/users", methods=["POST"])
def create_user():
    """
    コマンド例:
    curl -X POST -d "name=Taro" http://localhost:5000/users
    """

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
        user_id = cursor.lastrowid

    conn.close()

    return jsonify({"id": user_id, "name": name}), 201


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


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
    )

    with conn.cursor() as cursor:
        sql = "SELECT id, name FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()

    conn.close()

    if row is None:
        return jsonify({"error": "user not found"}), 404

    user = {"id": row[0], "name": row[1]}
    return jsonify(user)


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = pymysql.connect(
        host="db",
        user="flaskuser",
        password="flaskpass",
        database="flaskdb",
    )

    with conn.cursor() as cursor:
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        conn.commit()
        deleted_count = cursor.rowcount

    conn.close()

    if deleted_count == 0:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"message": "user deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0")

