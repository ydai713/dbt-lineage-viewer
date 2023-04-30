import re
from typing import Dict, List, Optional
from pathlib import Path


def main():
    model_name = "tbl_ga_sessions"
    max_depth = 5

    project_root = find_dbt_project_root()
    models_dir = project_root / "models"

    all_models = get_all_models(models_dir)

    downstream_models = generate_dependency_tree(
        model_name, all_models, max_depth=max_depth
    )
    dependency_tree = {
        model_name: downstream_models
    }
    mermaid_chart = dict_to_mermaid_chart(dependency_tree)
    print(mermaid_chart)


def find_dbt_project_root() -> Path:
    current_dir = Path.cwd()

    while current_dir != current_dir.parent:
        if (current_dir / "dbt_project.yml").exists():
            return current_dir
        current_dir = current_dir.parent

    raise FileNotFoundError("Please run the script inside a dbt project.")


def get_all_models(models_dir: Path) -> List[Path]:
    sql_files = list(models_dir.rglob("*.sql"))
    py_files = list(models_dir.rglob("*.py"))
    all_files = sql_files + py_files
    return all_files


def generate_re_pattern(model_name: str):
    pattern_template = r'\s*ref\(["\']{}["\']\)\s*'
    pattern_str = pattern_template.format(model_name)
    pattern = re.compile(pattern_str)
    return pattern


def generate_dependency_tree(
    parent_model_name: str,
    all_models: List[Path],
    current_depth: int = 0,
    max_depth: Optional[int] = None
) -> Dict[str, Dict]:
    dependencies = {}

    if max_depth is not None and current_depth >= max_depth:
        return dependencies

    for model in all_models:
        model_name = model.name.split(".")[0]

        pattern = generate_re_pattern(parent_model_name)

        f = open(model, "r")
        content = f.read()

        if pattern.search(content):
            dependencies[model_name] = generate_dependency_tree(
                model_name,
                all_models,
                current_depth=current_depth + 1,
                max_depth=max_depth
            )
        f.close()

    return dependencies


def dict_to_mermaid_chart(
    d: Dict[str, Dict], 
    parent=None,
    mentioned_nodes=None,
    visited_edges=None
) -> str:
    chart = ""
    
    if parent is None:
        chart += "flowchart LR\n"
        mentioned_nodes = set()
        visited_edges = set()
    
    for key, value in d.items():
        if parent:
            edge = (parent, key)
            if key not in mentioned_nodes:
                mentioned_nodes.add(key)
                chart += f"{key}[{key}]\n"
            if edge not in visited_edges:
                visited_edges.add(edge)
                chart += f"{parent} --> {key}\n"
        if value:
            chart += dict_to_mermaid_chart(value, key, mentioned_nodes, visited_edges)
    
    return chart


if __name__ == "__main__":
    main()

