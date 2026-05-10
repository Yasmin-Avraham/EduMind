from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import io
from fastapi import Form
from pydantic import BaseModel
import sqlite3
from src.config import DB_PATH
from typing import Optional
import jwt
from src.flows.edu_flow import app_graph
app = FastAPI(title="EduMind API")
security = HTTPBearer()

class ClassRequest(BaseModel):
    class_id: str
    class_name: str

class StudentRequest(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    class_id: str
    parent_email: str
    parent_phone: str

class GradeRequest(BaseModel):
    student_id: int
    subject: str
    grade: int
    date: str

class ChatRequest(BaseModel):
    query: str
    student_id: Optional[int] = None
    class_id: Optional[str] = None


async def get_current_user_role(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("role"), payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Token")
@app.get("/")
def read_root():
    return {"message": "Welcome to EduMind API"}

@app.post("/admin/classes", tags=["Admin"])
async def create_class(class_data: ClassRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO classes (class_id, class_name) VALUES (?, ?)",
            (class_data.class_id, class_data.class_name)
        )
        conn.commit()
        return {"message": f"Class {class_data.class_id} created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Class ID already exists")
    finally:
        conn.close()
@app.post("/admin/students", tags=["Admin"])
async def create_student(student_data: StudentRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (student_id, first_name, last_name, class_id,parent_email,parent_phone) VALUES (?, ?, ?, ?,?,?)",
            (student_data.student_id, student_data.first_name, student_data.last_name, student_data.class_id, student_data.parent_email, student_data.parent_phone)
        )
        conn.commit()
        return {"message": f"Student {student_data.first_name} added to class {student_data.class_id}"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Student ID already exists or Class ID not found")
    finally:
        conn.close()
@app.post("/admin/grades", tags=["Admin"])
async def add_grade(data: GradeRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO grades (student_id, subject, grade, date) VALUES (?, ?, ?, ?)",
            (data.student_id, data.subject, data.grade, data.date)
        )
        conn.commit()
        return {"status": "success", "message": f"Grade added for student {data.student_id}"}
    finally:
        conn.close()
@app.post("/admin/upload/grades_csv", tags=["Admin"])
async def upload_grades_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a CSV file only.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))

        required_columns = ['student_id', 'subject', 'grade', 'date']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"The file must contain the columns: {required_columns}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        success_count = 0
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO grades (student_id, subject, grade, date) VALUES (?, ?, ?, ?)",
                (int(row['student_id']), str(row['subject']), int(row['grade']), str(row['date']))
            )
            success_count += 1

        conn.commit()
        return {"status": "success", "message": f"The grades uploaded successfully {success_count} "}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        conn.close()
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
        file: UploadFile = File(...)):

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
@app.post("/chat")
async def chat_endpoint(
        request: ChatRequest,
        auth: HTTPAuthorizationCredentials = Depends(security)
    ):
    token = auth.credentials
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        role = payload.get("role")
        user_id = payload.get("user_id")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid Token")
    initial_state = {
        "query": request.query,
        "user_role": role,
        "student_id": request.student_id,
        "class_id": request.class_id,
        "user_id": user_id,
        "analysis_result": "",
        "final_response": "",
        "route_signal": ""
    }
    try:
        final_state = await app_graph.ainvoke(initial_state)
        print(final_state["final_response"])
        return {"response": final_state["final_response"]}
    except Exception as e:
        print(f"--- API ERROR: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))





