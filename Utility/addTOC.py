import os
import json
import re
from urllib.parse import quote

TOC_TAG = "auto-generated-toc"

def find_notebooks(base_dir="."):
    """Recursively find all Jupyter notebooks in the given directory."""
    notebooks = []
    for root, _, files in os.walk(base_dir):
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
        f.write("\n")  # Ensure there's a newline at the end

def remove_existing_toc(notebook_data):
    """Remove existing ToC cells identified by the TOC_TAG."""
    notebook_data['cells'] = [
        cell for cell in notebook_data['cells']
        if TOC_TAG not in cell.get('metadata', {}).get('tags', [])
    ]

def generate_toc(notebook_data):
    """Generate a Table of Contents from the notebook's markdown headings."""
    toc_lines = ["## Table of Contents\n"]
    for cell in notebook_data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            for line in cell.get("source", []):
                match = re.match(r"^(#{1,2})\s+(.*)", line)
                if match:
                    level = len(match.group(1))
                    if level > 2:
                        continue  # Skip deeper headings
                    title = match.group(2).strip()
                    anchor = quote(title.replace(" ", "-"))
                    indent = "  " * (level - 1)
                    toc_lines.append(f"{indent}- [{title}](#{anchor})")

    # Append Home link at the end
    toc_lines.append("- [🏠 Home](../../welcomePage.ipynb)")
    return "\n".join(toc_lines)

def insert_toc(notebook_data, toc):
    """Insert the generated ToC at the beginning of the notebook."""
    toc_cell = {
        "cell_type": "markdown",
        "metadata": {"tags": [TOC_TAG]},
        "source": [toc],
    }
    notebook_data['cells'].insert(0, toc_cell)

def process_notebook(notebook_path):
    """Process a single notebook: remove existing ToC, generate a new one, and insert it."""
    try:
        notebook_data = load_notebook(notebook_path)
        remove_existing_toc(notebook_data)
        toc = generate_toc(notebook_data)
        insert_toc(notebook_data, toc)
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
