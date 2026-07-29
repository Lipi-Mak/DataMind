from utils.insight_generator import explain_answer

question = "What is the average salary?"

answer = "The average value of Salary is 61333.33."

response = explain_answer(
    question,
    answer
)

print(response)