import os


def print_project_structure(root_dir, exclude_dirs=None, indent=""):
    if exclude_dirs is None:
        exclude_dirs = []

    print(indent + root_dir)
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            if item not in exclude_dirs:
                print_project_structure(item_path, exclude_dirs, f"{indent}  ")
        else:
            print(f"{indent}  {item}")

if __name__ == "__main__":
    project_root = "."  # Укажите путь к корневой директории вашего проекта
    dirs_to_exclude = [".git", ".idea", "venv", "tests"]  # Укажите список директорий для исключения
    print_project_structure(project_root, exclude_dirs=dirs_to_exclude)
