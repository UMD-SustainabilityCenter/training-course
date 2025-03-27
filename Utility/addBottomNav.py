import nbformat
import os
import re


def update_bottom_navigation(
    file_path, module_number, min_module, max_module, exam_file_name="Exam.ipynb"
):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    previous_link = (
        f"[◀︎ Module {module_number - 1}](Module{module_number - 1}.ipynb)"
        if module_number > min_module
        else ""
    )
    next_link = (
        f"[Module {module_number + 1} ▶︎](Module{module_number + 1}.ipynb)"
        if module_number < max_module
        else ""
    )

    # Modify next link if it is the last module
    if module_number == max_module:
        next_link = f"[Exam ▶︎]({exam_file_name})"

    home_link = "[🏠 Home](../../welcomePage.ipynb)"  # Corrected home link

    navigation_content = "### <center>"
    if previous_link:
        navigation_content += previous_link + "     "
    navigation_content += home_link
    if next_link:
        navigation_content += "     " + next_link
    navigation_content += "</center>"

    # Check for existing Bottom Navigation cell
    bottom_nav_cell = None
    for cell in notebook.cells:
        tags = (
            cell.get("metadata", {}).get("tags", [])
            if cell.get("metadata", {})
            else []
        )  # Handle missing metadata

        if cell.cell_type == "markdown" and "Bottom Navigation" in tags:
            bottom_nav_cell = cell
            break

    if bottom_nav_cell:
        bottom_nav_cell.source = navigation_content
    else:
        new_cell = nbformat.v4.new_markdown_cell(source=navigation_content)
        new_cell.metadata["tags"] = ["Bottom Navigation"]
        notebook.cells.append(new_cell)

    # Remove 'id' from all cells before validation
    for cell in notebook.cells:
        if "id" in cell:
            del cell["id"]

    try:
        nbformat.validate(notebook)
    except nbformat.ValidationError as e:
        print(f"Warning: Notebook validation failed for {file_path}. {e}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)
        print(f"✅ Updated: {file_path}")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")


def update_exam_navigation(file_path, max_module):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    previous_link = f"[◀︎ Module {max_module}](Module{max_module}.ipynb)"
    home_link = "[🏠 Home](../../welcomePage.ipynb)"  # Corrected home link

    navigation_content = "### <center>"
    if previous_link:
        navigation_content += previous_link + "     "
    navigation_content += home_link
    navigation_content += "</center>"

    # Check for existing Bottom Navigation cell
    bottom_nav_cell = None
    for cell in notebook.cells:
        tags = (
            cell.get("metadata", {}).get("tags", [])
            if cell.get("metadata", {})
            else []
        )  # Handle missing metadata
        if cell.cell_type == "markdown" and "Bottom Navigation" in tags:
            bottom_nav_cell = cell
            break

    if bottom_nav_cell:
        bottom_nav_cell.source = navigation_content
    else:
        new_cell = nbformat.v4.new_markdown_cell(source=navigation_content)
        new_cell.metadata["tags"] = ["Bottom Navigation"]
        notebook.cells.append(new_cell)

    # Remove 'id' from all cells before validation
    for cell in notebook.cells:
        if "id" in cell:
            del cell["id"]

    try:
        nbformat.validate(notebook)
    except nbformat.ValidationError as e:
        print(f"Warning: Notebook validation failed for {file_path}. {e}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)
        print(f"✅ Updated: {file_path}")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")


def main():
    current_dir = os.getcwd()
    module_files = []
    module_numbers = []
    exam_file = "Exam.ipynb"  # Define exam file name

    # Identify valid module notebooks
    for file_name in os.listdir(current_dir):
        match = re.match(r"Module(\d+)\.ipynb$", file_name)
        if match:
            module_num = int(match.group(1))
            module_files.append((module_num, file_name))
            module_numbers.append(module_num)

    if not module_files:
        print("No Module*.ipynb files found.")
        return

    min_module = min(module_numbers)
    max_module = max(module_numbers)

    for module_num, file_name in sorted(module_files):
        update_bottom_navigation(
            os.path.join(current_dir, file_name),
            module_num,
            min_module,
            max_module,
            exam_file,
        )

    # Update exam navigation after updating all modules
    if os.path.exists(os.path.join(current_dir, exam_file)):
        update_exam_navigation(os.path.join(current_dir, exam_file), max_module)
    else:
        print(f"Exam file '{exam_file}' not found.")


if __name__ == "__main__":
    main()
