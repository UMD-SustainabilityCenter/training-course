import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(filename):
    with open(filename, 'r') as file:
        data = file.read()
    lines = data.split("\n")
    data_list = []
    for line in lines:
        columns = line.split(",")
        data_list.append(columns)
    data = pd.DataFrame(data_list)
    # Find start and end index based on markers 'Y\X' and 'End'
    start_index = data[data[0] == 'Y\\X'].index[-1]
    end_index = data[data[0] == 'End'].index[-1]
    data.columns = data.iloc[start_index]
    data = data.iloc[start_index + 1:end_index].set_index(data.columns[0])
    data = data.apply(pd.to_numeric, errors='coerce')
    return np.array(data)

def correct_tilt(data, lower_bound, upper_bound):
    mask = (data >= lower_bound) & (data <= upper_bound)
    # Apply the mask to the data to filter it
    filtered_data = data[mask]
    # Determine the middle indices for the row and column
    middle_row_index = data.shape[0] // 2
    middle_col_index = data.shape[1] // 2
    # Extract the middle row and column from the data
    middle_row = data[middle_row_index, :]
    middle_col = data[:, middle_col_index]
    # Filter out NaN values from the middle row and column
    valid_x_indices = np.where(~np.isnan(middle_row) & (middle_row >= -1.5) & (middle_row <= 0))[0]
    valid_y_indices = np.where(~np.isnan(middle_col) & (middle_col >= -1.5) & (middle_col <= 0))[0]
    valid_middle_row = middle_row[valid_x_indices]
    valid_middle_col = middle_col[valid_y_indices]
    # Fit a linear model to the valid parts of the middle row and column
    if len(valid_x_indices) > 1 and len(valid_y_indices) > 1:
        slope_row, intercept_row, _, _, _ = linregress(valid_x_indices, valid_middle_row)
        slope_col, intercept_col, _, _, _ = linregress(valid_y_indices, valid_middle_col)
    else:
        slope_row, intercept_row, slope_col, intercept_col = 0, 0, 0, 0
    fitted_row = slope_row * np.arange(data.shape[1]) + intercept_row
    fitted_col = slope_col * np.arange(data.shape[0]) + intercept_col
    corrected_data = data - fitted_row
    corrected_data = (corrected_data.T - fitted_col).T
    return corrected_data

def plot(data):
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.heatmap(data, cmap='viridis', cbar=False, ax=ax)
    ax.set_aspect(aspect= 'equal')
    plt.tight_layout()
    plt.xticks([])
    plt.yticks([])
    # fig.savefig(f'{name}.png', bbox_inches='tight', pad_inches=0, dpi = 200)
    plt.show()
    plt.close()