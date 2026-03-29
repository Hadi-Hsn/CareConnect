"""
CareConnect Test Results Visualization
Generates bar chart showing accuracy across different test categories
Run this in Google Colab or Jupyter Notebook
"""

import matplotlib.pyplot as plt
import numpy as np

# Test results data from the paper - 680 comprehensive test scenarios
categories = [
    "Standard\nWorkflows",
    "Appointment\nModifications",
    "Information\nRetrieval",
    "Safety\nCompliance",
    "Edge Case\nHandling",
    "Overall",
]

# Success rates and counts (out of 680 total tests)
# Percentages are mathematically exact: passed/total * 100
success_rates = [90.6, 88.5, 92.3, 96.0, 90.9, 91.8]
test_counts = [
    "145/160",
    "115/130",
    "120/130",
    "144/150",
    "100/110",
    "624/680",
]

# Create figure with higher DPI for paper quality
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

# Create bars with dark blue for categories, dark green for overall
colors = ["#1a5490" if i < 5 else "#186a3b" for i in range(len(success_rates))]

bars = ax.bar(
    categories,
    success_rates,
    color=colors,
    edgecolor="black",
    linewidth=1.5,
    alpha=0.85,
)

# Add value labels on bars
for i, (bar, rate, count) in enumerate(zip(bars, success_rates, test_counts)):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 1.5,
        f"{rate}%\n({count})",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

# Customize the plot for publication
ax.set_ylabel("Task Completion Rate (%)", fontsize=13, fontweight="bold")
ax.set_xlabel("Test Category", fontsize=13, fontweight="bold")
ax.set_title(
    "Evaluation Results Across 680 Comprehensive Test Scenarios",
    fontsize=15,
    fontweight="bold",
    pad=20,
)

# Set y-axis limits and grid
ax.set_ylim(0, 110)
ax.set_yticks(np.arange(0, 111, 10))
ax.grid(axis="y", alpha=0.3, linestyle="--", linewidth=0.8)
ax.set_axisbelow(True)

# Customize ticks
ax.tick_params(axis="both", which="major", labelsize=11)
plt.xticks(rotation=0, ha="center")

# Tight layout for better spacing
plt.tight_layout()

# Save the figure
plt.savefig(
    "Assets/test_result_accuracy.pdf", format="pdf", bbox_inches="tight", dpi=300
)
plt.savefig(
    "Assets/test_result_accuracy.png", format="png", bbox_inches="tight", dpi=300
)

# Display the plot
plt.show()

print(
    "Figure saved as 'Assets/test_result_accuracy.pdf' and 'Assets/test_result_accuracy.png'"
)
print("\nSummary Statistics:")
print(
    f"Categories with ≥95% success: {sum(1 for r in success_rates[:-1] if r >= 95)}/5"
)
print(f"Overall success rate: {success_rates[-1]:.1f}%")
print(f"Total tests passed: {test_counts[-1]}")
print(f"Highest performing: Safety Compliance ({success_rates[3]:.1f}%)")
print(f"Most challenging: Appointment Modifications ({success_rates[1]:.1f}%)")
