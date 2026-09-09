from utils.question_answerer import understand_question

questions = [

    "How much do employees earn?",

    "Which department has the most employees?",

    "How many rows are there?",

    "What's the highest salary?",

    "Average age?"

]

for q in questions:

    print(q)

    print(
        understand_question(q)
    )

    print("-" * 40)