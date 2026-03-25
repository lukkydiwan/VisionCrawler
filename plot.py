import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("25march.csv", header=None)

# Clean data
df[1] = df[1].str.replace('x', '', regex=False)
df[1] = pd.to_numeric(df[1], errors='coerce')

# Convert time
df[0] = pd.to_datetime(df[0])

# Drop invalid rows
df = df.dropna()

# Plot
plt.figure()
plt.plot(df[0], df[1])

plt.xlabel("Time")
plt.ylabel("Extracted Value")
plt.title("Extracted Data Over Time")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()