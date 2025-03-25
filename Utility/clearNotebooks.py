import os
import json

def clear_notebook_outputs(file_path):
    """Clear output and execution count from a Jupyter notebook."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)

        changed = False
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                if cell.get('outputs') or cell.get('execution_count') is not None:
                    cell['outputs'] = []
                    cell['execution_count'] = None
                    changed = True

        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            print(f"✔ Cleared outputs in: {file_path}")
        else:
            print(f"✓ Already clean: {file_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def clear_all_notebooks(base_dir='.'):
    """Recursively clear outputs in all .ipynb files in a directory."""
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.ipynb'):
                full_path = os.path.join(root, file)
                clear_notebook_outputs(full_path)

if __name__ == "__main__":
    clear_all_notebooks()
