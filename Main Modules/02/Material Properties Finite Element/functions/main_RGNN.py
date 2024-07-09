#%% Import Libraries
import os
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
import model_RGNN as model
from sklearn.preprocessing import StandardScaler
from torch.optim.lr_scheduler import ExponentialLR
from utils_RGNN import*
import os
import time
import copy
import datetime
import json
import torch
import collections
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os
import matplotlib.colors as mcolors
import cv2
import os
from IPython.display import clear_output
import time

#%% Read Data
wDr = os.getcwd()
# Define the folder names you want to check or create
folders_to_create = ["results", "results/images", "results/curve"]
# Iterate through the folder paths and create them if they don't exist
for folder_path in folders_to_create:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")

field_path = wDr + '/field'
test_data = load_graph(path = field_path, num_files = 1, steps = 151)

#%% BCs
E11 = 0.08; # finite strain component of Green-Lagrangian strain tensor
e11 = np.sqrt(2*E11 + 1) - 1;
steps = 151
bc_strainPBC = np.linspace(0,e11,num = steps)

#%% Save model and load model
# Saving
path = wDr + '/model'
model_name = '/model.pt'

#%% Loading Model
load_model = True

if load_model == True:
    learned_model = model.EncodeProcessDecode(
                        node_feat_size = 7,                    
                        edge_feat_size = 3,
                        output_size=4,
                        latent_size=128,
                        message_passing_steps=10,
                        window = 1)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # device = torch.device('cpu')
    model = learned_model.to(device)    
    model.load_state_dict(torch.load(path + model_name, map_location=device))

#%% Testing

# device = torch.device('cpu')
# model = model.to(device)
# Testing on different steps than training
# Steps
start_step = 1
delta_step = 20
steps = 151

# step_list = list(range(start_step,steps,delta_step))
def test_f(model, test_data, geom = 0):
    model.eval()
    
    combined_data = []  # List to store input and corresponding predictions

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # device = torch.device('cpu')
    model.to(device)  # Ensure the model is on GPU
    edge_index = test_data[geom].edge_index.to(device)
    node_features = test_data[geom].node_features.to(device)
    edge_features = test_data[geom].edge_features.to(device)
    print('Performing Predictions')
    
    for step in range(start_step, steps, delta_step):
        node_features_tmp = torch.cat([node_features, bc_strainPBC[step] * torch.ones(node_features.shape[0], 1, device=device)], dim=-1)                    
        data = Data(edge_index=edge_index - 1, x = node_features_tmp, edge_attr = edge_features)
        data = data.to(device)
        
        with torch.no_grad():  # Disable gradient computation for inference
            start_time = time.time()
            out = model(data)
            # print(f'Test-{geom}')
            print('Predicting Step', (step),'Inference', (time.time() - start_time))
        
        out_step = out.cpu().numpy()  # Convert to numpy array
        # Combine input data and prediction for saving
        input_data = node_features_tmp.cpu().numpy()
        # input_data = node_features_tmp.numpy()
        combined_step_data = np.concatenate((input_data, out_step), axis=1)
        combined_data.append(combined_step_data)

    # Convert list to NumPy array for saving
    combined_data_np = np.vstack(combined_data)

    # Save the combined data
    np.save(f'results/predictions.npy', combined_data_np)
    return combined_data_np

# Usage of the function
# Assuming 'model', 'test_data', 'start_step', 'steps', 'delta_step', 'bc_strainPBC' are defined elsewhere
os.chdir(wDr)
data = test_f(model, test_data)

# Sample data (replace with your own)
scaled_data = data
mean_array = np.array([1.5385909298670306, 9.629088339561918, 3.827083166666664, 5.2692983809523835, 434.68045121428565,  639.4987465714283, 0.0, -0.015128178126523164, 5.584694109223598, 14.810351268758422, 0.3373928084163192])  # Replace with your mean values
std_array = np.array([[1.131297798928971, 6.494407672040135, 1.9426057517469186, 1.883718056332627, 216.39271764016704,  230.52290966435916, 1.0, 0.019269810164758188, 3.9308818796619924, 13.699886193474303, 0.9500569002991748]])  # Replace with your standard deviation values

# Inverse transform
original_data = scaled_data * std_array + mean_array
coordinate = original_data[:1098, [0,1]]
param = original_data[0, [2,3,4,5]]
field1 = original_data[:,[7,8]].reshape(30,1098,2)
field2 = original_data[:,[9,10]].reshape(30,1098,2)

#### Test
updated_data_coordinate = coordinate.copy()
data_field10 = field1[:,:,0]
data_field11 = field1[:,:,1]
data_field2 = field2[:,:,0]

min_stress = np.min(data_field2)
max_stress = np.max(data_field2)

norm = plt.Normalize(vmin=min_stress, vmax=max_stress)

cmap = mcolors.LinearSegmentedColormap.from_list(
    'custom_colormap',
    ['green', 'lightgreen', 'yellow', 'orange', 'red'],
    N=256
)

for i in range(data_field2.shape[0]):
    clear_output(wait=True)
    print(f'Frame {i}')
    temp = data_field2[i,:]
    plt.figure(figsize=(4, 12))
    plt.xlim(-1,6)
    plt.ylim(-5,50)
    plt.yticks(np.arange(-5, 51, 1))
    plt.scatter(updated_data_coordinate[:, 0] + data_field10[i,:], updated_data_coordinate[:, 1] + data_field11[i,:], c = temp, cmap=cmap, norm=norm, marker='o', s=20)
    cbar = plt.colorbar()
    plt.grid()
    plt.title('run')
    plt.savefig(f'results/images/{i:03d}.jpeg')
    plt.close()
    
image_folder = 'results/images/'
images = [img for img in os.listdir(image_folder) if img.endswith(".jpeg")]
images.sort()

first_image = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = first_image.shape

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs as well
video_output = cv2.VideoWriter(f'results/video.mp4', fourcc, 4, (width, height))

# Iterate through the image files and add them to the video
for image in images:
    img_path = os.path.join(image_folder, image)
    frame = cv2.imread(img_path)
    video_output.write(frame)

# Release the VideoWriter and close the video file
video_output.release()

print("Video created successfully.")