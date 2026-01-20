import pandas as pd

df = pd.read_csv("C:\\Users\\Lalit Hire\\UIDAI Data Hackathon 2026\\data\\UIDAI_with_population.csv")
print(df['PIN_Code'].nunique())