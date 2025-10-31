from fastapi import FastAPI
from api.users import router as users_router
from api.portfolio import router as portfolio_router
from api.chat import router as chat_router
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(
    title="IRA-RMD Portfolio Advisor",
    description="Backend API for portfolio management, analysis, and chat with AI agents.",
    version="1.0.0",
)

# Register routers
app.include_router(users_router)
app.include_router(portfolio_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "IRA-RMD Portfolio Advisor API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
