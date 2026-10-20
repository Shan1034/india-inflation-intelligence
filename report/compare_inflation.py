
import pandas as pd
from pathlib import Path

input_file = Path("data/processed/group_inflation_july_august_2026.csv")
output_file = Path("data/processed/inflation_monthly_comparison.csv")

df = pd.read_csv(input_file)

comparison = df.pivot(
    index=["group_code", "group_name"],
    columns="month",
    values="combined_inflation"
).reset_index()

comparison["change_pp"] = (
    comparison["August-2026"] - comparison["July-2026"]
)

comparison = comparison.sort_values("change_pp", ascending=False)
comparison.to_csv(output_file, index=False)

print("Comparison dataset saved:", output_file)
print("Categories compared:", len(comparison))

print("\nTop 5 increases:")
print(comparison.head(5).to_string(index=False))

print("\nTop 5 decreases:")
print(comparison.tail(5).sort_values("change_pp").to_string(index=False))
