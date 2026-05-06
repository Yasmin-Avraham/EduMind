import sys
import os
import asyncio

# Ensure the src directory is in the path
sys.path.append(os.getcwd())

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

    return df.to_json(orient="records", force_ascii=False)


@mcp.tool()
def get_student_analytics(student_id: int) -> str:
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


@mcp.tool()
def get_students(class_id: str) -> str:
    """
    Retrieves all students for a specific class from the database.
    Args:
    class_id (str): The unique ID of the class.
    """
    query = f"SELECT * FROM students WHERE class_id = '{class_id}'"
    df = execute_query_in_db(query)
    if df.empty:
        return f"No students found for the class '{class_id}'"

    return df.to_json(orient="records", force_ascii=False)


@mcp.tool()
def get_class_analytics(class_id: str) -> str:
    """
    Intended for teachers only. Computes cross-class analytics for the entire class.
    Args:
        class_id: Unique ID of the class.
    """
    query = f"""
        SELECT g.subject, ROUND(AVG(g.grade), 2) as avg_grade, MAX(g.grade) as max_grade
        FROM grades g
        JOIN students s ON g.student_id = s.student_id
        WHERE s.class_id = '{class_id}'
        GROUP BY g.subject
    """
    df = execute_query_in_db(query)

    if df.empty:
        return f"No information for class {class_id}."

    return f"class analytics report ({class_id}):\n" + df.to_string(index=False)


def execute_query_in_db(query: str):
    db_connection = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, db_connection)
    finally:
        db_connection.close()
    return df


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    mcp.run()