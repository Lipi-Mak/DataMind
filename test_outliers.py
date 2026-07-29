import pandas as pd

from utils.outlier_detector import detect_outliers


data = {
    "Salary": [
        45000,
        47000,
        49000,
        50000,
        51000,
        52000,
        250000,
        300000
    ]
}


df = pd.DataFrame(data)


outliers = detect_outliers(df)


print("Detected Outliers:")
print(outliers)