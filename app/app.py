import os
from functools import lru_cache

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


@lru_cache(maxsize=1)
def get_database_password():
    # Local Docker Compose uses DB_PASSWORD.
    password = os.getenv("DB_PASSWORD")
    if password:
        return password

    # GKE uses Workload Identity to access Secret Manager.
    project_id = os.getenv("GCP_PROJECT_ID")
    secret_id = os.getenv("DB_PASSWORD_SECRET")

    if not project_id or not secret_id:
        raise RuntimeError(
            "Configure DB_PASSWORD for local development, or set "
            "GCP_PROJECT_ID and DB_PASSWORD_SECRET for GKE."
        )

    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    secret_path = (
        f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    )

    response = client.access_secret_version(
        request={"name": secret_path}
    )

    return response.payload.data.decode("utf-8")

def get_db_connection():
    required_settings = ("DB_HOST", "DB_NAME", "DB_USER")
    missing_settings = [
        name for name in required_settings if not os.getenv(name)
    ]

    if missing_settings:
        raise RuntimeError(
            "Missing required database settings: "
            + ", ".join(missing_settings)
        )

    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.getenv("DB_PORT", "5432"),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=get_database_password(),
        connect_timeout=5,
    )
@app.route("/")
def home():
   return "DevOps Activity 2B - Flask API is running!"

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/users", methods=["GET"])
def get_users():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email
                FROM users
                ORDER BY id
                """
            )
            users = cursor.fetchall()

        return jsonify([
            {"id": user[0], "name": user[1], "email": user[2]}
            for user in users
        ])

    finally:
        connection.close()


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400

    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "email is required"}), 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email)
                VALUES (%s, %s)
                RETURNING id
                """,
                (name.strip(), email.strip()),
            )
            user_id = cursor.fetchone()[0]

        connection.commit()

        return jsonify({
            "id": user_id,
            "name": name.strip(),
            "email": email.strip(),
        }), 201

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )

# import os
# import psycopg2
# from flask import Flask, jsonify, request

# app = Flask(__name__)


# def get_db_connection():
#     return psycopg2.connect(
#         host=os.getenv("DB_HOST", "db"),
#         port=os.getenv("DB_PORT", "5432"),
#         database=os.getenv("DB_NAME", "activity2a"),
#         user=os.getenv("DB_USER", "postgres"),
#         password=os.getenv("DB_PASSWORD", "postgres"),
#     )
# @app.route("/")
# def home():
#     return "DevOps Activity 2A - Flask API is running!"


# @app.route("/health")
# def health():
#     return jsonify({
#         "status": "healthy"
#     })


# @app.route("/users", methods=["GET"])
# def get_users():
#     connection = get_db_connection()

#     try:
#         cursor = connection.cursor()

#         cursor.execute(
#             """
#             SELECT id, name, email
#             FROM users
#             ORDER BY id
#             """
#         )

#         users = cursor.fetchall()

#         result = []

#         for user in users:
#             result.append({
#                 "id": user[0],
#                 "name": user[1],
#                 "email": user[2]
#             })

#         cursor.close()

#         return jsonify(result)

#     finally:
#         connection.close()



# @app.route("/users", methods=["POST"])
# def create_user():
#     data = request.get_json(silent=True)

#     if not isinstance(data, dict):
#         return jsonify({
#             "error": "A valid JSON object is required"
#         }), 400

#     name = data.get("name")
#     email = data.get("email")

#     if not isinstance(name, str) or not name.strip():
#         return jsonify({
#             "error": "name is required"
#         }), 400

#     if not isinstance(email, str) or not email.strip():
#         return jsonify({
#             "error": "email is required"
#         }), 400

#     connection = get_db_connection()

#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 """
#                 INSERT INTO users (name, email)
#                 VALUES (%s, %s)
#                 RETURNING id
#                 """,
#                 (name.strip(), email.strip())
#             )

#             user_id = cursor.fetchone()[0]
#             connection.commit()

#         return jsonify({
#             "id": user_id,
#             "name": name.strip(),
#             "email": email.strip()
#         }), 201

#     finally:
#         connection.close()





# if __name__ == "__main__":
#     app.run(
#         host="0.0.0.0",
#         port=int(os.getenv("PORT", "5000")),
#         debug=False,
#     )








# # @app.route("/users", methods=["POST"])
# # def create_user():
# #     data = request.get_json(silent=True)

# #     if not isinstance(data, dict):
# #         return jsonify({
# #             "error": "A valid JSON object is required"
# #         }), 400

# #     name = data.get("name")
# #     email = data.get("email")

# #     if not isinstance(name, str) or not name.strip():
# #         return jsonify({
# #             "error": "name is required"
# #         }), 400

# #     if not isinstance(email, str) or not email.strip():
# #         return jsonify({
# #             "error": "email is required"
# #         }), 400

# #     connection = get_db_connection()

# #     try:
# #         with connection.cursor() as cursor:
# #             cursor.execute(
# #                 """
# #                 INSERT INTO users (name, email)
# #                 VALUES (%s, %s)
# #                 RETURNING id
# #                 """,
# #                 (name.strip(), email.strip())
# #             )

# #             user_id = cursor.fetchone()[0]
# #             connection.commit()

# #         return jsonify({
# #             "id": user_id,
# #             "name": name.strip(),
# #             "email": email.strip()
# #         }), 201

# #     finally:
# #         connection.close()
