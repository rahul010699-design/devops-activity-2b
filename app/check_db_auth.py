import os
import sys

import psycopg2
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
secret_path = (
    f"projects/{os.environ['GCP_PROJECT_ID']}"
    f"/secrets/{os.environ['DB_PASSWORD_SECRET']}/versions/latest"
)
secret = client.access_secret_version(request={"name": secret_path})
password = secret.payload.data.decode("utf-8")

try:
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=password,
        connect_timeout=10,
    )
    connection.close()
    print("DATABASE_AUTHENTICATION_SUCCESS")
except Exception as exc:
    print(f"DATABASE_AUTHENTICATION_FAILED: {type(exc).__name__}")
    sys.exit(1)
