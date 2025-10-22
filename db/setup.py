import psycopg2
from connection import get_connection

def create_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    age INT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Portfolio table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id) ON DELETE CASCADE,
                    stock_name VARCHAR(255),
                    ticker VARCHAR(20),
                    quantity INT,
                    recommendation TEXT,
                    uploaded_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Chat history table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    role VARCHAR(10) CHECK (role IN ('user', 'assistant')),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            conn.commit()
            print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()
