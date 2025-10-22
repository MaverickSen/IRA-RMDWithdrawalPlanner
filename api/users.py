from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from db.connection import get_connection
import psycopg2

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    age: int = Field(..., gt=0)


@router.post("/register")
def register_user(user: UserCreate):
    """Register a new user."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check if the email already exists
            cur.execute("SELECT id FROM users WHERE email = %s;", (user.email,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="Email already registered. Please log in instead.")

            try:
                cur.execute(
                    """
                    INSERT INTO users (email, first_name, last_name, age)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (user.email, user.first_name, user.last_name, user.age),
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                return {"message": "User registered successfully", "user_id": user_id}
            except psycopg2.Error as e:
                conn.rollback()
                raise HTTPException(status_code=400, detail=f"Database error: {e.pgerror}")
            except Exception as e:
                conn.rollback()
                raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


class UserLogin(BaseModel):
    email: EmailStr


@router.post("/login")
def login_user(user: UserLogin):
    """Log in an existing user."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, first_name, last_name, age FROM users WHERE email = %s;",
                (user.email,),
            )
            result = cur.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="User not found. Please register first.")

            user_data = {
                "user_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "age": result[3],
                "email": user.email,
            }

            return {"message": "Login successful", "user": user_data}


@router.get("/{user_id}")
def get_user_by_id(user_id: int):
    """Fetch user details by user_id (optional helper)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, first_name, last_name, email, age FROM users WHERE id = %s;",
                (user_id,),
            )
            result = cur.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="User not found.")

            return {
                "user_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "email": result[3],
                "age": result[4],
            }
