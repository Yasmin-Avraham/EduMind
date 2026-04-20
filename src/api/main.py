from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import sqlite3
import io
from src.config import DB_PATH

app = FastAPI(title="EduMind API")


@app.get("/")
def read_root():
    return {"message": "Welcome to EduMind API"}


@app.post("/upload/students")
async def upload_students(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Please uploade only csv file')

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        required_columns = ['student_id', 'first_name', 'last_name', 'class_id', 'parent_email']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"The file must contain: {required_columns}")

        conn = sqlite3.connect(DB_PATH)
        df.to_sql('students', conn, if_exists='append', index=False)
        conn.close()

        return {"message": f" {len(df)} students upload successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error to process the file: {str(e)}")


# נתיב נוסף להעלאת ציונים
@app.post("/upload/grades")
async def upload_grades(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please uploade only csv file")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # בדיקת עמודות לציונים
        required_columns = ['student_id', 'subject', 'grade', 'date']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"The file must contain: {required_columns}")

        conn = sqlite3.connect(DB_PATH)
        df.to_sql('grades', conn, if_exists='append', index=False)
        conn.close()

        return {"message": f" {len(df)} grades upload successfully "}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error to process the file: {str(e)}")