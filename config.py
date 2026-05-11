import os

# Fix: Render provides postgres:// but psycopg3 requires postgresql://
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kyc_database_user:0y1ec6hDHNG6I4VWJzcht6H27igeKvrV@dpg-d80l8crrjlhs73ae04rg-a.virginia-postgres.render.com/kyc_database_ozpi"
).replace("postgres://", "postgresql://", 1)