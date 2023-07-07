"""
This script generates a mermaid chart of the dependency tree of a dbt model.

It purely uses the model files in the project directory and does not rely on
the dbt manifest.json file, which means it does not need to run `dbt compile`
first.
"""
from .model import find_dbt_project_root
from .model import generate_downstream_tree
from .model import generate_upstream_tree
from .model import get_all_models

from .mermaid import export_diagram_to_html
from .mermaid import generate_mermaid_code

from .utils import generate_local_file_url

import click


@click.command()
@click.argument("model_name")
@click.option("--max-depth", default=0, help="Maximum depth of dependencies.")
@click.option("--output", default="test.html", help="Output file path.")
@click.option("--model-dir-name", default="models", help="Model folder name")
@click.option("--data-dir-name", default="data", help="Data folder name")
@click.option("--snapshot-dir-name", default="snapshots", help="Snapshots folder name")
@click.option("--upstream-only", is_flag=True, help="Show upstream models only.")
@click.option("--downstream-only", is_flag=True, help="Show downstream models only.")
@click.option("--mermaid-code-only", is_flag=True, help="Show mermaid code only.")
def main(
    model_name: str,
    max_depth: int,
    output: str,
    model_dir_name: str,
    data_dir_name: str,
    snapshot_dir_name,
    upstream_only: bool,
    downstream_only: bool,
    mermaid_code_only: bool,

):
    if upstream_only and downstream_only:
        print("Cannot use --upstream-only and --downstream-only together.")
        exit(1)

    try:
        project_root = find_dbt_project_root()
    except FileNotFoundError as error:
        print(error)
        exit(1)

    # Time consuming
    all_models = get_all_models(
        project_root, model_dir_name, data_dir_name, snapshot_dir_name
    )

    if not all_models.get(model_name):
        print(f"Error: Could not find model {model_name}")
        exit(1)

    # Traverse downstream models (slower with bigget max_depth)
    downstream_models = generate_downstream_tree(
        model_name, all_models, max_depth=max_depth
    ) if not upstream_only else {}
    downstream_tree = { model_name: downstream_models }

    # Traverse upstream models (fast, max_depth has little effect)
    upstream_models = generate_upstream_tree(
        model_name, all_models, max_depth=max_depth
    ) if not downstream_only else {}
    upstream_tree = { model_name: upstream_models }

    # Convert dependency tree to mermaid code
    downstream_chart = generate_mermaid_code(downstream_tree, downstream=True)
    upstream_chart = generate_mermaid_code(upstream_tree, downstream=False)

    mermaid_code = f"""
        flowchart LR
        {downstream_chart}
        {upstream_chart}
    """
    if mermaid_code_only:
        with open(output, "w") as fout:
            fout.write(mermaid_code)
        exit(0)

    # Wrap mermaid code with html and output it so can be displayed
    # in local browser
    export_diagram_to_html(output, mermaid_code)
    output = generate_local_file_url(output)
    print(output)
