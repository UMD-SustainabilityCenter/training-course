import os
import json
import re
from urllib.parse import quote
import glob

TOC_TAG = "auto-generated-toc"
WELCOME_PAGE_FILENAME = "welcomePage.ipynb"
WELCOME_PAGE_PATH = None  # Global variable to store the path
TOC_HEADER_REGEX = r"^##\s*Table of Contents"

def find_notebooks(base_dir="."):
    """Recursively find all Jupyter notebooks, ignoring .ipynb_checkpoints."""
    notebooks = []
    for root, _, files in os.walk(base_dir):
        if ".ipynb_checkpoints" in root:
            continue
        for file in files:
            if file.endswith(".ipynb"):
                notebooks.append(os.path.join(root, file))
    return notebooks

def load_notebook(notebook_path):
    """Load a Jupyter notebook from a file."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notebook(notebook_data, notebook_path):
    """Save a Jupyter notebook to a file."""
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook_data, f, indent=1, ensure_ascii=False)
        f.write("\n")

def generate_toc(notebook_data, notebook_path):
    """Generate ToC from markdown headings, with dynamic Home link."""
    toc_lines = []
    for cell in notebook_data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            for line in cell.get("source", []):
                # Skip the Table of Contents header line
                if re.match(TOC_HEADER_REGEX, line):
                    continue

                match = re.match(r"^(#{1,2})\s+(.*)", line)
                if match:
                    level = len(match.group(1))
                    if level > 2:
                        continue
                    title = match.group(2).strip()
                    anchor = quote(title.replace(" ", "-"))
                    indent = "  " * (level - 1)
                    toc_lines.append(f"{indent}- [{title}](#{anchor})")

    # Generate dynamic Home link
    home_link = generate_home_link(notebook_path)
    toc_lines.append(f"- [🏠 Home]({home_link})")
    return "\n".join(toc_lines)

def get_welcome_page_path():
    """Check for welcome page once, prompt if not found."""
    global WELCOME_PAGE_PATH
    if WELCOME_PAGE_PATH is not None:
        return WELCOME_PAGE_PATH

    # 1. Check if welcomePage.ipynb exists in the execution folder
    if os.path.exists(WELCOME_PAGE_FILENAME):
        WELCOME_PAGE_PATH = WELCOME_PAGE_FILENAME
        return WELCOME_PAGE_PATH

    # 2. If not, prompt the user for the path (and sanitize) - only ONCE
    while True:
        file_path = input(
            f"Could not find '{WELCOME_PAGE_FILENAME}'. Please enter the "
            f"full path to '{WELCOME_PAGE_FILENAME}': "
        )
        # Sanitize file path
        file_path = file_path.strip().replace('"', '').replace("'", "")
        if os.path.exists(file_path):
            WELCOME_PAGE_PATH = file_path
            return WELCOME_PAGE_PATH
        else:
            print("Invalid path. Please try again.")

def generate_home_link(notebook_path):
    """Dynamically generate the Home link based on notebook's location."""
    welcome_page_path = get_welcome_page_path()
    notebook_dir = os.path.dirname(os.path.abspath(notebook_path))

    # Calculate relative path from notebook to welcome page
    try:
        relative_path = os.path.relpath(welcome_page_path, notebook_dir)
    except ValueError:
        # Handle cases where paths are on different drives (Windows)
        relative_path = welcome_page_path

    return relative_path.replace("\\", "/") # Ensure forward slashes

def insert_or_update_toc(notebook_data, toc):
    """Insert ToC at the beginning or update existing ToC."""
    toc_cell = {
        "cell_type": "markdown",
        "metadata": {"tags": [TOC_TAG]},
        "source": ["## Table of Contents\n", toc],  # Added header here
    }
    for i, cell in enumerate(notebook_data['cells']):
        if TOC_TAG in cell.get('metadata', {}).get('tags', []):
            # Added header here
            notebook_data['cells'][i]['source'] = ["## Table of Contents\n", toc]
            print("ToC already exists, updating in place")
            return
    notebook_data['cells'].insert(0, toc_cell)
    print("ToC does not exist, inserting at the top")

def remove_existing_toc(notebook_data):
    """Remove existing ToC cells identified by TOC_TAG."""
    notebook_data['cells'] = [
        cell for cell in notebook_data['cells']
        if TOC_TAG not in cell.get('metadata', {}).get('tags', [])
    ]

def process_notebook(notebook_path):
    """Process a single notebook: generate/insert/update ToC."""
    try:
        notebook_data = load_notebook(notebook_path)
        toc = generate_toc(notebook_data, notebook_path)  # Pass notebook_path
        insert_or_update_toc(notebook_data, toc)
        save_notebook(notebook_data, notebook_path)
        print(f"✅ Updated ToC in: {notebook_path}")
    except Exception as e:
        print(f"❌ Error processing {notebook_path}: {e}")

def main():
    notebooks = find_notebooks()
    for notebook in notebooks:
        process_notebook(notebook)

if __name__ == "__main__":
    main()
