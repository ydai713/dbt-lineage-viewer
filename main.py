import re
from typing import List
from pathlib import Path


def main():
    model_path = "/home/yang/Code/Klaviyo/company/klaviyo-bi-scripts/src/dbt/models/staging/google_analytics/intermediate/stg_ga_sessions.sql"
    model_path = Path(model_path)
    models_dir = get_models_dir(model_path)

    # Find the 'models' directory
    if not models_dir:
        print("models directory not found in the given path.")
        return

    all_models = get_all_models(models_dir)
    pattern = generate_re_pattern(model_path)

    matching_files = []
    # Print the files
    for file in all_models:
        with file.open() as f:
            content = f.read()
            if pattern.search(content):
                matching_files.append(file)


def get_models_dir(path: Path) -> Path | None:
    models_dir = None
    for part in path.parts:
        if part == "models":
            models_dir = path.parents[-path.parts.index(part)-1]
            return models_dir

def get_all_models(models_dir: Path) -> List[Path]:
    sql_files = list(models_dir.rglob("*.sql"))
    py_files = list(models_dir.rglob("*.py"))
    all_files = sql_files + py_files
    return all_files


def generate_re_pattern(model_path: Path):
    pattern_template = r'\s*ref\(["\']{}["\']\)\s*'
    model_name = model_path.name.split(".")[0]
    pattern_str = pattern_template.format(model_name)
    pattern = re.compile(pattern_str)
    return pattern


if __name__ == "__main__":
    main()
