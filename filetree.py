import os

def generate_html_for_directory(directory_path, exclude_dirs=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []

    file_structure_html = ''
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path) and item not in exclude_dirs:
            file_structure_html += f'<li>{item}</li>'
            file_structure_html += f'<ul>{generate_html_for_directory(item_path, exclude_dirs, exclude_files)}</ul>'
        elif os.path.isfile(item_path) and item not in exclude_files:
            file_structure_html += f'<li>{item}</li>'
    return file_structure_html


def generate_file_structure_html(directory_path, exclude_dirs=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []

    file_structure_html = f'<ul>{generate_html_for_directory(directory_path, exclude_dirs, exclude_files)}</ul>'

    with open('file_structure.html', 'w') as f:
        f.write(file_structure_html)

    return file_structure_html

directory_path = os.getcwd()
exclude_dirs = ['.history', '__pycache__', 'venv', 'my-ai']
exclude_files = []

file_structure_html = generate_file_structure_html(directory_path, exclude_dirs, exclude_files)
print(file_structure_html)
