import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_connection
from workflows.portfolio_workflow import PortfolioWorkflow
from config.settings import settings
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    user_id: int
    message: str


@router.post("/")
def chat_with_llm(request: ChatRequest):
    """
    Chat with the LLM about the user's portfolio.
    Handles validation, DB I/O, and passes data to PortfolioWorkflow.
    """
    try:
        user_id = request.user_id
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing OpenAI API key.")

        with get_connection() as conn:
            with conn.cursor() as cur:
                # Validate user existence
                cur.execute("SELECT 1 FROM users WHERE id = %s;", (user_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="User not found.")

                # Fetch portfolio
                cur.execute(
                    """
                    SELECT stock_name, ticker, quantity, recommendation, uploaded_at
                    FROM portfolio
                    WHERE user_id = %s
                    ORDER BY uploaded_at DESC;
                    """,
                    (user_id,),
                )
                portfolio_rows = cur.fetchall()
                if not portfolio_rows:
                    raise HTTPException(status_code=404, detail="No portfolio found for this user.")

                portfolio = [
                    {
                        "stock_name": r[0],
                        "ticker": r[1],
                        "quantity": r[2],
                        "recommendation": r[3],
                        "uploaded_at": r[4],
                    }
                    for r in portfolio_rows
                ]

                # Get chat history (last 10 messages)
                cur.execute(
                    """
                    SELECT role, message
                    FROM chat_history
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 10;
                    """,
                    (user_id,),
                )
                chat_history = [{"role": r, "content": m} for r, m in cur.fetchall()][::-1]

        # Run the workflow
        workflow = PortfolioWorkflow(api_key=api_key)
        answer = workflow.handle_query(user_id, request.message, portfolio, chat_history)

        # Save new chat messages
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s);",
                    (user_id, "user", request.message),
                )
                cur.execute(
                    "INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s);",
                    (user_id, "assistant", answer),
                )
                conn.commit()

        return {"response": answer, "context_used": len(chat_history)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
