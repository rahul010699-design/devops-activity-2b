import os

import psycopg2
from google.cloud import secretmanager


def get_database_password():
    client = secretmanager.SecretManagerServiceClient()
    secret_path = (
        f"projects/{os.environ['GCP_PROJECT_ID']}"
        f"/secrets/{os.environ['DB_PASSWORD_SECRET']}/versions/latest"
    )
    response = client.access_secret_version(
        request={"name": secret_path}
    )
    return response.payload.data.decode("utf-8")


def main():
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=get_database_password(),
        connect_timeout=10,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL
                    );
                """)
        print("Database initialization completed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
