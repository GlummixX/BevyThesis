import matplotlib.pyplot as plt

# Example data
data = {
    'x': [10, 2, 6, 3, 9, 6],   # [max, min, median, 5%, 95%, mean]
    'y': [12, 4, 8, 5, 11, 8],
    'z': [8, 1, 5, 2, 7, 5],
    'a': [15, 5, 10, 6, 14, 10]
}

labels = list(data.keys())
positions = range(len(labels))

fig, ax = plt.subplots()

for i, key in enumerate(labels):
    maximum, minimum, median, p5, p95, mean = data[key]

    # Draw box between 5th and 95th percentile
    ax.add_patch(plt.Rectangle((i - 0.2, p5), 0.4, p95 - p5, edgecolor='black', facecolor='lightblue'))

    # Draw median line
    ax.plot([i - 0.2, i + 0.2], [median, median], color='red', linewidth=2)

    # Draw min/max as whiskers
    ax.plot([i, i], [minimum, p5], color='black', linestyle='--')
    ax.plot([i, i], [p95, maximum], color='black', linestyle='--')

    # Draw caps
    ax.plot([i - 0.1, i + 0.1], [minimum, minimum], color='black')
    ax.plot([i - 0.1, i + 0.1], [maximum, maximum], color='black')

    # Optional: mark the mean
    ax.plot(i, mean, marker='o', color='green', label='Mean' if i == 0 else "")

ax.set_xticks(positions)
ax.set_xticklabels(labels)
ax.set_ylabel('Values')
ax.set_title('Custom Boxplot from Summary Statistics')
ax.legend()
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
