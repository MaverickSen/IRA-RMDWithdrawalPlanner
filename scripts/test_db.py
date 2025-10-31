from db.connection import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT NOW();")
        print(cur.fetchone())
