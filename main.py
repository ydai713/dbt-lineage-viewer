"""
This script generates a mermaid chart of the dependency tree of a dbt model.

It purely uses the model files in the project directory and does not rely on
the dbt manifest.json file, which means it does not need to run `dbt compile`
first.
"""
import re
from typing import Dict, Optional
from pathlib import Path
from itertools import chain


def main():
    # model_name = "tbl_ga_sessions"
    model_name = "tbl_acquisition_funnel"
    # model_name = "tbl_kpm_email_base"
    max_depth = 3

    project_root = find_dbt_project_root()
    models_dir = project_root / "models"
    data_dir = project_root / "data"
    snapshots_dir = project_root / "snapshots"

    all_models = get_all_models(models_dir, data_dir, snapshots_dir)

    downstream_models = generate_downstream_tree(
        model_name, all_models, max_depth=max_depth
    )
    downstream_tree = { model_name: downstream_models }

    upstream_models = generate_upstream_tree(
        model_name, all_models, max_depth=max_depth
    )
    upstream_tree = { model_name: upstream_models }

    downstream_chart = generate_mermaid_code(downstream_tree, downstream=True)
    upstream_chart = generate_mermaid_code(upstream_tree, downstream=False)

    chart = f"""
        flowchart LR
        {downstream_chart}
        {upstream_chart}
    """

    print(chart)


def find_dbt_project_root() -> Path:
    current_dir = Path.cwd()

    while current_dir != current_dir.parent:
        if (current_dir / "dbt_project.yml").exists():
            return current_dir
        current_dir = current_dir.parent

    raise FileNotFoundError("Please run the script inside a dbt project.")


def get_all_models(
    models_dir: Path,
    data_dir: Path,
    snapshots_dir: Path
) -> Dict[str, str]:
    """
    Returns a dictionary of all models in the project.
    The keys are the model names and the values are the model contents.
    """
    all_models = chain(
        models_dir.rglob("*.sql"), 
        models_dir.rglob("*.py"),
        data_dir.rglob("*.csv"),
        snapshots_dir.rglob("*.sql"),
    )
    result = {}
    for model in all_models: 
        model_name = model.name.split(".")[0]
        model_content = model.read_text() if model.suffix == ".sql" else ""
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
    max_depth: Optional[int] = None
) -> Dict[str, Dict]:
    children = {}

    if max_depth is not None and current_depth >= max_depth:
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
    max_depth: Optional[int] = None
) -> Dict[str, Dict]:
    parents = {}

    if max_depth is not None and current_depth >= max_depth:
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
                pass
        elif model_type == "source":
            parents[model_name] = {}

    return parents


def generate_mermaid_code(
    d: Dict[str, Dict], 
    parent=None,
    mentioned_nodes=set(),
    visited_edges=set(),
    downstream: bool = False
) -> str:
    chart = ""
    
    if parent is None:
        mentioned_nodes = set()
        visited_edges = set()
    
    for key, value in d.items():
        if parent:
            edge = (parent, key)
            if key not in mentioned_nodes:
                mentioned_nodes.add(key)
            if edge not in visited_edges:
                visited_edges.add(edge)
                chart += (
                    f"{key} --> {parent}\n" if not downstream 
                    else f"{parent} --> {key}\n"
                )
        if value:
            chart += generate_mermaid_code(
                value, 
                key,
                mentioned_nodes,
                visited_edges, 
                downstream=downstream
            )
    
    return chart


if __name__ == "__main__":
    main()

