from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import sqlite3
import io
from src.config import DB_PATH
from fastapi import Form

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


@app.post("/upload/teacher_notes")
async def upload_notes(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # validate columns
    required = ['student_id', 'class_id', 'note_text', 'date']
    if not all(col in df.columns for col in required):
        raise HTTPException(status_code=400, detail="Missing required columns")

    #RAG server
    from src.mcp_servers.rag_server import add_teacher_note

    success_count = 0
    for _, row in df.iterrows():
        add_teacher_note(
            student_id=row['student_id'],
            class_id=row['class_id'],
            note_text=row['note_text'],
            date=row['date']
        )
        success_count += 1

    return {"message": f"Successfully indexed {success_count} notes into RAG."}


@app.post("/upload/student_note_text")
async def upload_student_note_txt(
        student_id: int = Form(...),
        class_id: str = Form(...),
        file: UploadFile = File(...)
):

    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="please upload only txt file")

    try:
        contents = await file.read()
        note_text = contents.decode("utf-8")

        # RAG server
        from src.mcp_servers.rag_server import add_teacher_note
        from datetime import datetime

        current_date = datetime.now().strftime("%Y-%m-%d")

        add_teacher_note(
            student_id=student_id,
            class_id=class_id,
            note_text=note_text,
            date=current_date
        )

        return {
            "status": "success",
            "message": f"the note for student {student_id} saved successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error upload the file: {str(e)}")