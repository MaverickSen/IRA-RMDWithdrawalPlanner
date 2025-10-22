from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from db.connection import get_connection
import pandas as pd
import io


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/upload-excel")
async def upload_portfolio_excel(user_id: int = Form(...), file: UploadFile = File(...)):
    """
    Upload a portfolio Excel file for a user.
    - Excel must contain columns: stock_name, ticker, quantity
    - Extra columns will be ignored
    - Recommendation remains NULL until updated later
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")

    try:
        # Read Excel file into pandas DataFrame
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        required_cols = {"stock_name", "ticker", "quantity"}
        missing = required_cols - set(df.columns)
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

        # Keep only necessary columns
        df = df[list(required_cols)]

        # Insert into DB
        with get_connection() as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    cur.execute(
                        """
                        INSERT INTO portfolio (user_id, stock_name, ticker, quantity)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (user_id, row["stock_name"], row["ticker"], int(row["quantity"])),
                    )
            conn.commit()

        return {"message": "Portfolio uploaded successfully", "rows_inserted": len(df)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
