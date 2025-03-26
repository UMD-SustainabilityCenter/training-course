import re
import nbformat
import os

def remove_trailing_colons(notebook_path):
    """
    Removes trailing colons from level 1 and level 2 headings in Markdown cells
    of a Jupyter Notebook.

    Args:
        notebook_path (str): The path to the Jupyter Notebook file (.ipynb).
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
    except FileNotFoundError:
        print(f"Error: File not found at path: {notebook_path}")
        return
    except Exception as e:
        print(f"Error: Could not read notebook. {e}")
        return

    replacements_made = False
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            # Define a function to replace trailing colons in a heading
            def replace_heading(match):
                nonlocal replacements_made
                heading = match.group(0)
                new_heading = re.sub(r':+\s*$', '', heading)
                if heading != new_heading:
                    print(f"    {heading} → {new_heading}")
                    replacements_made = True
                    return new_heading
                return heading

            # Use re.sub with a function to replace headings
            cell.source = re.sub(r'^(#+.*?):+\s*$', replace_heading, cell.source, flags=re.MULTILINE)

    if not replacements_made:
        print("    No text replacements done.")

    try:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print(f"  Successfully processed and updated: {notebook_path}")
    except Exception as e:
        print(f"Error: Could not write notebook. {e}")

def process_notebooks(path):
    """
    Processes either a single notebook file or all .ipynb files in a directory recursively,
    ignoring files in '.ipynb_checkpoints' directories.

    Args:
        path (str): The path to either a single notebook file or a directory.
    """
    if os.path.isfile(path) and path.endswith('.ipynb'):
        print(f"Scanning file: {path}")
        remove_trailing_colons(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            # Skip .ipynb_checkpoints directories
            if '.ipynb_checkpoints' in root:
                continue
            for file in files:
                if file.endswith('.ipynb'):
                    file_path = os.path.join(root, file)
                    print(f"Scanning file: {file_path}")
                    remove_trailing_colons(file_path)
    else:
        print("Error: Invalid path. Please provide a valid .ipynb file or directory.")

if __name__ == "__main__":
    input_path = input("Enter the path to the Jupyter Notebook file or directory: ")
    # Sanitize the input by removing single and double quotes
    input_path = input_path.replace('"', '').replace("'", '')
    process_notebooks(input_path)
