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
    db_connection = sqlite3.connect(DB_PATH)
    query = f"SELECT subject, grade, date FROM grades WHERE student_id = {student_id}"
    df = pd.read_sql_query(query, db_connection)
    db_connection.close()

    if df.empty:
        return f"No grades found for the student {student_id}"

    return  df.to_json(orient="records", force_ascii=False)


if __name__ == "__main__":
    mcp.run()