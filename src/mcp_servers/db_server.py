from mcp.server.fastmcp import FastMCP
import sqlite3
import pandas as pd
from src.config import DB_PATH

mcp = FastMCP("EduData")

@mcp.tool()
def get_student_grades(student_id: int) -> str:
    """
    Retrieves all grades for a specific student from the database.
    Args:
    student_id (int): The unique ID of the student.
    """
    query = f"SELECT subject, grade, date FROM grades WHERE student_id = {student_id}"
    df = execute_query_in_db(query)

    if df.empty:
        return f"No grades found for the student {student_id}"

    return  df.to_json(orient="records", force_ascii=False)

@mcp.tool()
def get_student_analytics (student_id: int) -> str:
    """
    Calculates detailed statistical analytics for a student, grouped by subjects.
    Includes averages, min/max grades, and chronological history per subject.
    Args:
        student_id: The unique ID of the student.
    """
    query = f"""
        SELECT subject, grade, date 
        FROM grades 
        WHERE student_id = {student_id} 
        ORDER BY subject, date ASC
    """
    df = execute_query_in_db(query)
    if df.empty:
        return f"No grades found for the student {student_id}"

    report = [f"--- Analytic Report for student: {student_id} ---"]

    for subject, group in df.groupby('subject'):
        avg_grade = round(group['grade'].mean(), 2)
        max_grade = group['grade'].max()
        min_grade = group['grade'].min()
        history = ", ".join([f"{row['grade']} ({row['date']})" for _, row in group.iterrows()])

        subject_summary = (
            f"\nsubject: {subject}\n"
            f"  - avg: {avg_grade}\n"
            f"  - max_grade: {max_grade}\n"
            f"  - min_grade: {min_grade}\n"
            f"  - grades_history: {history}"
        )
        report.append(subject_summary)
    return "\n".join(report)

def execute_query_in_db(query:str):
    db_connection = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, db_connection)
    db_connection.close()
    return df

if __name__ == "__main__":
    mcp.run()