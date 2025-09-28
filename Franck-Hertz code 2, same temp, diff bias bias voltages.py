#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd
import glob
import re
import os
import scipy.signal

files = glob.glob(r"C:\Users\uhone\OneDrive\Documents\set 1\*.txt")
print("Files found:", files)

col_names = ['Time', 'Bias_V', 'Acc_V', 'Coll_c', 'Temp']

# Only plot for bias voltage 1.0 and temps 170, 180, 190
TARGET_TEMPS = [170, 180, 190]
TARGET_BIAS_VOLTAGES = [1.0]
SMOOTH_WINDOW = 2  # moving average window size

plt.figure(figsize=(10,7))
all_min_acc_v = []
all_dfs = []
# First pass: find the largest minimum Acc_V across all files
for i in files:
    if os.path.isdir(i):
        continue
    print(f"Reading file: {i}")
    # Extract temp and bias voltage from filename
    temp_match = re.search(r'(\d+)dC', i)
    bias_match = re.search(r'Vb=([\d.]+)V', i)
    temp_val = int(temp_match.group(1)) if temp_match else None
    bias_val = float(bias_match.group(1)) if bias_match else None
    if temp_val not in TARGET_TEMPS or bias_val not in TARGET_BIAS_VOLTAGES:
        print(f"Skipping file {i} (temp={temp_val}, bias={bias_val})")
        continue
    df = pd.read_csv(i, sep="\t", names=col_names, header=None)
    df.columns = df.columns.str.strip()
    # Convert Acc_V and Coll_c to float, handling comma decimal separator
    for col in ["Acc_V", "Coll_c"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)
    if "Acc_V" in df.columns and "Coll_c" in df.columns:
        df_sorted = df.sort_values(by="Acc_V")
        all_min_acc_v.append(df_sorted["Acc_V"].min())
        all_dfs.append((df_sorted, temp_val))

if not all_min_acc_v:
    print("No valid data to plot.")
else:
    align_start = max(all_min_acc_v)
    print(f"Aligning all curves to start at Acc_V >= {align_start}")
    for df_sorted, temp_val in all_dfs:
        df_aligned = df_sorted[df_sorted["Acc_V"] >= align_start].copy()
        x = df_aligned["Acc_V"].values
        y = df_aligned["Coll_c"].values
        # Plot raw data only, no peak/trough markings
        plt.plot(x, y, marker='o', markersize=5, linewidth=1.5, label=f"Temp {temp_val}°C")
    print("Finished reading all files. Now displaying plot...")
    plt.xlabel("Accelerating Voltage (V)")
    plt.ylabel("Collector Current (mA)")
    plt.title(f"Franck-Hertz: Collector Current vs Acc. Voltage at Bias 1V (Raw Data)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()