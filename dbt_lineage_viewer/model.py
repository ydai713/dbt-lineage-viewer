import re
from typing import Dict, Optional
from pathlib import Path
from itertools import chain


def find_dbt_project_root() -> Path:
    current_dir = Path.cwd()

    while current_dir != current_dir.parent:
        if (current_dir / "dbt_project.yml").exists():
            return current_dir
        current_dir = current_dir.parent

    raise FileNotFoundError("Please run the script inside a dbt project.")


def get_all_models(
    project_root: Path,
    model_dir_name: str,
    data_dir_name: str,
    snapshot_dir_name: str
) -> Dict[str, str]:
    """
    Returns a dictionary of all models in the project.
    The keys are the model names and the values are the model contents.
    """
    models_dir = project_root / model_dir_name
    data_dir = project_root / data_dir_name
    snapshots_dir = project_root / snapshot_dir_name

    all_models = chain(
        models_dir.rglob("*.sql"), 
        models_dir.rglob("*.py"),
        data_dir.rglob("*.csv"),
        snapshots_dir.rglob("*.sql"),
    )
    result = {}
    for model in all_models: 
        model_name = model.name.split(".")[0]
        model_content = (
            model.read_text()
            if model.suffix == ".sql" or model.suffix == ".py"
            else ""
        )
        result[model_name] = model_content
    return result


def is_downstream_model(
    parent_model_name: str,
    child_model_content: str
) -> bool:
    pattern_template = r'\s*ref\(["\']{}["\']\)\s*'
    pattern_str = pattern_template.format(parent_model_name)
    pattern = re.compile(pattern_str)
    return True if pattern.search(child_model_content) else False


def extract_model_name_and_source_type(model_content: str) -> Dict[str, str]:
    """
    Returns a dictionary of all matched model names and their source types.
    The keys are the model names and the values are the source types.
    """
    pattern = r"s*(source|ref)\s*\(\s*['\"]?(?:[\w-]+',\s*)?['\"]?(.*?)['\"]?\s*\)"
    matches = re.findall(pattern, model_content)

    if not matches:
        return {}

    models = {
        match[1]: match[0]
        for match in matches
    }

    return models


def generate_downstream_tree(
    parent_model_name: str,
    all_models: Dict[str, str],
    current_depth: int = 0,
    max_depth: int = 0
) -> Dict[str, Dict]:
    children = {}

    if max_depth != 0 and current_depth >= max_depth:
        return children

    for model_name, model_content in all_models.items():
        if is_downstream_model(parent_model_name, model_content):
            children[model_name] = generate_downstream_tree(
                model_name,
                all_models,
                current_depth=current_depth + 1,
                max_depth=max_depth
            )

    return children


def generate_upstream_tree(
    child_model_name: str,
    all_models: Dict[str, str],
    current_depth: int = 0,
    max_depth: int = 0
) -> Dict[str, Dict]:
    parents = {}

    if max_depth != 0 and current_depth >= max_depth:
        return parents

    # use regular expression to find parten model_name in all_models
    models = extract_model_name_and_source_type(all_models[child_model_name])
    for model_name, model_type in models.items():
        if model_type == "ref":
            try:
                parents[model_name] = generate_upstream_tree(
                    model_name,
                    all_models,
                    current_depth=current_depth + 1,
                    max_depth=max_depth
                )
            except KeyError:
                print(f"Warning: {model_name} is dynamically generated")
        elif model_type == "source":
            parents[model_name] = {}

    return parents


