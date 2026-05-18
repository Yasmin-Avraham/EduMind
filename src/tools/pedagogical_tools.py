from crewai.tools import tool


@tool("Grade Goal Calculator")
def calculate_required_grade(grades_string: str, target_average: int) -> str:
    """
    Calculates the exact grade a student needs on their next exam to reach a specific target average.

    Args:
        grades_string (str): A comma-separated string of current grades (e.g., '80, 95, 74').
        target_average (int): The desired average score the user wants to reach (e.g., 85).

    Returns:
        str: A clear, factual message indicating the required score or mathematical impossibility.
    """
    try:
        grades = [int(g.strip()) for g in grades_string.split(",") if g.strip().isdigit()]

        if not grades:
            return "Error: No valid numeric grades were provided for calculation."

        current_sum = sum(grades)
        current_count = len(grades)
        next_count = current_count + 1
        required_grade = (target_average * next_count) - current_sum

        if required_grade > 100:
            return f"Mathematically impossible. To reach an average of {target_average}, the student would need a score of {int(required_grade)} on the next test."
        elif required_grade < 0:
            return f"Excellent position! Even with a score of 0 on the next test, the student's average will remain above {target_average}."
        else:
            return f"To reach an average of {target_average}, the student must score at least {int(required_grade)} on the next exam."

    except Exception as e:
        return f"Error computing grade goal: {str(e)}"