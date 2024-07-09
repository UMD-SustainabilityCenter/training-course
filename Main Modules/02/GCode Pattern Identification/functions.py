import pandas as pd
import numpy as np

def clean_numeric(value):
    # Remove any non-numeric characters except for the decimal point and minus sign
    return ''.join([char for char in value if char.isdigit() or char == '.' or char == '-'])

def parse_gcode(file_path, slicer_type='cura'):
    width = 1
    positions = {'X': None, 'Y': None, 'Z': None, 'E': None}  # Initialize E to 0
    speed = None
    changes = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('G1') or line.startswith('G0'):
                current_speed = None
                segments = line.split()

                for segment in segments:
                    if segment.startswith(('X', 'Y', 'Z', 'E')):
                        axis, value = segment[0], float(clean_numeric(segment[1:]))
                        # Reset E to 0 if negative (indicating retraction)
                        if axis == 'E' and value < 0:
                            value = 0
                        positions[axis] = value
                    elif segment.startswith('F'):
                        current_speed = float(clean_numeric(segment[1:]))
                        if speed is None or speed != current_speed:
                            speed = current_speed  # Update speed if it has changed

                changes.append((positions['X'], positions['Y'], positions['Z'], positions['E'], speed))

        changes = pd.DataFrame(changes, columns=['X', 'Y', 'Z', 'E', 'F'])
        changes = changes.dropna()

        if slicer_type == 'cura':
            changes['E'] = changes['E'].diff()
            changes['E'] = changes['E'].apply(lambda x: 0 if x <= 0 else width)  # Assuming `width` is defined somewhere
        elif slicer_type == 'prusa':
            changes['E'] = changes['E'].apply(lambda x: 0 if x <= 0 else width)  # Assuming `width` is defined somewhere

        changes = changes.reset_index(drop=True)
        changes.loc[0, 'E'] = 0

    return changes