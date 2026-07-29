from utils.insight_generator import (
    generate_ai_relationship_explanations
)


relationship_findings = [

    "Price and Demand show a strong negative "
    "correlation with a correlation coefficient of -0.85."

]


explanations = (
    generate_ai_relationship_explanations(
        relationship_findings
    )
)


print("AI Relationship Explanations:\n")


for explanation in explanations:

    print(explanation)

    print("\n" + "-" * 50)