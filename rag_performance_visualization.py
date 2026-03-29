"""
RAG Performance Visualization - Hospital Document Retrieval
Shows retrieval accuracy as a function of top-k parameter
"""

import matplotlib.pyplot as plt
import numpy as np

# Top-k values from 1 to 10
k_values = np.arange(1, 11)

# Retrieval accuracy (%) for different k values
# Peaks at k=5 (92.8%), then slightly decreases due to noise from irrelevant documents
retrieval_accuracy = [78.4, 83.6, 87.9, 90.5, 92.8, 92.4, 92.0, 91.7, 91.5, 91.3]

# Create figure with higher DPI for paper quality
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

# Plot line with markers
ax.plot(
    k_values,
    retrieval_accuracy,
    color="#1a5490",
    linewidth=2.5,
    marker="o",
    markersize=7,
    markerfacecolor="#1a5490",
    markeredgecolor="white",
    markeredgewidth=1.2,
)

# Add value labels on points
for k, acc in zip(k_values, retrieval_accuracy):
    ax.text(
        k, acc + 0.8, f"{acc}%", ha="center", va="bottom", fontsize=8.5, color="#2c3e50"
    )

# Customize the plot
ax.set_xlabel("Top-k Documents Retrieved", fontsize=12, fontweight="bold")
ax.set_ylabel("Retrieval Accuracy (%)", fontsize=12, fontweight="bold")
ax.set_title(
    "RAG Document Retrieval Performance",
    fontsize=13,
    fontweight="bold",
    pad=12,
)

# Set axis properties
ax.set_xticks(k_values)
ax.set_ylim(75, 100)
ax.set_xlim(0.5, 10.5)
ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7, color="#cccccc")
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Customize ticks
ax.tick_params(axis="both", which="major", labelsize=11)

# Tight layout
plt.tight_layout()

# Save the figure
plt.savefig("Assets/rag_performance.pdf", format="pdf", bbox_inches="tight", dpi=300)
plt.savefig("Assets/rag_performance.png", format="png", bbox_inches="tight", dpi=300)

# Display the plot
plt.show()

print("Figure saved as 'Assets/rag_performance.pdf' and 'Assets/rag_performance.png'")
print("\nRAG Performance Summary:")
print(f"Optimal k value: 5")
print(f"Maximum accuracy: 92.8%")
print(f"Accuracy at k=1: {retrieval_accuracy[0]}%")
print(f"Accuracy at k=10: {retrieval_accuracy[-1]}%")
print(f"Performance gain (k=5 vs k=1): {92.8 - retrieval_accuracy[0]:.1f}%")
