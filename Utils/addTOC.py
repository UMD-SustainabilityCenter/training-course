import json
import os
import re
from urllib.parse import quote

def create_table_of_contents(notebook_path, level_1_treatment):
    """
    Generates and injects a table of contents into a Jupyter Notebook.

    Args:
        notebook_path (str): The path to the Jupyter Notebook file.
        level_1_treatment (str): How to treat Level 1 headings ('part of the list' or 'independent lines').
    """
    # Remove quotes from notebook path
    notebook_path = notebook_path.strip('"').strip("'")

    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at path: {notebook_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {notebook_path}")
        return

    toc = generate_toc(notebook_data, level_1_treatment)
    inject_toc(notebook_data, toc)

    try:
        with open(notebook_path, "w", encoding="utf-8") as f:
            json.dump(notebook_data, f, indent=1, ensure_ascii=False)
            f.write("\n")  # Add a newline at the end of the file
        print(f"Table of Contents updated in: {notebook_path}")
    except IOError as e:
        print(f"Error writing to file: {notebook_path}. {e}")


def generate_toc(notebook_data, level_1_treatment):
    """
    Generates the table of contents as a Markdown string.

    Args:
        notebook_data (dict): The parsed Jupyter Notebook data.
        level_1_treatment (str): How to treat Level 1 headings ('part of the list' or 'independent lines').

    Returns:
        str: The Markdown string representing the table of contents.
    """
    toc_lines = ["## Table of Contents"]  # Added title
    for cell in notebook_data["cells"]:
        if cell["cell_type"] == "markdown":
            for line in cell["source"]:
                # Skip the "Table of Contents" header itself
                if re.match(r"^## Table of Contents$", line.strip()):
                    continue

                # Match level 1 headings
                match = re.match(r"^(#) (.*)$", line)  # Level 1
                if match:
                    heading_text = match.group(2).strip()
                    # Create a URL-friendly anchor link (preserve case)
                    anchor = heading_text.replace(" ", "-")
                    anchor = quote(anchor)  # URL encode for safety
                    if level_1_treatment == "part of the list":
                        toc_lines.append(f"- [{heading_text}](#{anchor})")  # First-level bullet
                    elif level_1_treatment == "independent lines":
                        toc_lines.append(f"[{heading_text}](#{anchor})")  # Independent line
                    continue  # Skip to the next line

                # Match level 2 headings
                match = re.match(r"^(##) (.*)$", line)  # Level 2
                if match:
                    heading_text = match.group(2).strip()
                    # Create a URL-friendly anchor link (preserve case)
                    anchor = heading_text.replace(" ", "-")
                    anchor = quote(anchor)  # URL encode for safety
                    indent = "  "  # Indent of two spaces for Level 2
                    toc_lines.append(f"{indent}- [{heading_text}](#{anchor})")  # Second-level bullet
                    continue

    # Add the home link
    if level_1_treatment == "part of the list":
        toc_lines.append("- [🏠 Home](welcomePage.ipynb)")  # Home link as a first-level bullet
    elif level_1_treatment == "independent lines":
        toc_lines.append("")  # Add a blank line above the home link
        toc_lines.append("[🏠 Home](welcomePage.ipynb)")  # Home link as an independent line

    return "\n".join(toc_lines)  # Join with newlines to ensure proper formatting


def inject_toc(notebook_data, toc):
    """
    Injects the table of contents into the notebook data.  It either replaces an
    existing TOC cell (if one exists with the 'Table of Contents' tag) or
    inserts a new TOC cell at the beginning of the notebook.

    Args:
        notebook_data (dict): The parsed Jupyter Notebook data.
        toc (str): The Markdown string representing the table of contents.
    """
    toc_cell_exists = False
    for i, cell in enumerate(notebook_data["cells"]):
        if cell["cell_type"] == "markdown" and "tags" in cell["metadata"] and \
           "Table of Contents" in cell["metadata"]["tags"]:
            # Replace existing TOC cell
            notebook_data["cells"][i]["source"] = [toc]
            toc_cell_exists = True
            break

    if not toc_cell_exists:
        # Insert new TOC cell at the beginning
        toc_cell = {
            "cell_type": "markdown",
            "metadata": {"tags": ["Table of Contents"]},
            "source": [toc],
        }
        notebook_data["cells"].insert(0, toc_cell)


if __name__ == "__main__":
    notebook_file = input("Enter the path to the Jupyter Notebook file: ")
    print("How do you want to treat Level 1 (#) headings?")
    print("1. Part of the list")
    print("2. Independent lines")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        level_1_treatment = "part of the list"
    elif choice == "2":
        level_1_treatment = "independent lines"
    else:
        print("Invalid choice. Defaulting to 'part of the list'.")
        level_1_treatment = "part of the list"

    create_table_of_contents(notebook_file, level_1_treatment)
