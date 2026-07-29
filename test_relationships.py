import pandas as pd

from utils.relationship_detector import (
    detect_relationships,
    generate_relationship_findings
)


data = {
    "Price": [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ],

    "Demand": [
        100,
        90,
        80,
        70,
        60,
        50,
        40,
        30
    ]
}


df = pd.DataFrame(data)


relationships = detect_relationships(df)


print("\nDetected Relationships:\n")

for relationship in relationships:

    print(relationship)


findings = generate_relationship_findings(
    relationships
)


print("\nFactual Findings:\n")

for finding in findings:

    print(finding)