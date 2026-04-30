from src.flows.edu_flow import EduMindFlow
import asyncio


async def run_simulation():
    print("--- תחילת סימולציית מערכת EduMind ---")

    # סימולציה 1: הורה שואל על הבן שלו (שילוב SQL ו-RAG)
    print("\n[Scenario 1: Parent Query]")
    parent_flow = EduMindFlow()
    parent_flow.state.user_role = "parent"
    parent_flow.state.student_id = 123456789
    parent_flow.state.query = "How is my son progressing? Are there any comments from the teacher?"

    parent_flow.kickoff()
    print(f"Final Response to Parent:\n{parent_flow.state.final_response}")

    print("-" * 30)

    # סימולציה 2: מורה שואל על כל הכיתה (גישה ל-SQL כיתתי)
    print("\n[Scenario 2: Teacher Query]")
    teacher_flow = EduMindFlow()
    teacher_flow.state.user_role = "teacher"
    teacher_flow.state.class_id = "Class_grade_D_2"
    teacher_flow.state.query = "What is the class average and are there any students with unusual behavior comments?"

    teacher_flow.kickoff()
    print(f"Final Response to Teacher:\n{teacher_flow.state.final_response}")


if __name__ == "__main__":
    asyncio.run(run_simulation())