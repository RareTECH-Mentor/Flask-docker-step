import os

from flask import Flask, request, jsonify, render_template
import pymysql

app = Flask(__name__)


DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "flaskuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "flaskpass")
DB_NAME = os.environ.get("DB_NAME", "flaskdb")


def get_connection():
  try:
      conn = pymysql.connect(
          host=DB_HOST,
          user=DB_USER,
          password=DB_PASSWORD,
          database=DB_NAME,
      )
      return conn
  except Exception as e:
      raise RuntimeError("database connection failed") from e


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "internal server error"}), 500


@app.route("/")
def hello():
    return "Hello Docker Flask + MySQL (config & error handling step)"


@app.route("/db")
def db_test():
    conn = get_connection()

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

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "INSERT INTO users (name) VALUES (%s)"
        cursor.execute(sql, (name,))
        conn.commit()

    conn.close()

    return jsonify({"name": name}), 201


@app.route("/users", methods=["GET"])
def list_users():
    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "SELECT id, name FROM users"
        cursor.execute(sql)
        rows = cursor.fetchall()

    conn.close()

    users = [{"id": row[0], "name": row[1]} for row in rows]

    return jsonify(users)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_connection()

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
    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        conn.commit()
        deleted_count = cursor.rowcount

    conn.close()

    if deleted_count == 0:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"message": "user deleted"}), 200


@app.route("/users/new", methods=["GET"])
def new_user_form():
    return render_template("new_user.html")


@app.route("/users/list", methods=["GET"])
def user_list_page():
    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "SELECT id, name FROM users"
        cursor.execute(sql)
        rows = cursor.fetchall()

    conn.close()

    users = [{"id": row[0], "name": row[1]} for row in rows]

    return render_template("user_list.html", users=users)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

