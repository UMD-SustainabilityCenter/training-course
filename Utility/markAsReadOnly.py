import os
import nbformat
from tqdm import tqdm  # Import tqdm for progress bar


def sanitize_path(input_path):
    """
    Removes single and double quotes from the input path.

    Args:
        input_path (str): The raw input path.

    Returns:
        str: Sanitized path.
    """
    return input_path.strip("'\"")


def set_markdown_cells_read_only(notebook_path):
    """
    Sets all markdown cells in a Jupyter Notebook to read-only
    by adding the 'editable': False metadata.

    Args:
        notebook_path (str): Path to the Jupyter Notebook file.
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        for cell in nb.cells:
            if cell.cell_type == "markdown":
                if 'metadata' not in cell:
                    cell.metadata = {}
                cell.metadata['editable'] = False

        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

    except Exception as e:
        print(f"Error processing {notebook_path}: {e}")


def process_notebooks_recursively(root_dir):
    """
    Recursively finds and processes all Jupyter Notebooks in a directory,
    setting markdown cells to read-only.

    Args:
        root_dir (str): Root directory to search for .ipynb files.
    """
    notebook_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".ipynb"):
                notebook_files.append(os.path.join(root, file))

    # Wrap notebook_files with tqdm for a progress bar
    for notebook_path in tqdm(notebook_files, desc="Processing notebooks"):
        set_markdown_cells_read_only(notebook_path)


def process_single_notebook(notebook_path):
    """
    Processes a single Jupyter Notebook file, setting markdown cells to read-only.

    Args:
        notebook_path (str): Path to the Jupyter Notebook file.
    """
    print(f"Processing single notebook: {notebook_path}")
    set_markdown_cells_read_only(notebook_path)


if __name__ == "__main__":
    raw_input_path = input("Enter the file or directory to process: ")
    target_path = sanitize_path(raw_input_path)  # Sanitize the input path

    if os.path.isfile(target_path) and target_path.endswith(".ipynb"):
        # If the target is a single notebook file
        process_single_notebook(target_path)
    elif os.path.isdir(target_path):
        # If the target is a directory
        process_notebooks_recursively(target_path)
    else:
        print("Invalid input. Please provide a valid .ipynb file or directory.")

    print("Finished processing.")
