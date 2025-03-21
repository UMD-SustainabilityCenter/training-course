import nbformat
import os

def update_bottom_navigation(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Load the notebook
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)
    except Exception as e:
        print(f"Error: Could not read the notebook file. {e}")
        return

    # Extract the module number from the file name
    try:
        file_name = os.path.basename(file_path)
        module_number = int(file_name.split("Module")[1].split(".")[0])
    except (IndexError, ValueError):
        print("Error: Could not determine the module number from the file name.")
        return

    # Determine the navigation links
    previous_link = (
        f"[◀︎ Module {module_number - 1}](Module{module_number - 1}.ipynb)"
        if module_number > 1
        else ""
    )
    next_link = (
        f"[Module {module_number + 1} ▶︎](Module{module_number + 1}.ipynb)"
        if module_number < 8
        else ""
    )
    home_link = "[🏠 Home](../../welcomePage.ipynb)"

    # Construct the markdown content
    navigation_content = "### <center>"
    if previous_link:
        navigation_content += previous_link + "     "
    navigation_content += home_link
    if next_link:
        navigation_content += "     " + next_link
    navigation_content += "</center>"

    # Check if a cell with the "Bottom Navigation" tag already exists
    bottom_nav_cell = None
    for cell in notebook.cells:
        if cell.cell_type == "markdown" and "Bottom Navigation" in cell.get("metadata", {}).get("tags", []):
            bottom_nav_cell = cell
            break

    # If the cell exists, update its content; otherwise, add a new cell
    if bottom_nav_cell:
        bottom_nav_cell.source = navigation_content
    else:
        new_cell = nbformat.v4.new_markdown_cell(source=navigation_content)
        new_cell.metadata["tags"] = ["Bottom Navigation"]
        notebook.cells.append(new_cell)

    # Normalize the notebook to ensure all cells have unique IDs
    try:
        nbformat.validate(notebook)  # Validate the notebook structure
    except nbformat.ValidationError as e:
        print(f"Warning: Notebook validation failed. {e}")

    # Save the updated notebook
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            nbformat.write(notebook, f)
        print(f"Successfully updated '{file_path}'.")
    except Exception as e:
        print(f"Error: Could not save the updated notebook. {e}")


if __name__ == "__main__":
    # Prompt the user for the file path
    file_path = input("Enter the path to the Jupyter Notebook file: ").strip()
    # Remove single and double quotes from the input
    file_path = file_path.strip("'\"")
    update_bottom_navigation(file_path)
